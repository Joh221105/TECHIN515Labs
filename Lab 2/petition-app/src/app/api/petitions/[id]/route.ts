import { NextResponse } from "next/server";
import { getDb } from "@/lib/db";

export const runtime = "nodejs";

const ALLOWED_STATUS = new Set([
  "pending",
  "in_review",
  "sent_to_instructor",
  "approved",
  "denied",
]);

export async function PATCH(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const db = getDb();
  const existing = db.prepare("SELECT id FROM petitions WHERE id = ?").get(id) as
    | { id: string }
    | undefined;
  if (!existing) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const updates: string[] = [];
  const values: Record<string, string | null> = { id };

  if (typeof body.status === "string") {
    const s = body.status;
    if (!ALLOWED_STATUS.has(s)) {
      return NextResponse.json({ error: "Invalid status" }, { status: 400 });
    }
    updates.push("status = @status");
    values.status = s;
  }
  if (typeof body.instructor_name === "string") {
    updates.push("instructor_name = @instructor_name");
    values.instructor_name = body.instructor_name.trim() || null;
  }
  if (typeof body.instructor_email === "string") {
    updates.push("instructor_email = @instructor_email");
    values.instructor_email = body.instructor_email.trim() || null;
  }
  if (typeof body.notes === "string") {
    updates.push("notes = @notes");
    values.notes = body.notes.trim() || null;
  }

  if (updates.length === 0) {
    return NextResponse.json({ error: "No valid fields to update" }, { status: 400 });
  }

  db.prepare(`UPDATE petitions SET ${updates.join(", ")} WHERE id = @id`).run(values);

  const row = db
    .prepare(
      `SELECT id, student_name, student_email, uw_course, status,
              instructor_name, instructor_email, notes, created_at
       FROM petitions WHERE id = ?`,
    )
    .get(id);

  return NextResponse.json({ petition: row });
}
