import fs from "fs";
import fsPromises from "fs/promises";
import path from "path";
import { NextResponse } from "next/server";
import { getDb } from "@/lib/db";
import { buildFollowUpEmailBody } from "@/lib/follow-up-email";
import { uniquePetitionId } from "@/lib/petition-id";
import { petitionUploadDir } from "@/lib/paths";
import {
  buildDiscrepancyNoteForForward,
  confidenceFromComparison,
} from "@/lib/ai-confidence";
import type { ComparisonPayload } from "@/lib/claude-comparison";
import {
  mergePdfBuffers,
  validateFile,
  type FileValidation,
} from "@/lib/validate-documents";

export const runtime = "nodejs";

export async function GET() {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT id, student_name, student_email, uw_course, status,
              instructor_name, instructor_email, notes, created_at
       FROM petitions ORDER BY datetime(created_at) DESC`,
    )
    .all() as Array<{
      id: string;
      student_name: string | null;
      student_email: string | null;
      uw_course: string | null;
      status: string | null;
      instructor_name: string | null;
      instructor_email: string | null;
      notes: string | null;
      created_at: string | null;
    }>;

  const petitions = rows.map((r) => {
    const combinedPath = path.join(petitionUploadDir(r.id), "combined.pdf");
    const hasCombinedPdf = fs.existsSync(combinedPath);
    const comp = db
      .prepare(
        `SELECT comparison_json, summary, course_level_concern, pedagogy_mismatch
         FROM ai_comparisons WHERE petition_id = ?`,
      )
      .get(r.id) as
      | {
          comparison_json: string;
          summary: string | null;
          course_level_concern: number;
          pedagogy_mismatch: number;
        }
      | undefined;

    const hasAiComparison = Boolean(comp);
    let aiConfidence: "green" | "yellow" | "red" | null = null;
    let aiSummary: string | null = null;
    let aiForwardContext: string | null = null;

    if (comp) {
      aiSummary = comp.summary;
      const courseLvl = Boolean(comp.course_level_concern);
      const ped = Boolean(comp.pedagogy_mismatch);
      try {
        const payload = JSON.parse(comp.comparison_json) as ComparisonPayload;
        aiConfidence = confidenceFromComparison(payload, courseLvl, ped);
        aiForwardContext = buildDiscrepancyNoteForForward(payload, courseLvl, ped);
      } catch {
        aiConfidence = "yellow";
        aiForwardContext =
          "Comparison data could not be parsed; please open the comparison view in the tool.";
      }
    }

    return {
      ...r,
      hasCombinedPdf,
      hasAiComparison,
      aiConfidence,
      aiSummary,
      aiForwardContext,
    };
  });

  return NextResponse.json({ petitions });
}

export async function POST(request: Request) {
  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return NextResponse.json({ error: "Invalid form data" }, { status: 400 });
  }

  const studentName = String(formData.get("student_name") ?? "").trim();
  const studentEmail = String(formData.get("student_email") ?? "").trim();
  const uwCourse = String(formData.get("uw_course") ?? "").trim();

  if (!studentName || !studentEmail || !uwCourse) {
    return NextResponse.json(
      { error: "student_name, student_email, and uw_course are required" },
      { status: 400 },
    );
  }

  const entries = formData.getAll("files");
  const files = entries.filter((e): e is File => e instanceof File);
  if (files.length === 0) {
    return NextResponse.json({ error: "At least one file is required" }, { status: 400 });
  }

  const db = getDb();
  const petitionId = uniquePetitionId(db);
  const dir = petitionUploadDir(petitionId);
  await fsPromises.mkdir(dir, { recursive: true });

  const validations: FileValidation[] = [];
  const mergeBuffers: Uint8Array[] = [];

  for (const file of files) {
    const originalName = file.name || "upload";
    let buffer: Buffer;
    try {
      buffer = Buffer.from(await file.arrayBuffer());
    } catch {
      validations.push({
        originalName,
        savedRelativePath: "",
        passed: false,
        issues: ["Corrupt file"],
        mergePdfBytes: null,
      });
      continue;
    }

    const safe = originalName.replace(/[^a-zA-Z0-9._-]+/g, "_");
    const diskName = `${Date.now()}-${safe}`;
    const absolutePath = path.join(dir, diskName);
    try {
      await fsPromises.writeFile(absolutePath, buffer);
    } catch {
      validations.push({
        originalName,
        savedRelativePath: path.relative(process.cwd(), absolutePath),
        passed: false,
        issues: ["Corrupt file"],
        mergePdfBytes: null,
      });
      continue;
    }

    const savedRelativePath = path.relative(process.cwd(), absolutePath);
    const v = await validateFile({
      originalName,
      buffer,
      savedRelativePath,
    });
    validations.push(v);
    if (v.mergePdfBytes) {
      mergeBuffers.push(v.mergePdfBytes);
    }
  }

  let combinedRelative: string | null = null;
  const merged = await mergePdfBuffers(mergeBuffers);
  if (merged && merged.byteLength > 0) {
    const combinedPath = path.join(dir, "combined.pdf");
    await fsPromises.writeFile(combinedPath, merged);
    combinedRelative = path.relative(process.cwd(), combinedPath);
  }

  db.prepare(
    `INSERT INTO petitions (
      id, student_name, student_email, uw_course, status,
      instructor_name, instructor_email, notes
    ) VALUES (
      @id, @student_name, @student_email, @uw_course, @status,
      @instructor_name, @instructor_email, @notes
    )`,
  ).run({
    id: petitionId,
    student_name: studentName,
    student_email: studentEmail,
    uw_course: uwCourse,
    status: "pending",
    instructor_name: null,
    instructor_email: null,
    notes: null,
  });

  const anyFailed = validations.some((v) => !v.passed);
  const followUpEmail = anyFailed
    ? buildFollowUpEmailBody({
        studentName,
        studentEmail,
        uwCourse,
        validations,
      })
    : undefined;

  return NextResponse.json({
    petitionId,
    combinedPdfPath: combinedRelative,
    combinedPdfUrl: combinedRelative
      ? `/api/petitions/${encodeURIComponent(petitionId)}/combined`
      : null,
    files: validations.map((v) => ({
      name: v.originalName,
      passed: v.passed,
      issues: v.issues,
      savedPath: v.savedRelativePath,
    })),
    followUpEmail,
    banner: anyFailed
      ? "Some documents have issues — you may want to follow up with the student"
      : undefined,
  });
}
