import path from "path";

export const DATA_DIR = path.join(process.cwd(), "data");
export const DB_PATH = path.join(DATA_DIR, "petitions.db");
export const UPLOADS_ROOT = path.join(DATA_DIR, "uploads");

export function petitionUploadDir(petitionId: string) {
  return path.join(UPLOADS_ROOT, petitionId);
}

export function uwCourseUploadDir(courseId: number) {
  return path.join(UPLOADS_ROOT, "uw-courses", String(courseId));
}
