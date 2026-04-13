import fs from "fs";
import path from "path";
import { NextResponse } from "next/server";
import {
  compareSyllabi,
  compareSyllabusExtracts,
  extractExternalSyllabus,
  type ComparisonPayload,
  type ExternalExtract,
} from "@/lib/claude-comparison";
import { getDb, type UwCourseRow } from "@/lib/db";
import {
  extractTextFromLocalFile,
  extractTextFromPetitionUploads,
} from "@/lib/extract-petition-text";
import { petitionUploadDir } from "@/lib/paths";
import { lookupUwCourse } from "@/lib/uw-lookup";

export const runtime = "nodejs";

type SavedComparison = {
  externalExtract: ExternalExtract;
  referenceExtract: ExternalExtract | null;
  comparison: ComparisonPayload;
  summary: string | null;
  course_level_concern: boolean;
  pedagogy_mismatch: boolean;
  created_at: string | null;
};

function buildBundle(args: {
  petition: Record<string, unknown>;
  uwCourse: UwCourseRow | undefined;
  saved: SavedComparison | null;
  hasExtractableText: boolean;
  hasCombinedPdf: boolean;
  usesUwSyllabusFile: boolean;
}) {
  return {
    petition: args.petition,
    uwCourse: args.uwCourse ?? null,
    savedComparison: args.saved,
    hasExtractableText: args.hasExtractableText,
    hasCombinedPdf: args.hasCombinedPdf,
    usesUwSyllabusFile: args.usesUwSyllabusFile,
  };
}

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const db = getDb();
  const petition = db
    .prepare(
      `SELECT id, student_name, student_email, uw_course, status,
              instructor_name, instructor_email, notes, created_at
       FROM petitions WHERE id = ?`,
    )
    .get(id) as Record<string, unknown> | undefined;
  if (!petition) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const uwCourse = lookupUwCourse(db, petition.uw_course as string | null);
  const row = db
    .prepare(`SELECT * FROM ai_comparisons WHERE petition_id = ?`)
    .get(id) as
    | {
        external_extract: string;
        reference_extract: string | null;
        comparison_json: string;
        summary: string | null;
        course_level_concern: number;
        pedagogy_mismatch: number;
        created_at: string | null;
      }
    | undefined;

  let saved: SavedComparison | null = null;
  if (row) {
    let referenceExtract: ExternalExtract | null = null;
    if (row.reference_extract) {
      try {
        referenceExtract = JSON.parse(row.reference_extract) as ExternalExtract;
      } catch {
        referenceExtract = null;
      }
    }
    saved = {
      externalExtract: JSON.parse(row.external_extract) as ExternalExtract,
      referenceExtract,
      comparison: JSON.parse(row.comparison_json) as ComparisonPayload,
      summary: row.summary,
      course_level_concern: Boolean(row.course_level_concern),
      pedagogy_mismatch: Boolean(row.pedagogy_mismatch),
      created_at: row.created_at,
    };
  }

  const rawText = await extractTextFromPetitionUploads(id);
  const hasExtractableText = rawText.trim().length > 0;
  const hasCombinedPdf = fs.existsSync(
    path.join(petitionUploadDir(id), "combined.pdf"),
  );

  const usesUwSyllabusFile = Boolean(uwCourse?.syllabus_relpath);

  return NextResponse.json(
    buildBundle({
      petition,
      uwCourse,
      saved,
      hasExtractableText,
      hasCombinedPdf,
      usesUwSyllabusFile,
    }),
  );
}

export async function POST(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const db = getDb();
  const petition = db
    .prepare(
      `SELECT id, student_name, student_email, uw_course, status,
              instructor_name, instructor_email, notes, created_at
       FROM petitions WHERE id = ?`,
    )
    .get(id) as { id: string; uw_course: string | null } | undefined;
  if (!petition) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const uwCourse = lookupUwCourse(db, petition.uw_course);
  if (!uwCourse) {
    return NextResponse.json(
      {
        error:
          "No UW course in the catalog matches this petition’s UW course field. Add or fix the course code under Courses.",
      },
      { status: 400 },
    );
  }

  const rawText = await extractTextFromPetitionUploads(id);
  if (!rawText.trim()) {
    return NextResponse.json(
      {
        error:
          "No extractable text found (upload PDFs or DOCX with text — images alone won’t work for AI comparison).",
      },
      { status: 400 },
    );
  }

  try {
    const external = await extractExternalSyllabus(rawText);
    let comparison: ComparisonPayload;
    let referenceExtract: ExternalExtract | null = null;

    if (uwCourse.syllabus_relpath) {
      const uwAbs = path.join(process.cwd(), uwCourse.syllabus_relpath);
      const uwRaw = await extractTextFromLocalFile(uwAbs);
      if (!uwRaw.trim()) {
        return NextResponse.json(
          {
            error:
              "The UW class syllabus on file has no extractable text. Upload a text-based PDF or DOCX on the Courses tab.",
          },
          { status: 400 },
        );
      }
      referenceExtract = await extractExternalSyllabus(uwRaw);
      comparison = await compareSyllabusExtracts({
        student: external,
        reference: referenceExtract,
        uw: uwCourse,
      });
    } else {
      comparison = await compareSyllabi({ external, uw: uwCourse });
    }

    db.prepare(
      `INSERT INTO ai_comparisons (
        petition_id, uw_course_id, external_extract, reference_extract, comparison_json, summary,
        course_level_concern, pedagogy_mismatch
      ) VALUES (
        @petition_id, @uw_course_id, @external_extract, @reference_extract, @comparison_json, @summary,
        @course_level_concern, @pedagogy_mismatch
      )
      ON CONFLICT(petition_id) DO UPDATE SET
        uw_course_id = excluded.uw_course_id,
        external_extract = excluded.external_extract,
        reference_extract = excluded.reference_extract,
        comparison_json = excluded.comparison_json,
        summary = excluded.summary,
        course_level_concern = excluded.course_level_concern,
        pedagogy_mismatch = excluded.pedagogy_mismatch`,
    ).run({
      petition_id: id,
      uw_course_id: uwCourse.id,
      external_extract: JSON.stringify(external),
      reference_extract: referenceExtract ? JSON.stringify(referenceExtract) : null,
      comparison_json: JSON.stringify(comparison),
      summary: comparison.summary,
      course_level_concern: comparison.course_level_concern ? 1 : 0,
      pedagogy_mismatch: comparison.pedagogy_mismatch ? 1 : 0,
    });

    const row = db
      .prepare(`SELECT * FROM ai_comparisons WHERE petition_id = ?`)
      .get(id) as {
        external_extract: string;
        reference_extract: string | null;
        comparison_json: string;
        summary: string | null;
        course_level_concern: number;
        pedagogy_mismatch: number;
        created_at: string | null;
      };

    let refParsed: ExternalExtract | null = null;
    if (row.reference_extract) {
      try {
        refParsed = JSON.parse(row.reference_extract) as ExternalExtract;
      } catch {
        refParsed = null;
      }
    }

    const saved: SavedComparison = {
      externalExtract: JSON.parse(row.external_extract) as ExternalExtract,
      referenceExtract: refParsed,
      comparison: JSON.parse(row.comparison_json) as ComparisonPayload,
      summary: row.summary,
      course_level_concern: Boolean(row.course_level_concern),
      pedagogy_mismatch: Boolean(row.pedagogy_mismatch),
      created_at: row.created_at,
    };

    const fullPetition = db
      .prepare(
        `SELECT id, student_name, student_email, uw_course, status,
                instructor_name, instructor_email, notes, created_at
         FROM petitions WHERE id = ?`,
      )
      .get(id) as Record<string, unknown>;

    const hasCombinedPdf = fs.existsSync(
      path.join(petitionUploadDir(id), "combined.pdf"),
    );

    return NextResponse.json(
      buildBundle({
        petition: fullPetition,
        uwCourse,
        saved,
        hasExtractableText: true,
        hasCombinedPdf,
        usesUwSyllabusFile: Boolean(uwCourse.syllabus_relpath),
      }),
    );
  } catch (e) {
    const message = e instanceof Error ? e.message : "Comparison failed";
    const status = message.includes("ANTHROPIC_API_KEY") ? 503 : 500;
    return NextResponse.json({ error: message }, { status });
  }
}
