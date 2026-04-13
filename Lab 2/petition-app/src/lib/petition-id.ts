import { randomInt } from "crypto";
import type { Database } from "better-sqlite3";

const ALPHANUM = "abcdefghijklmnopqrstuvwxyz0123456789";

export function generatePetitionId(): string {
  let suffix = "";
  for (let i = 0; i < 4; i++) {
    suffix += ALPHANUM[randomInt(ALPHANUM.length)];
  }
  return `PET-${suffix}`;
}

export function uniquePetitionId(db: Database) {
  for (let attempt = 0; attempt < 50; attempt++) {
    const id = generatePetitionId();
    const row = db.prepare("SELECT 1 FROM petitions WHERE id = ?").get(id);
    if (!row) return id;
  }
  throw new Error("Could not allocate a unique petition id");
}
