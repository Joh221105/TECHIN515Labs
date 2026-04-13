import fs from "fs";
import path from "path";
import { extractDocxTextFromBuffer } from "./validate-documents";
import { petitionUploadDir } from "./paths";

async function pdfBufferToText(buffer: Buffer): Promise<string> {
  const { PDFParse } = await import("pdf-parse");
  const parser = new PDFParse({ data: new Uint8Array(buffer) });
  try {
    const { text } = await parser.getText();
    return (text ?? "").trim();
  } finally {
    await parser.destroy().catch(() => undefined);
  }
}

const MAX_CHARS = 120_000;

/**
 * Reads syllabus text from combined.pdf, then other PDFs / DOCX in the petition upload folder.
 */
export async function extractTextFromPetitionUploads(petitionId: string): Promise<string> {
  const dir = petitionUploadDir(petitionId);
  if (!fs.existsSync(dir)) return "";

  const parts: string[] = [];
  const combined = path.join(dir, "combined.pdf");
  if (fs.existsSync(combined)) {
    const buf = fs.readFileSync(combined);
    const t = await pdfBufferToText(buf);
    if (t) parts.push(t);
  } else {
    const entries = fs.readdirSync(dir);
    const pdfs = entries.filter((f) => f.toLowerCase().endsWith(".pdf")).sort();
    for (const name of pdfs) {
      const buf = fs.readFileSync(path.join(dir, name));
      const t = await pdfBufferToText(buf);
      if (t) parts.push(`--- ${name} ---\n${t}`);
    }
  }

  const docxFiles = fs
    .readdirSync(dir)
    .filter((f) => f.toLowerCase().endsWith(".docx"))
    .sort();
  for (const name of docxFiles) {
    try {
      const buf = fs.readFileSync(path.join(dir, name));
      parts.push(`--- ${name} ---\n${extractDocxTextFromBuffer(buf)}`);
    } catch {
      // skip unreadable docx
    }
  }

  let out = parts.join("\n\n").trim();
  if (out.length > MAX_CHARS) {
    out = `${out.slice(0, MAX_CHARS)}\n\n[Text truncated for model context]`;
  }
  return out;
}

const SINGLE_FILE_MAX_CHARS = 120_000;

/**
 * Extract text from a single PDF or DOCX on disk (absolute path).
 * Used for UW course syllabi uploaded on the Courses tab.
 */
export async function extractTextFromLocalFile(absPath: string): Promise<string> {
  if (!fs.existsSync(absPath)) return "";

  const ext = path.extname(absPath).toLowerCase();
  let chunk = "";

  if (ext === ".pdf") {
    const buf = fs.readFileSync(absPath);
    chunk = await pdfBufferToText(buf);
  } else if (ext === ".docx") {
    try {
      const buf = fs.readFileSync(absPath);
      chunk = extractDocxTextFromBuffer(buf);
    } catch {
      return "";
    }
  } else {
    return "";
  }

  let out = chunk.trim();
  if (out.length > SINGLE_FILE_MAX_CHARS) {
    out = `${out.slice(0, SINGLE_FILE_MAX_CHARS)}\n\n[Text truncated for model context]`;
  }
  return out;
}
