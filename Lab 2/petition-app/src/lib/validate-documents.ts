import { unzipSync } from "fflate";
import { PDFDocument } from "pdf-lib";

const STOP_WORDS = new Set([
  "the",
  "and",
  "is",
  "of",
  "to",
  "for",
  "in",
  "that",
  "with",
  "a",
]);

const IMAGE_MESSAGE =
  "Image file — cannot extract text. Please request a PDF from the student.";

export type FileValidation = {
  originalName: string;
  savedRelativePath: string;
  passed: boolean;
  issues: string[];
  mergePdfBytes: Uint8Array | null;
};

function pathBasename(p: string) {
  const normalized = p.replace(/\\/g, "/");
  const parts = normalized.split("/");
  return parts[parts.length - 1] || "file";
}

function extensionOf(filename: string) {
  const base = pathBasename(filename);
  const dot = base.lastIndexOf(".");
  if (dot <= 0) return "";
  return base.slice(dot + 1).toLowerCase();
}

function isPng(buf: Uint8Array) {
  return (
    buf.length >= 8 &&
    buf[0] === 0x89 &&
    buf[1] === 0x50 &&
    buf[2] === 0x4e &&
    buf[3] === 0x47
  );
}

function isJpeg(buf: Uint8Array) {
  return buf.length >= 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff;
}

function extractDocxPlainText(xml: string) {
  const chunks: string[] = [];
  const re = /<w:t(?:\s[^>]*)?>([^<]*)<\/w:t>/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(xml)) !== null) {
    if (m[1]) chunks.push(m[1]);
  }
  return chunks.join(" ").replace(/\s+/g, " ").trim();
}

export function extractDocxTextFromBuffer(buffer: Buffer): string {
  const unzipped = unzipSync(new Uint8Array(buffer));
  const entry =
    unzipped["word/document.xml"] ??
    Object.entries(unzipped).find(([k]) =>
      k.toLowerCase().endsWith("word/document.xml"),
    )?.[1];
  if (!entry) throw new Error("Missing word/document.xml");
  const xml = new TextDecoder("utf-8").decode(entry);
  return extractDocxPlainText(xml);
}

function tokenizeWords(text: string): string[] {
  const lower = text.toLowerCase();
  const matches = lower.match(/[a-z']+/g);
  return matches ?? [];
}

function englishStopWordCheck(text: string): string | null {
  const words = tokenizeWords(text);
  if (words.length < 100) return null;
  let stops = 0;
  for (const w of words) {
    if (STOP_WORDS.has(w)) stops++;
  }
  const pct = (stops / words.length) * 100;
  if (pct < 5) return "May not be in English";
  return null;
}

async function extractPdfText(buffer: Buffer): Promise<string> {
  const { PDFParse } = await import("pdf-parse");
  const parser = new PDFParse({ data: new Uint8Array(buffer) });
  try {
    const { text } = await parser.getText();
    return (text ?? "").trim();
  } finally {
    await parser.destroy().catch(() => undefined);
  }
}

export async function validateFile(args: {
  originalName: string;
  buffer: Buffer;
  savedRelativePath: string;
}): Promise<FileValidation> {
  const { originalName, buffer, savedRelativePath } = args;
  const issues: string[] = [];
  let mergePdfBytes: Uint8Array | null = null;

  const ext = extensionOf(originalName);
  const buf = new Uint8Array(buffer);

  try {
    if (buffer.length === 0) {
      issues.push("Corrupt file");
      return {
        originalName,
        savedRelativePath,
        passed: issues.length === 0,
        issues,
        mergePdfBytes: null,
      };
    }

    if (ext === "png" || ext === "jpeg" || ext === "jpg") {
      const magicOk =
        (ext === "png" && isPng(buf)) ||
        ((ext === "jpeg" || ext === "jpg") && isJpeg(buf));
      if (!magicOk) {
        return {
          originalName,
          savedRelativePath,
          passed: false,
          issues: ["Corrupt file"],
          mergePdfBytes: null,
        };
      }
      return {
        originalName,
        savedRelativePath,
        passed: false,
        issues: [IMAGE_MESSAGE],
        mergePdfBytes: null,
      };
    }

    if (ext === "pdf") {
      let text: string;
      try {
        text = await extractPdfText(buffer);
      } catch {
        issues.push("Corrupt file");
        return {
          originalName,
          savedRelativePath,
          passed: false,
          issues,
          mergePdfBytes: null,
        };
      }
      if (text.length < 50) issues.push("Empty document");
      const eng = englishStopWordCheck(text);
      if (eng) issues.push(eng);
      if (text.length >= 50) {
        mergePdfBytes = new Uint8Array(buffer);
      }
      return {
        originalName,
        savedRelativePath,
        passed: issues.length === 0,
        issues,
        mergePdfBytes,
      };
    }

    if (ext === "docx") {
      let text: string;
      try {
        text = extractDocxTextFromBuffer(buffer);
      } catch {
        issues.push("Corrupt file");
        return {
          originalName,
          savedRelativePath,
          passed: false,
          issues,
          mergePdfBytes: null,
        };
      }
      if (text.length < 50) issues.push("Empty document");
      const eng = englishStopWordCheck(text);
      if (eng) issues.push(eng);
      return {
        originalName,
        savedRelativePath,
        passed: issues.length === 0,
        issues,
        mergePdfBytes: null,
      };
    }

    issues.push("Unsupported file type (use PDF, PNG, JPEG, or DOCX)");
    return {
      originalName,
      savedRelativePath,
      passed: false,
      issues,
      mergePdfBytes: null,
    };
  } catch {
    issues.length = 0;
    issues.push("Corrupt file");
    return {
      originalName,
      savedRelativePath,
      passed: false,
      issues,
      mergePdfBytes: null,
    };
  }
}

export async function mergePdfBuffers(pdfs: Uint8Array[]): Promise<Uint8Array | null> {
  if (pdfs.length === 0) return null;
  const merged = await PDFDocument.create();
  for (const bytes of pdfs) {
    try {
      const doc = await PDFDocument.load(bytes);
      const pages = await merged.copyPages(doc, doc.getPageIndices());
      for (const p of pages) merged.addPage(p);
    } catch {
      // skip unloadable fragments
    }
  }
  if (merged.getPageCount() === 0) return null;
  const out = await merged.save();
  return out;
}
