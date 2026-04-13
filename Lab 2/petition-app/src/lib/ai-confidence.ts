import type { ComparisonPayload } from "./claude-comparison";

export type AiConfidenceLevel = "green" | "yellow" | "red";

export function confidenceFromComparison(
  c: ComparisonPayload,
  courseLevelConcern: boolean,
  pedagogyMismatch: boolean,
): AiConfidenceLevel {
  const missing = c.missing_from_external?.length ?? 0;
  if (courseLevelConcern || pedagogyMismatch || missing >= 2) return "red";
  if (missing === 0) return "green";
  return "yellow";
}

export function buildDiscrepancyNoteForForward(
  c: ComparisonPayload,
  courseLevelConcern: boolean,
  pedagogyMismatch: boolean,
): string {
  const lines: string[] = [];
  if (courseLevelConcern) {
    lines.push(
      "• The AI-assisted comparison flagged a possible course level concern (external course vs. UW course level).",
    );
  }
  if (pedagogyMismatch) {
    lines.push(
      "• A possible pedagogy mismatch was flagged (e.g., project-based vs. text/seminar emphasis).",
    );
  }
  const missing = c.missing_from_external ?? [];
  if (missing.length > 0) {
    lines.push("• UW learning outcomes not clearly evidenced in the external syllabus:");
    for (const m of missing) {
      lines.push(`  – ${m}`);
    }
  }
  const extra = c.extra_in_external ?? [];
  if (extra.length > 0) {
    lines.push(
      "• Additional content in the external syllabus not mapped to UW outcomes (for context only):",
    );
    const cap = Math.min(extra.length, 5);
    for (let i = 0; i < cap; i++) {
      lines.push(`  – ${extra[i]}`);
    }
    if (extra.length > 5) {
      lines.push(`  … and ${extra.length - 5} more item(s).`);
    }
  }
  if (lines.length === 0) {
    return "No additional discrepancy list beyond the summary — please still verify against the syllabus PDF.";
  }
  return lines.join("\n");
}
