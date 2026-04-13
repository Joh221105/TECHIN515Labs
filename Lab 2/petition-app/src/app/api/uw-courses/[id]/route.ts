import fs from "fs";
import path from "path";
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

export async function PATCH(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const numericId = Number(id);
  if (!Number.isFinite(numericId)) {
    return NextResponse.json({ error: "Invalid id" }, { status: 400 });
  }

  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const db = getDb();
  const existing = db.prepare("SELECT id FROM uw_courses WHERE id = ?").get(numericId) as
    | { id: number }
    | undefined;
  if (!existing) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const updates: string[] = [];
  const values: Record<string, string | number | null> = { id: numericId };

  if (typeof body.course_code === "string") {
    updates.push("course_code = @course_code");
    values.course_code = body.course_code.trim();
  }
  if (typeof body.title === "string") {
    updates.push("title = @title");
    values.title = body.title.trim() || null;
  }
  if (typeof body.level === "number" && Number.isFinite(body.level)) {
    updates.push("level = @level");
    values.level = body.level;
  }
  if (typeof body.pedagogy_type === "string") {
    const p = body.pedagogy_type.trim();
    if (!PEDAGOGY.has(p)) {
      return NextResponse.json(
        { error: "pedagogy_type must be project, text, or mixed" },
        { status: 400 },
      );
    }
    updates.push("pedagogy_type = @pedagogy_type");
    values.pedagogy_type = p;
  }
  if (body.learning_outcomes !== undefined) {
    try {
      values.learning_outcomes = toJsonStringArray(body.learning_outcomes, "learning_outcomes");
      updates.push("learning_outcomes = @learning_outcomes");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Invalid learning_outcomes";
      return NextResponse.json({ error: msg }, { status: 400 });
    }
  }
  if (body.topics !== undefined) {
    try {
      values.topics = toJsonStringArray(body.topics, "topics");
      updates.push("topics = @topics");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Invalid topics";
      return NextResponse.json({ error: msg }, { status: 400 });
    }
  }

  if (updates.length === 0) {
    return NextResponse.json({ error: "No valid fields" }, { status: 400 });
  }

  try {
    db.prepare(`UPDATE uw_courses SET ${updates.join(", ")} WHERE id = @id`).run(values);
  } catch {
    return NextResponse.json({ error: "Update failed (duplicate code?)" }, { status: 400 });
  }

  const row = db.prepare("SELECT * FROM uw_courses WHERE id = ?").get(numericId);
  return NextResponse.json({ course: row });
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
    .prepare("SELECT syllabus_relpath FROM uw_courses WHERE id = ?")
    .get(numericId) as { syllabus_relpath: string | null } | undefined;
  const res = db.prepare("DELETE FROM uw_courses WHERE id = ?").run(numericId);
  if (res.changes === 0) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  if (row?.syllabus_relpath) {
    const abs = path.join(process.cwd(), row.syllabus_relpath);
    try {
      if (fs.existsSync(abs)) fs.unlinkSync(abs);
    } catch {
      /* ignore */
    }
  }
  return NextResponse.json({ ok: true });
}
