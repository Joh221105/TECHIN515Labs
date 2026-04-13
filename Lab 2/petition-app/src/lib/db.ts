import fs from "fs";
import Database from "better-sqlite3";
import { DATA_DIR, DB_PATH, UPLOADS_ROOT } from "./paths";

let db: Database.Database | null = null;

function applyMigrations(instance: Database.Database) {
  const uwCols = instance.prepare(`PRAGMA table_info(uw_courses)`).all() as { name: string }[];
  if (!uwCols.some((c) => c.name === "syllabus_relpath")) {
    instance.exec(`ALTER TABLE uw_courses ADD COLUMN syllabus_relpath TEXT`);
  }
  const aiCols = instance.prepare(`PRAGMA table_info(ai_comparisons)`).all() as { name: string }[];
  if (!aiCols.some((c) => c.name === "reference_extract")) {
    instance.exec(`ALTER TABLE ai_comparisons ADD COLUMN reference_extract TEXT`);
  }
}

/** Ensures `./data` and `./data/uploads` exist (called automatically by `getDb()`). */
export function ensureDataDirectories() {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  if (!fs.existsSync(UPLOADS_ROOT)) fs.mkdirSync(UPLOADS_ROOT, { recursive: true });
}

export function getDb() {
  if (db) return db;
  ensureDataDirectories();
  const instance = new Database(DB_PATH);
  instance.exec(`
    CREATE TABLE IF NOT EXISTS petitions (
      id TEXT PRIMARY KEY,
      student_name TEXT,
      student_email TEXT,
      uw_course TEXT,
      status TEXT DEFAULT 'pending',
      instructor_name TEXT,
      instructor_email TEXT,
      notes TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS uw_courses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      course_code TEXT UNIQUE NOT NULL,
      title TEXT,
      level INTEGER,
      learning_outcomes TEXT,
      topics TEXT,
      pedagogy_type TEXT
    );

    CREATE TABLE IF NOT EXISTS ai_comparisons (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      petition_id TEXT NOT NULL UNIQUE,
      uw_course_id INTEGER NOT NULL,
      external_extract TEXT NOT NULL,
      comparison_json TEXT NOT NULL,
      summary TEXT,
      course_level_concern INTEGER NOT NULL DEFAULT 0,
      pedagogy_mismatch INTEGER NOT NULL DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (petition_id) REFERENCES petitions(id),
      FOREIGN KEY (uw_course_id) REFERENCES uw_courses(id)
    );
  `);
  applyMigrations(instance);
  db = instance;
  return instance;
}

export type PetitionRow = {
  id: string;
  student_name: string | null;
  student_email: string | null;
  uw_course: string | null;
  status: string | null;
  instructor_name: string | null;
  instructor_email: string | null;
  notes: string | null;
  created_at: string | null;
};

export type UwCourseRow = {
  id: number;
  course_code: string;
  title: string | null;
  level: number | null;
  learning_outcomes: string | null;
  topics: string | null;
  pedagogy_type: string | null;
  syllabus_relpath: string | null;
};

export type AiComparisonRow = {
  id: number;
  petition_id: string;
  uw_course_id: number;
  external_extract: string;
  comparison_json: string;
  summary: string | null;
  course_level_concern: number;
  pedagogy_mismatch: number;
  created_at: string | null;
};
