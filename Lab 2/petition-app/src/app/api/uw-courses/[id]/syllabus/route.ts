import fs from "fs";
import fsPromises from "fs/promises";
import path from "path";
import { NextResponse } from "next/server";
import { extractCatalogFieldsFromSyllabusText } from "@/lib/claude-comparison";
import { getDb } from "@/lib/db";
import { extractTextFromLocalFile } from "@/lib/extract-petition-text";
import { uwCourseUploadDir } from "@/lib/paths";

export const runtime = "nodejs";

const MAX_BYTES = 25 * 1024 * 1024;

function allowedExt(filename: string) {
  const lower = filename.toLowerCase();
  if (lower.endsWith(".pdf")) return ".pdf";
  if (lower.endsWith(".docx")) return ".docx";
  return null;
}

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const numericId = Number(id);
  if (!Number.isFinite(numericId)) {
    return NextResponse.json({ error: "Invalid id" }, { status: 400 });
  }
  const db = getDb();
  const row = db
    .prepare(`SELECT id, course_code, syllabus_relpath FROM uw_courses WHERE id = ?`)
    .get(numericId) as
    | { id: number; course_code: string; syllabus_relpath: string | null }
    | undefined;
  if (!row?.syllabus_relpath) {
    return NextResponse.json({ error: "No syllabus on file" }, { status: 404 });
  }
  const abs = path.join(process.cwd(), row.syllabus_relpath);
  if (!fs.existsSync(abs)) {
    return NextResponse.json({ error: "File missing on disk" }, { status: 404 });
  }
  const buf = fs.readFileSync(abs);
  const ext = path.extname(abs).toLowerCase();
  const mime = ext === ".pdf" ? "application/pdf" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
  const safeCode = row.course_code.replace(/[^\w.-]+/g, "_");
  return new NextResponse(new Uint8Array(buf), {
    headers: {
      "Content-Type": mime,
      "Content-Disposition": `attachment; filename="${safeCode}-syllabus${ext}"`,
    },
  });
}

export async function POST(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const numericId = Number(id);
  if (!Number.isFinite(numericId)) {
    return NextResponse.json({ error: "Invalid id" }, { status: 400 });
  }

  const db = getDb();
  const exists = db.prepare(`SELECT id, syllabus_relpath FROM uw_courses WHERE id = ?`).get(numericId) as
    | { id: number; syllabus_relpath: string | null }
    | undefined;
  if (!exists) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return NextResponse.json({ error: "Invalid form data" }, { status: 400 });
  }

  const file = formData.get("file");
  if (!(file instanceof File)) {
    return NextResponse.json({ error: "file is required" }, { status: 400 });
  }

  const ext = allowedExt(file.name || "");
  if (!ext) {
    return NextResponse.json(
      { error: "Only .pdf and .docx syllabi are supported" },
      { status: 400 },
    );
  }

  let buffer: Buffer;
  try {
    buffer = Buffer.from(await file.arrayBuffer());
  } catch {
    return NextResponse.json({ error: "Could not read upload" }, { status: 400 });
  }
  if (buffer.byteLength > MAX_BYTES) {
    return NextResponse.json({ error: "File too large (max 25 MB)" }, { status: 400 });
  }

  if (exists.syllabus_relpath) {
    const prev = path.join(process.cwd(), exists.syllabus_relpath);
    try {
      if (fs.existsSync(prev)) await fsPromises.unlink(prev);
    } catch {
      /* ignore */
    }
  }

  const dir = uwCourseUploadDir(numericId);
  await fsPromises.mkdir(dir, { recursive: true });
  const diskName = `syllabus${ext}`;
  const abs = path.join(dir, diskName);
  await fsPromises.writeFile(abs, buffer);
  const relpath = path.relative(process.cwd(), abs);

  db.prepare(`UPDATE uw_courses SET syllabus_relpath = ? WHERE id = ?`).run(relpath, numericId);

  type CatalogExtraction = {
    filled: boolean;
    learningOutcomeCount?: number;
    topicCount?: number;
    warning?: string;
  };

  let catalogExtraction: CatalogExtraction = { filled: false };

  try {
    const rawText = await extractTextFromLocalFile(abs);
    if (!rawText.trim()) {
      catalogExtraction = {
        filled: false,
        warning:
          "Syllabus saved, but no text could be extracted. Use a text-based PDF or DOCX, or enter learning outcomes manually.",
      };
    } else {
      const extracted = await extractCatalogFieldsFromSyllabusText(rawText);
      const los = extracted.learning_outcomes.map((s) => String(s).trim()).filter(Boolean);
      const topics = extracted.topics_covered.map((s) => String(s).trim()).filter(Boolean);

      if (los.length === 0 && topics.length === 0) {
        catalogExtraction = {
          filled: false,
          warning:
            "Syllabus saved, but no learning outcomes or topics were detected. Try editing the course manually or upload a clearer syllabus.",
        };
      } else {
        db.prepare(
          `UPDATE uw_courses SET learning_outcomes = @los, topics = @topics WHERE id = @id`,
        ).run({
          los: JSON.stringify(los),
          topics: JSON.stringify(topics),
          id: numericId,
        });
        catalogExtraction = {
          filled: true,
          learningOutcomeCount: los.length,
          topicCount: topics.length,
        };
      }
    }
  } catch (e) {
    const message = e instanceof Error ? e.message : "Extraction failed";
    catalogExtraction = {
      filled: false,
      warning: message.includes("ANTHROPIC_API_KEY")
        ? "Syllabus saved. Set ANTHROPIC_API_KEY to auto-fill learning outcomes from the file."
        : `Syllabus saved, but auto-fill failed (${message}). You can edit learning outcomes manually.`,
    };
  }

  const course = db.prepare(`SELECT * FROM uw_courses WHERE id = ?`).get(numericId);
  return NextResponse.json({
    course,
    downloadUrl: `/api/uw-courses/${numericId}/syllabus`,
    catalogExtraction,
  });
}

export async function DELETE(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const numericId = Number(id);
  if (!Number.isFinite(numericId)) {
    return NextResponse.json({ error: "Invalid id" }, { status: 400 });
  }

  const db = getDb();
  const row = db
    .prepare(`SELECT id, syllabus_relpath FROM uw_courses WHERE id = ?`)
    .get(numericId) as { id: number; syllabus_relpath: string | null } | undefined;
  if (!row) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  if (row.syllabus_relpath) {
    const abs = path.join(process.cwd(), row.syllabus_relpath);
    try {
      if (fs.existsSync(abs)) await fsPromises.unlink(abs);
    } catch {
      /* ignore */
    }
  }
  db.prepare(`UPDATE uw_courses SET syllabus_relpath = NULL WHERE id = ?`).run(numericId);
  const course = db.prepare(`SELECT * FROM uw_courses WHERE id = ?`).get(numericId);
  return NextResponse.json({ course });
}
