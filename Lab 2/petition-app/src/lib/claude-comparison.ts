import Anthropic from "@anthropic-ai/sdk";
import type { UwCourseRow } from "./db";

const MODEL = "claude-sonnet-4-20250514";

const COMPARISON_SYSTEM = `You are helping a university advisor compare a student's external syllabus against a UW course. Your job is to identify which learning outcomes match, which partially match, and which are missing. You do NOT make approval or denial decisions. Return ONLY valid JSON.`;

export type ExternalExtract = {
  learning_outcomes: string[];
  topics_covered: string[];
  deliverables: string[];
  course_level: number;
};

export type ComparisonPayload = {
  matched: { external: string; uw: string; strength: "strong" | "partial" }[];
  missing_from_external: string[];
  extra_in_external: string[];
  course_level_concern: boolean;
  pedagogy_mismatch: boolean;
  summary: string;
};

export function parseModelJson<T>(raw: string): T {
  let s = raw.trim();
  const fence = s.match(/^```(?:json)?\s*([\s\S]*?)```$/i);
  if (fence) s = fence[1].trim();
  return JSON.parse(s) as T;
}

function getClient() {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error("ANTHROPIC_API_KEY is not set");
  }
  return new Anthropic({ apiKey });
}

export async function extractExternalSyllabus(
  rawSyllabusText: string,
): Promise<ExternalExtract> {
  const client = getClient();
  const user = `From the following syllabus / document text, extract structured fields for an external (non-UW) course.
Return ONLY valid JSON with this exact shape:
{
  "learning_outcomes": string[],
  "topics_covered": string[],
  "deliverables": string[],
  "course_level": number
}

Use US-style levels (100, 200, 300, 400) as best estimate. If uncertain, pick the closest and reflect ambiguity in the arrays.

SYLLABUS TEXT:
${rawSyllabusText}`;

  const msg = await client.messages.create({
    model: MODEL,
    max_tokens: 4096,
    messages: [{ role: "user", content: user }],
  });
  const block = msg.content.find((b) => b.type === "text");
  if (!block || block.type !== "text") {
    throw new Error("No text response from model");
  }
  return parseModelJson<ExternalExtract>(block.text);
}

/** Parse an official class syllabus into catalog fields (learning outcomes, topics, etc.). */
export async function extractCatalogFieldsFromSyllabusText(
  rawSyllabusText: string,
): Promise<ExternalExtract> {
  const client = getClient();
  const user = `From the following official university course syllabus text, extract fields for a course catalog record.

Rules:
- learning_outcomes: every stated learning outcome, objective, competency, or "students will be able to…" item — one short string each, preserve meaning, no bullet characters in the strings.
- topics_covered: major themes, units, modules, or week-by-week topics as concise phrases.
- deliverables: assignments, exams, projects, papers, presentations mentioned.
- course_level: US-style level (100–600) inferred from course number, catalog text, or degree context; use 500 for typical graduate / professional if unclear.

Return ONLY valid JSON with this exact shape:
{
  "learning_outcomes": string[],
  "topics_covered": string[],
  "deliverables": string[],
  "course_level": number
}

SYLLABUS TEXT:
${rawSyllabusText}`;

  const msg = await client.messages.create({
    model: MODEL,
    max_tokens: 4096,
    messages: [{ role: "user", content: user }],
  });
  const block = msg.content.find((b) => b.type === "text");
  if (!block || block.type !== "text") {
    throw new Error("No text response from model");
  }
  return parseModelJson<ExternalExtract>(block.text);
}

export async function compareSyllabi(args: {
  external: ExternalExtract;
  uw: UwCourseRow;
}): Promise<ComparisonPayload> {
  const client = getClient();
  const outcomes = JSON.parse(
    args.uw.learning_outcomes || "[]",
  ) as string[];
  const topics = JSON.parse(args.uw.topics || "[]") as string[];

  const user = `External syllabus (structured JSON):
${JSON.stringify(args.external, null, 2)}

UW reference course:
{
  "course_code": ${JSON.stringify(args.uw.course_code)},
  "title": ${JSON.stringify(args.uw.title)},
  "level": ${args.uw.level},
  "learning_outcomes": ${JSON.stringify(outcomes)},
  "topics": ${JSON.stringify(topics)},
  "pedagogy_type": ${JSON.stringify(args.uw.pedagogy_type)}
}

Return ONLY valid JSON with this exact shape:
{
  "matched": [{ "external": "...", "uw": "...", "strength": "strong" | "partial" }],
  "missing_from_external": ["UW outcome not covered..."],
  "extra_in_external": ["External outcome not in UW course..."],
  "course_level_concern": true or false,
  "pedagogy_mismatch": true or false,
  "summary": "2-3 sentence plain English overview"
}`;

  const msg = await client.messages.create({
    model: MODEL,
    max_tokens: 8192,
    system: COMPARISON_SYSTEM,
    messages: [{ role: "user", content: user }],
  });
  const block = msg.content.find((b) => b.type === "text");
  if (!block || block.type !== "text") {
    throw new Error("No text response from model");
  }
  return parseModelJson<ComparisonPayload>(block.text);
}

/** Compare student syllabus extract to the official UW syllabus on file (also structured via extraction). */
export async function compareSyllabusExtracts(args: {
  student: ExternalExtract;
  reference: ExternalExtract;
  uw: UwCourseRow;
}): Promise<ComparisonPayload> {
  const client = getClient();
  const user = `Student external course (from petition materials, structured JSON):
${JSON.stringify(args.student, null, 2)}

UW official class syllabus on file (structured JSON extracted from the advisor-uploaded syllabus):
${JSON.stringify(args.reference, null, 2)}

Official offering metadata from the catalog record (use for course_level_concern vs. student level and pedagogy_mismatch):
{
  "course_code": ${JSON.stringify(args.uw.course_code)},
  "title": ${JSON.stringify(args.uw.title)},
  "level": ${args.uw.level},
  "pedagogy_type": ${JSON.stringify(args.uw.pedagogy_type)}
}

Return ONLY valid JSON with this exact shape:
{
  "matched": [{ "external": "...", "uw": "...", "strength": "strong" | "partial" }],
  "missing_from_external": ["UW / official syllabus outcome not adequately covered in student syllabus..."],
  "extra_in_external": ["Student syllabus emphasizes ... not reflected in official UW syllabus..."],
  "course_level_concern": true or false,
  "pedagogy_mismatch": true or false,
  "summary": "2-3 sentence plain English overview comparing the two syllabi"
}

In "matched", the "uw" side must quote or paraphrase the official UW syllabus extract; "external" is from the student syllabus.`;

  const msg = await client.messages.create({
    model: MODEL,
    max_tokens: 8192,
    system: COMPARISON_SYSTEM,
    messages: [{ role: "user", content: user }],
  });
  const block = msg.content.find((b) => b.type === "text");
  if (!block || block.type !== "text") {
    throw new Error("No text response from model");
  }
  return parseModelJson<ComparisonPayload>(block.text);
}
