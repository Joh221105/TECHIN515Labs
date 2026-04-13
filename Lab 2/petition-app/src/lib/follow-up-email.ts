import type { FileValidation } from "./validate-documents";

export function buildFollowUpEmailBody(opts: {
  studentName: string;
  studentEmail: string;
  uwCourse: string;
  validations: FileValidation[];
}): string {
  const problems = opts.validations.filter((v) => !v.passed);
  const lines: string[] = [
    `Hi ${opts.studentName},`,
    "",
    `Regarding your course petition for ${opts.uwCourse}, a few uploaded documents need attention:`,
    "",
  ];
  for (const p of problems) {
    lines.push(`• ${p.originalName}: ${p.issues.join("; ")}`);
  }
  lines.push(
    "",
    "Please reply with updated files (PDF preferred for syllabi) or let us know if you have questions.",
    "",
    "Thank you,",
    "Jason",
  );
  return lines.join("\n");
}
