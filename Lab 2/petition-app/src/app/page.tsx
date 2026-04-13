"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Spinner } from "@/components/Spinner";

type AiConfidenceLevel = "green" | "yellow" | "red";

type PetitionRow = {
  id: string;
  student_name: string | null;
  student_email: string | null;
  uw_course: string | null;
  status: string | null;
  instructor_name: string | null;
  instructor_email: string | null;
  notes: string | null;
  created_at: string | null;
  hasCombinedPdf?: boolean;
  hasAiComparison?: boolean;
  aiConfidence?: AiConfidenceLevel | null;
  aiSummary?: string | null;
  aiForwardContext?: string | null;
};

type FileResult = {
  name: string;
  passed: boolean;
  issues: string[];
};

type SubmitResponse = {
  petitionId: string;
  combinedPdfUrl: string | null;
  files: FileResult[];
  followUpEmail?: string;
  banner?: string;
};

const ACCEPT = ".pdf,.png,.jpeg,.jpg,.docx,application/pdf,image/png,image/jpeg,application/vnd.openxmlformats-officedocument.wordprocessingml.document";

const STATUS_OPTIONS = [
  { value: "pending", label: "Pending" },
  { value: "in_review", label: "In Review" },
  { value: "sent_to_instructor", label: "Sent to Instructor" },
  { value: "approved", label: "Approved" },
  { value: "denied", label: "Denied" },
] as const;

type FilterTab = "all" | "pending" | "in_review" | "with_instructor" | "decided";

function formatStatus(status: string | null) {
  const o = STATUS_OPTIONS.find((x) => x.value === status);
  return o?.label ?? status ?? "—";
}

function matchesFilter(p: PetitionRow, tab: FilterTab) {
  const s = p.status ?? "pending";
  switch (tab) {
    case "all":
      return true;
    case "pending":
      return s === "pending";
    case "in_review":
      return s === "in_review";
    case "with_instructor":
      return s === "sent_to_instructor";
    case "decided":
      return s === "approved" || s === "denied";
    default:
      return true;
  }
}

function escapeCsv(v: string) {
  if (/[",\n]/.test(v)) return `"${v.replace(/"/g, '""')}"`;
  return v;
}

function statusCellHighlight(status: string | null) {
  const s = status ?? "pending";
  if (s === "approved") return "bg-emerald-50 ring-1 ring-inset ring-emerald-200/80";
  if (s === "denied") return "bg-rose-50 ring-1 ring-inset ring-rose-200/80";
  if (s === "pending") return "bg-amber-50 ring-1 ring-inset ring-amber-200/80";
  if (s === "in_review") return "bg-sky-50 ring-1 ring-inset ring-sky-200/80";
  return "bg-violet-50 ring-1 ring-inset ring-violet-200/80";
}

export default function Home() {
  const [studentName, setStudentName] = useState("");
  const [studentEmail, setStudentEmail] = useState("");
  const [uwCourse, setUwCourse] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<SubmitResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [petitions, setPetitions] = useState<PetitionRow[]>([]);
  const [filterTab, setFilterTab] = useState<FilterTab>("all");
  const [search, setSearch] = useState("");
  const [listLoading, setListLoading] = useState(true);
  const [listLoadError, setListLoadError] = useState<string | null>(null);
  const [patchError, setPatchError] = useState<string | null>(null);
  const [csvError, setCsvError] = useState<string | null>(null);

  const loadPetitions = useCallback(async () => {
    setListLoadError(null);
    setListLoading(true);
    try {
      const res = await fetch("/api/petitions");
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setListLoadError(
          typeof data.error === "string" ? data.error : "Could not load petitions.",
        );
        setPetitions([]);
        return;
      }
      setPetitions(data.petitions ?? []);
    } catch {
      setListLoadError("Network error — could not load the petition list.");
      setPetitions([]);
    } finally {
      setListLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadPetitions();
  }, [loadPetitions]);

  const filteredPetitions = useMemo(() => {
    const q = search.trim().toLowerCase();
    return petitions.filter((p) => {
      if (!matchesFilter(p, filterTab)) return false;
      if (!q) return true;
      const name = (p.student_name ?? "").toLowerCase();
      const course = (p.uw_course ?? "").toLowerCase();
      return name.includes(q) || course.includes(q);
    });
  }, [petitions, filterTab, search]);

  const addFiles = (list: FileList | File[]) => {
    const next = [...files];
    const arr = Array.from(list);
    for (const f of arr) {
      next.push(f);
    }
    setFiles(next);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
  };

  const patchPetition = async (
    id: string,
    patch: Partial<{
      status: string;
      instructor_name: string;
      instructor_email: string;
      notes: string;
    }>,
  ) => {
    setPatchError(null);
    try {
      const res = await fetch(`/api/petitions/${encodeURIComponent(id)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patch),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setPatchError(
          typeof data.error === "string" ? data.error : "Update failed. Try again.",
        );
        return;
      }
      const updated = data.petition as PetitionRow;
      setPetitions((prev) =>
        prev.map((p) =>
          p.id === id
            ? {
                ...p,
                ...updated,
                hasCombinedPdf: p.hasCombinedPdf,
                hasAiComparison: p.hasAiComparison,
                aiConfidence: p.aiConfidence,
                aiSummary: p.aiSummary,
                aiForwardContext: p.aiForwardContext,
              }
            : p,
        ),
      );
    } catch {
      setPatchError("Network error — changes were not saved.");
    }
  };

  const handleStatusChange = (p: PetitionRow, nextStatus: string) => {
    if (nextStatus === "approved" || nextStatus === "denied") {
      const label = STATUS_OPTIONS.find((o) => o.value === nextStatus)?.label ?? nextStatus;
      if (
        !window.confirm(
          `Change status to “${label}” for ${p.id}? This updates the recorded outcome.`,
        )
      ) {
        return;
      }
    }
    void patchPetition(p.id, { status: nextStatus });
  };

  function aiConfidenceLabel(c: AiConfidenceLevel | null | undefined) {
    if (c === "green") return "high";
    if (c === "yellow") return "moderate";
    if (c === "red") return "low";
    return "none";
  }

  const exportCsv = () => {
    setCsvError(null);
    try {
      const headers = [
        "Petition ID",
        "Student Name",
        "Student Email",
        "UW Course",
        "Status",
        "AI Confidence",
        "Instructor",
        "Notes",
        "Date Submitted",
      ];
      const lines = [headers.map(escapeCsv).join(",")];
      for (const p of petitions) {
        lines.push(
          [
            p.id,
            p.student_name ?? "",
            p.student_email ?? "",
            p.uw_course ?? "",
            formatStatus(p.status),
            aiConfidenceLabel(p.aiConfidence),
            p.instructor_name ?? "",
            p.notes ?? "",
            p.created_at ?? "",
          ]
            .map((c) => escapeCsv(String(c)))
            .join(","),
        );
      }
      const csv = lines.join("\n");
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "petitions.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setCsvError("Could not export CSV.");
    }
  };

  /** Forward to instructor modal */
  const [forwardRow, setForwardRow] = useState<PetitionRow | null>(null);
  const [forwardName, setForwardName] = useState("");
  const [forwardEmail, setForwardEmail] = useState("");
  const [forwardStep, setForwardStep] = useState<"form" | "generated">("form");
  const [forwardSubject, setForwardSubject] = useState("");
  const [forwardBody, setForwardBody] = useState("");
  const [forwardBusy, setForwardBusy] = useState(false);
  const [forwardError, setForwardError] = useState<string | null>(null);

  const openForward = (p: PetitionRow) => {
    setForwardRow(p);
    setForwardName((p.instructor_name ?? "").trim());
    setForwardEmail((p.instructor_email ?? "").trim());
    setForwardStep("form");
    setForwardSubject("");
    setForwardBody("");
    setForwardError(null);
  };

  const closeForward = () => {
    setForwardRow(null);
    setForwardStep("form");
    setForwardSubject("");
    setForwardBody("");
    setForwardError(null);
  };

  const generateForwardEmail = async () => {
    if (!forwardRow) return;
    const p = petitions.find((row) => row.id === forwardRow.id) ?? forwardRow;
    const name = forwardName.trim();
    const email = forwardEmail.trim();
    const course = (p.uw_course ?? "").trim() || "the requested course";
    const student = (p.student_name ?? "").trim() || "a student";

    const subject = `Course Petition Review — ${course} — ${student}`;

    const summaryBlock =
      (p.aiSummary ?? "").trim() ||
      "No AI comparison summary is available yet. Please review the petition materials and the attached combined syllabus in the petition tool.";

    const flagsBlock =
      (p.aiForwardContext ?? "").trim() ||
      "No additional discrepancy list was generated — please rely on your review of the syllabus PDF.";

    const body = [
      `Hello${name ? ` ${name}` : ""},`,
      "",
      `A student has submitted a petition for ${course}. Please review the attached combined syllabus (from the petition packet) and the comparison summary below.`,
      "",
      "Comparison summary (AI-assisted, for reference only):",
      summaryBlock,
      "",
      "Flagged gaps / items to double-check:",
      flagsBlock,
      "",
      "Could you share feedback within about two weeks so we can move this petition toward a decision?",
      "",
      "Thank you,",
      "Jason",
    ].join("\n");

    setForwardBusy(true);
    setForwardError(null);
    try {
      const res = await fetch(`/api/petitions/${encodeURIComponent(p.id)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: "sent_to_instructor",
          instructor_name: name || null,
          instructor_email: email || null,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setForwardError(
          typeof data.error === "string" ? data.error : "Could not update petition.",
        );
        return;
      }
      const updated = data.petition as PetitionRow;
      setPetitions((prev) =>
        prev.map((row) =>
          row.id === p.id
            ? {
                ...row,
                ...updated,
                hasCombinedPdf: row.hasCombinedPdf,
                hasAiComparison: row.hasAiComparison,
                aiConfidence: row.aiConfidence,
                aiSummary: row.aiSummary,
                aiForwardContext: row.aiForwardContext,
              }
            : row,
        ),
      );
      setForwardSubject(subject);
      setForwardBody(body);
      setForwardStep("generated");
      setForwardRow((r) =>
        r
          ? {
              ...r,
              ...updated,
              hasCombinedPdf: r.hasCombinedPdf,
              hasAiComparison: r.hasAiComparison,
              aiConfidence: r.aiConfidence,
              aiSummary: r.aiSummary,
              aiForwardContext: r.aiForwardContext,
            }
          : r,
      );
    } catch {
      setForwardError("Network error — email was not generated and status may be unchanged.");
    } finally {
      setForwardBusy(false);
    }
  };

  const copyForwardEmail = async () => {
    try {
      const text = `${forwardSubject}\n\n${forwardBody}`;
      await navigator.clipboard.writeText(text);
    } catch {
      setForwardError("Could not copy to clipboard.");
    }
  };

  const mailtoForward = () => {
    const to = forwardEmail.trim();
    if (!to) return;
    const q = (s: string) => encodeURIComponent(s);
    window.location.href = `mailto:${q(to)}?subject=${q(forwardSubject)}&body=${q(forwardBody)}`;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!studentName.trim() || !studentEmail.trim() || !uwCourse.trim()) {
      setError("Please fill in student name, email, and UW course.");
      return;
    }
    if (files.length === 0) {
      setError("Add at least one file.");
      return;
    }
    setSubmitting(true);
    try {
      const fd = new FormData();
      fd.set("student_name", studentName.trim());
      fd.set("student_email", studentEmail.trim());
      fd.set("uw_course", uwCourse.trim());
      for (const f of files) fd.append("files", f);
      const res = await fetch("/api/petitions", { method: "POST", body: fd });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(typeof data.error === "string" ? data.error : "Submit failed");
        return;
      }
      setResult(data as SubmitResponse);
      setFiles([]);
      await loadPetitions();
    } catch {
      setError("Network error — upload did not complete. Check your connection and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-[calc(100vh-3.5rem)] text-slate-900">
      <div className="page-container space-y-8">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
            Course petition review
          </h1>
          <p className="max-w-2xl text-sm leading-relaxed text-slate-600">
            Upload materials, validate documents, and track petitions.
          </p>
        </header>

        <section className="surface-card p-6 sm:p-8">
          <h2 className="section-label mb-6">New petition</h2>
          <form onSubmit={onSubmit} className="space-y-6">
            <div className="grid gap-5 sm:grid-cols-3">
              <label className="block text-sm">
                <span className="mb-2 block font-medium text-slate-700">Student name</span>
                <input
                  className="spreadsheet-input w-full"
                  value={studentName}
                  onChange={(e) => setStudentName(e.target.value)}
                  autoComplete="name"
                />
              </label>
              <label className="block text-sm">
                <span className="mb-2 block font-medium text-slate-700">Student email</span>
                <input
                  type="email"
                  className="spreadsheet-input w-full"
                  value={studentEmail}
                  onChange={(e) => setStudentEmail(e.target.value)}
                  autoComplete="email"
                />
              </label>
              <label className="block text-sm">
                <span className="mb-2 block font-medium text-slate-700">UW course</span>
                <input
                  className="spreadsheet-input w-full"
                  placeholder="e.g. TECHIN 510"
                  value={uwCourse}
                  onChange={(e) => setUwCourse(e.target.value)}
                />
              </label>
            </div>

            <div>
              <span className="mb-2 block text-sm font-medium text-slate-700">
                Upload student syllabi, transcripts, and supporting documents
              </span>
              <div
                role="presentation"
                onDragEnter={(e) => {
                  e.preventDefault();
                  setDragActive(true);
                }}
                onDragOver={(e) => e.preventDefault()}
                onDragLeave={() => setDragActive(false)}
                onDrop={onDrop}
                className={`rounded-xl border-2 border-dashed px-4 py-10 text-center text-sm transition-[border-color,background-color,box-shadow] ${
                  dragActive
                    ? "border-indigo-400 bg-indigo-50/90 shadow-inner shadow-indigo-500/10"
                    : "border-slate-200 bg-slate-50/80 hover:border-slate-300"
                }`}
              >
                <input
                  type="file"
                  multiple
                  accept={ACCEPT}
                  className="hidden"
                  id="file-input"
                  onChange={(e) => {
                    if (e.target.files?.length) addFiles(e.target.files);
                    e.target.value = "";
                  }}
                />
                <label htmlFor="file-input" className="cursor-pointer font-medium text-indigo-600 hover:text-indigo-800">
                  Click to browse
                </label>
                <span className="text-slate-600">
                  {" "}
                  or drag and drop files here (.pdf, .png, .jpeg, .docx)
                </span>
              </div>
              {files.length > 0 && (
                <ul className="mt-3 max-h-28 space-y-1 overflow-auto rounded-lg border border-slate-100 bg-slate-50/80 px-3 py-2 text-xs text-slate-600">
                  {files.map((f, i) => (
                    <li key={`${f.name}-${i}`} className="truncate">
                      {f.name}{" "}
                      <span className="text-slate-400">({Math.round(f.size / 1024)} KB)</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {error && (
              <p className="alert-error" role="alert">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="btn-primary inline-flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <Spinner size="sm" className="text-white" />
                  Uploading and validating documents…
                </>
              ) : (
                "Submit"
              )}
            </button>
          </form>

          {result && (
            <div className="mt-8 space-y-5 border-t border-slate-200/80 pt-8">
              {result.banner && (
                <div className="alert-warn" role="status">
                  {result.banner}
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-slate-800">
                  Petition{" "}
                  <code className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-800 ring-1 ring-slate-200/80">
                    {result.petitionId}
                  </code>
                </p>
                <ul className="mt-4 space-y-3">
                  {result.files.map((f) => (
                    <li
                      key={f.name}
                      className="flex gap-3 rounded-lg border border-slate-100 bg-slate-50/50 px-3 py-2.5 text-sm"
                    >
                      <span className={f.passed ? "text-emerald-600" : "text-rose-600"} aria-hidden>
                        {f.passed ? "✓" : "⚠"}
                      </span>
                      <span>
                        <span className="font-medium text-slate-900">{f.name}</span>
                        {!f.passed && (
                          <span className="mt-0.5 block text-sm text-rose-800">
                            {f.issues.join("; ")}
                          </span>
                        )}
                        {f.passed && <span className="text-emerald-700"> OK</span>}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
              {result.combinedPdfUrl && (
                <div className="rounded-xl border border-indigo-200/80 bg-linear-to-br from-indigo-50/90 to-white p-5 ring-1 ring-indigo-500/10">
                  <p className="text-sm font-semibold text-slate-900">Combined syllabus PDF</p>
                  <p className="mt-1 text-xs text-slate-600">
                    All valid student PDFs merged into one file — Jason’s primary handoff artifact.
                  </p>
                  <a
                    className="btn-primary mt-4 inline-flex items-center justify-center px-5 py-2.5"
                    href={result.combinedPdfUrl}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Download combined PDF
                  </a>
                </div>
              )}
              {result.followUpEmail && (
                <div className="surface-muted p-4">
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Follow-up email draft
                    </span>
                    <button
                      type="button"
                      className="btn-secondary px-3 py-1 text-xs"
                      onClick={async () => {
                        try {
                          await navigator.clipboard.writeText(result.followUpEmail!);
                        } catch {
                          setError("Could not copy follow-up email to clipboard.");
                        }
                      }}
                    >
                      Copy to clipboard
                    </button>
                  </div>
                  <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg border border-slate-200/80 bg-white px-3 py-2 font-mono text-xs text-slate-800">
                    {result.followUpEmail}
                  </pre>
                </div>
              )}
            </div>
          )}
        </section>

        <section className="surface-card overflow-hidden">
          <div className="flex flex-col gap-4 border-b border-slate-200/80 bg-slate-50/90 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <h2 className="section-label">
              Petition tracker
            </h2>
            <div className="flex flex-wrap items-center gap-2">
              <input
                type="search"
                placeholder="Search student or course…"
                className="spreadsheet-input h-9 w-full min-w-48 max-w-xs text-xs sm:w-48"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <button
                type="button"
                onClick={exportCsv}
                className="btn-secondary h-9 px-3 text-xs"
              >
                Export CSV
              </button>
            </div>
          </div>
          {csvError && (
            <p className="border-b border-rose-100 bg-rose-50/80 px-4 py-2.5 text-xs text-rose-900 sm:px-6" role="alert">
              {csvError}
            </p>
          )}
          {listLoadError && (
            <p className="border-b border-rose-100 bg-rose-50/80 px-4 py-2.5 text-xs text-rose-900 sm:px-6" role="alert">
              {listLoadError}
            </p>
          )}
          {patchError && (
            <p className="border-b border-rose-100 bg-rose-50/80 px-4 py-2.5 text-xs text-rose-900 sm:px-6" role="alert">
              {patchError}
            </p>
          )}
          <div className="flex flex-wrap gap-1.5 border-b border-slate-100 px-4 py-3 sm:px-6">
            {(
              [
                ["all", "All"],
                ["pending", "Pending"],
                ["in_review", "In Review"],
                ["with_instructor", "With Instructor"],
                ["decided", "Decided"],
              ] as const
            ).map(([key, label]) => (
              <button
                key={key}
                type="button"
                onClick={() => setFilterTab(key)}
                className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-[color,background-color,box-shadow] ${
                  filterTab === key
                    ? "bg-white text-slate-900 shadow-sm ring-1 ring-slate-200/90"
                    : "text-slate-600 hover:bg-slate-100/80 hover:text-slate-900"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="overflow-x-auto bg-white">
            {listLoading ? (
              <div className="flex items-center justify-center gap-3 py-20 text-slate-600">
                <Spinner size="lg" />
                <span className="text-sm font-medium">Loading petitions…</span>
              </div>
            ) : petitions.length === 0 ? (
              <p className="px-6 py-16 text-center text-sm text-slate-600">
                No petitions yet — upload documents above to get started.
              </p>
            ) : (
              <>
                <table className="w-full min-w-[960px] text-left text-[11px] leading-snug text-slate-700">
                  <thead className="sticky top-0 z-10 border-b border-slate-200 bg-slate-50/95 backdrop-blur-sm">
                    <tr className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                      <th className="whitespace-nowrap px-3 py-3">Petition ID</th>
                      <th className="whitespace-nowrap px-3 py-3">Student</th>
                      <th className="whitespace-nowrap px-3 py-3">Email</th>
                      <th className="whitespace-nowrap px-3 py-3">UW course</th>
                      <th className="whitespace-nowrap px-3 py-3">Status</th>
                      <th className="max-w-[52px] whitespace-normal px-2 py-3 text-center leading-tight">
                        AI
                      </th>
                      <th className="whitespace-nowrap px-3 py-3">Instructor</th>
                      <th className="min-w-[120px] px-3 py-3">Notes</th>
                      <th className="whitespace-nowrap px-3 py-3">Submitted</th>
                      <th className="whitespace-nowrap px-3 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredPetitions.map((p, idx) => (
                      <tr
                        key={p.id}
                        className={
                          idx % 2 === 0 ? "bg-white" : "bg-slate-50/40"
                        }
                      >
                        <td className="whitespace-nowrap px-3 py-2 font-mono text-[10px] text-slate-800">
                          {p.id}
                        </td>
                        <td className="max-w-[120px] truncate px-3 py-2 text-slate-900">
                          {p.student_name}
                        </td>
                        <td className="max-w-[160px] truncate px-3 py-2 text-slate-700">
                          {p.student_email}
                        </td>
                        <td className="whitespace-nowrap px-3 py-2 font-medium text-slate-900">
                          {p.uw_course}
                        </td>
                        <td className={`px-2 py-1.5 ${statusCellHighlight(p.status)}`}>
                          <select
                            className="spreadsheet-input h-8 max-w-[148px] border-0 bg-transparent py-0 pr-6 text-[11px] shadow-none focus:ring-0"
                            value={p.status ?? "pending"}
                            onChange={(e) => handleStatusChange(p, e.target.value)}
                          >
                            {STATUS_OPTIONS.map((o) => (
                              <option key={o.value} value={o.value}>
                                {o.label}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="px-2 py-2 text-center align-middle">
                          <span
                            className="inline-flex h-6 w-6 items-center justify-center"
                            title={
                              p.aiConfidence === "green"
                                ? "AI alignment: stronger (heuristic)"
                                : p.aiConfidence === "yellow"
                                  ? "AI alignment: moderate — some gaps"
                                  : p.aiConfidence === "red"
                                    ? "AI alignment: concerns — review gaps / flags"
                                    : "No comparison generated"
                            }
                          >
                            <span
                              className={`inline-block h-2.5 w-2.5 rounded-full ring-2 ring-white ${
                                p.aiConfidence === "green"
                                  ? "bg-emerald-500 shadow-[0_0_0_1px_rgb(16_185_129/0.35)]"
                                  : p.aiConfidence === "yellow"
                                    ? "bg-amber-400 shadow-[0_0_0_1px_rgb(251_191_36/0.4)]"
                                    : p.aiConfidence === "red"
                                      ? "bg-rose-500 shadow-[0_0_0_1px_rgb(244_63_94/0.35)]"
                                      : "bg-slate-300"
                              }`}
                            />
                          </span>
                        </td>
                        <td className="px-2 py-1.5">
                          <input
                            key={`instructor-${p.id}-${p.instructor_name ?? ""}`}
                            className="spreadsheet-input h-8 w-full min-w-[100px] max-w-[140px] px-2 text-[11px]"
                            defaultValue={p.instructor_name ?? ""}
                            onBlur={(e) =>
                              void patchPetition(p.id, {
                                instructor_name: e.target.value,
                              })
                            }
                            aria-label="Instructor name"
                          />
                        </td>
                        <td className="px-2 py-1.5">
                          <input
                            key={`notes-${p.id}-${p.notes ?? ""}`}
                            className="spreadsheet-input h-8 w-full min-w-[140px] max-w-[220px] px-2 text-[11px]"
                            defaultValue={p.notes ?? ""}
                            onBlur={(e) =>
                              void patchPetition(p.id, { notes: e.target.value })
                            }
                            aria-label="Notes"
                          />
                        </td>
                        <td className="whitespace-nowrap px-3 py-2 text-slate-500">
                          {p.created_at
                            ? (() => {
                                const raw = p.created_at;
                                const iso = raw.includes("T") ? raw : raw.replace(" ", "T");
                                const d = new Date(iso);
                                return Number.isNaN(d.getTime()) ? raw : d.toLocaleString();
                              })()
                            : "—"}
                        </td>
                        <td className="whitespace-nowrap px-3 py-2">
                          <Link
                            className="link-default mr-3 text-[11px]"
                            href={`/petition/${encodeURIComponent(p.id)}`}
                          >
                            View
                          </Link>
                          <button
                            type="button"
                            className="link-default text-[11px]"
                            onClick={() => openForward(p)}
                          >
                            Forward
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {filteredPetitions.length === 0 && (
                  <p className="border-t border-slate-100 px-6 py-10 text-center text-sm text-slate-600">
                    No petitions match your filters.
                  </p>
                )}
              </>
            )}
          </div>
        </section>

        {forwardRow && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-[2px]"
            role="dialog"
            aria-modal="true"
            aria-labelledby="forward-modal-title"
            onClick={closeForward}
          >
            <div
              className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl border border-slate-200/90 bg-white shadow-2xl shadow-slate-900/20 ring-1 ring-slate-900/5"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="border-b border-slate-100 bg-slate-50/80 px-5 py-4">
                <h3 id="forward-modal-title" className="text-sm font-semibold text-slate-900">
                  Forward to instructor
                </h3>
                <p className="mt-1 text-xs text-slate-500">
                  Petition <span className="font-mono text-slate-700">{forwardRow.id}</span> ·{" "}
                  {forwardRow.uw_course}
                </p>
              </div>
              <div className="space-y-4 p-5 text-sm">
                {forwardStep === "form" && (
                  <>
                    <label className="block text-sm">
                      <span className="mb-1.5 block font-medium text-slate-700">
                        Instructor name
                      </span>
                      <input
                        className="spreadsheet-input h-10 w-full"
                        value={forwardName}
                        onChange={(e) => setForwardName(e.target.value)}
                      />
                    </label>
                    <label className="block text-sm">
                      <span className="mb-1.5 block font-medium text-slate-700">
                        Instructor email
                      </span>
                      <input
                        type="email"
                        className="spreadsheet-input h-10 w-full"
                        value={forwardEmail}
                        onChange={(e) => setForwardEmail(e.target.value)}
                      />
                    </label>
                    {forwardError && (
                      <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-900">
                        {forwardError}
                      </p>
                    )}
                    <div className="flex flex-wrap gap-2 pt-1">
                      <button
                        type="button"
                        disabled={forwardBusy}
                        onClick={() => void generateForwardEmail()}
                        className="btn-primary inline-flex items-center gap-2 text-xs"
                      >
                        {forwardBusy ? (
                          <>
                            <Spinner size="sm" className="text-white" />
                            Working…
                          </>
                        ) : (
                          "Generate Email"
                        )}
                      </button>
                      <button
                        type="button"
                        onClick={closeForward}
                        className="btn-secondary text-xs"
                      >
                        Cancel
                      </button>
                    </div>
                  </>
                )}
                {forwardStep === "generated" && (
                  <>
                    <p className="text-xs text-slate-600">
                      Status updated to <strong>Sent to Instructor</strong>. Instructor details
                      saved.
                    </p>
                    <div className="surface-muted space-y-2 p-3 text-xs">
                      <p className="font-semibold text-slate-600">Subject</p>
                      <p className="text-slate-900">{forwardSubject}</p>
                      <p className="pt-2 font-semibold text-slate-600">Body</p>
                      <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded-lg border border-slate-200/80 bg-white p-2 font-mono text-slate-800">
                        {forwardBody}
                      </pre>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => void copyForwardEmail()}
                        className="btn-primary text-xs"
                      >
                        Copy to Clipboard
                      </button>
                      <button
                        type="button"
                        disabled={!forwardEmail.trim()}
                        onClick={mailtoForward}
                        className="btn-secondary text-xs disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        Open in Email Client
                      </button>
                      <button
                        type="button"
                        onClick={closeForward}
                        className="btn-secondary text-xs"
                      >
                        Close
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
