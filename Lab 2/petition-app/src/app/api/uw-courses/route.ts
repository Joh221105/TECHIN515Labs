import { NextResponse } from "next/server";
import { getDb } from "@/lib/db";

export const runtime = "nodejs";

const PEDAGOGY = new Set(["project", "text", "mixed"]);

function toJsonStringArray(v: unknown, field: string): string {
  if (Array.isArray(v)) {
    return JSON.stringify(v.map((x) => String(x).trim()).filter(Boolean));
  }
  if (typeof v === "string") {
    const lines = v
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    return JSON.stringify(lines);
  }
  throw new Error(`Invalid ${field}`);
}

export async function GET() {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT id, course_code, title, level, learning_outcomes, topics, pedagogy_type, syllabus_relpath
       FROM uw_courses ORDER BY course_code ASC`,
    )
    .all();
  return NextResponse.json({ courses: rows });
}

export async function POST(request: Request) {
  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const course_code = typeof body.course_code === "string" ? body.course_code.trim() : "";
  const title = typeof body.title === "string" ? body.title.trim() : "";
  const level = typeof body.level === "number" && Number.isFinite(body.level) ? body.level : null;
  const pedagogy_type =
    typeof body.pedagogy_type === "string" ? body.pedagogy_type.trim() : "";

  if (!course_code) {
    return NextResponse.json({ error: "course_code is required" }, { status: 400 });
  }
  if (!PEDAGOGY.has(pedagogy_type)) {
    return NextResponse.json(
      { error: "pedagogy_type must be project, text, or mixed" },
      { status: 400 },
    );
  }

  let learning_outcomes: string;
  let topics: string;
  try {
    learning_outcomes = toJsonStringArray(body.learning_outcomes, "learning_outcomes");
    topics = toJsonStringArray(body.topics, "topics");
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Invalid fields";
    return NextResponse.json({ error: msg }, { status: 400 });
  }

  const db = getDb();
  try {
    db.prepare(
      `INSERT INTO uw_courses (course_code, title, level, learning_outcomes, topics, pedagogy_type)
       VALUES (@course_code, @title, @level, @learning_outcomes, @topics, @pedagogy_type)`,
    ).run({
      course_code,
      title: title || null,
      level,
      learning_outcomes,
      topics,
      pedagogy_type,
    });
  } catch {
    return NextResponse.json(
      { error: "Could not create course (duplicate code?)" },
      { status: 400 },
    );
  }

  const row = db
    .prepare(`SELECT * FROM uw_courses WHERE course_code = ?`)
    .get(course_code);

  return NextResponse.json({ course: row }, { status: 201 });
}
