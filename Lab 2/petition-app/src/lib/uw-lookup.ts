import type { Database } from "better-sqlite3";
import type { UwCourseRow } from "./db";

/** Match petition `uw_course` to `uw_courses.course_code` (spacing/case insensitive). */
export function lookupUwCourse(
  db: Database,
  petitionCourseField: string | null,
): UwCourseRow | undefined {
  if (!petitionCourseField?.trim()) return undefined;
  const raw = petitionCourseField.trim();
  const spaced = raw.replace(/\s+/g, " ");
  const compact = spaced.replace(/ /g, "").toLowerCase();

  const row = db
    .prepare(
      `SELECT * FROM uw_courses
       WHERE lower(course_code) = lower(?)
          OR lower(replace(course_code, ' ', '')) = ?`,
    )
    .get(spaced, compact) as UwCourseRow | undefined;

  return row;
}
