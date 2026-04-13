"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState, type ReactNode } from "react";
import { Spinner } from "@/components/Spinner";
import type { ComparisonPayload, ExternalExtract } from "@/lib/claude-comparison";
import type { UwCourseRow } from "@/lib/db";

type Bundle = {
  petition: {
    id: string;
    student_name: string | null;
    student_email: string | null;
    uw_course: string | null;
    status: string | null;
    created_at: string | null;
  };
  uwCourse: UwCourseRow | null;
  savedComparison: {
    externalExtract: ExternalExtract;
    referenceExtract: ExternalExtract | null;
    comparison: ComparisonPayload;
    summary: string | null;
    course_level_concern: boolean;
    pedagogy_mismatch: boolean;
    created_at: string | null;
  } | null;
  hasExtractableText: boolean;
  hasCombinedPdf: boolean;
  usesUwSyllabusFile: boolean;
};

function ListBlock({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h3>
      <div className="mt-2">{children}</div>
    </div>
  );
}

export default function PetitionComparisonPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";

  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!id) return;
    setLoadError(null);
    setLoading(true);
    try {
      const res = await fetch(`/api/petitions/${encodeURIComponent(id)}/comparison`);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setLoadError(
          typeof data.error === "string" ? data.error : "Could not load this petition.",
        );
        setBundle(null);
        return;
      }
      setBundle(data as Bundle);
    } catch {
      setLoadError("Network error — check your connection and try again.");
      setBundle(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  const generate = async () => {
    if (!id) return;
    setBusy(true);
    setGenError(null);
    try {
      const res = await fetch(`/api/petitions/${encodeURIComponent(id)}/comparison`, {
        method: "POST",
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setGenError(
          typeof data.error === "string"
            ? data.error
            : "AI comparison failed. Check ANTHROPIC_API_KEY and try again.",
        );
        return;
      }
      setBundle(data as Bundle);
    } catch {
      setGenError("Network error — the comparison request did not complete.");
    } finally {
      setBusy(false);
    }
  };

  if (loadError) {
    return (
      <main className="min-h-[calc(100vh-3.5rem)]">
        <div className="page-container py-16">
          <div className="alert-error max-w-xl" role="alert">
            {loadError}
          </div>
          <Link href="/" className="link-default mt-6 inline-block text-sm">
            ← Back to petitions
          </Link>
        </div>
      </main>
    );
  }

  if (loading || !bundle) {
    return (
      <div className="flex min-h-[45vh] items-center justify-center gap-3 px-4 py-20 text-slate-600">
        <Spinner size="lg" />
        <span className="text-sm font-medium">Loading petition…</span>
      </div>
    );
  }

  const { petition, uwCourse, savedComparison, hasExtractableText, hasCombinedPdf, usesUwSyllabusFile } =
    bundle;
  const comp = savedComparison?.comparison;
  const ext = savedComparison?.externalExtract;
  const refExt = savedComparison?.referenceExtract ?? null;

  const uwOutcomes = uwCourse
    ? (JSON.parse(uwCourse.learning_outcomes || "[]") as string[])
    : [];
  const uwTopics = uwCourse ? (JSON.parse(uwCourse.topics || "[]") as string[]) : [];

  const combinedHref = `/api/petitions/${encodeURIComponent(id)}/combined`;

  return (
    <main className="min-h-[calc(100vh-3.5rem)] text-slate-900">
      <div className="page-container space-y-6">
        {hasCombinedPdf && (
          <div className="surface-card border-indigo-200/60 bg-linear-to-br from-indigo-50/50 to-white p-5 sm:p-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">Combined syllabus PDF</p>
                <p className="mt-1 text-xs leading-relaxed text-slate-600">
                  All valid student PDFs merged into one file — use for review, forwarding, and
                  records.
                </p>
              </div>
              <a
                href={combinedHref}
                target="_blank"
                rel="noreferrer"
                className="btn-primary inline-flex shrink-0 items-center justify-center px-5 py-2.5"
              >
                Download combined PDF
              </a>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <Link href="/" className="link-default text-sm">
              ← Petitions
            </Link>
            <h1 className="mt-3 text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
              Comparison · <span className="font-mono text-xl text-slate-700 sm:text-2xl">{petition.id}</span>
            </h1>
            <p className="mt-2 text-sm text-slate-600">
              <span className="font-medium text-slate-800">{petition.student_name}</span>
              <span className="text-slate-400"> · </span>
              {petition.student_email}
              <span className="text-slate-400"> · </span>
              <span className="font-mono font-medium text-slate-900">{petition.uw_course}</span>
            </p>
          </div>
          <div className="flex flex-col items-stretch gap-2 sm:items-end">
            <button
              type="button"
              disabled={busy || !uwCourse || !hasExtractableText}
              onClick={() => void generate()}
              title={
                !uwCourse
                  ? "Match petition UW course to catalog first"
                  : !hasExtractableText
                    ? "Need PDF/DOCX text in uploads"
                    : undefined
              }
              className="btn-primary inline-flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {busy ? (
                <>
                  <Spinner size="sm" className="text-white" />
                  Analyzing syllabus…
                </>
              ) : savedComparison ? (
                "Regenerate comparison"
              ) : (
                "Generate comparison"
              )}
            </button>
          </div>
        </div>

        {!uwCourse && (
          <div className="alert-warn" role="status">
            No catalog course matches <code className="rounded bg-amber-100/80 px-1.5 py-0.5 font-mono text-xs">{petition.uw_course}</code>. Add or adjust the course under{" "}
            <Link href="/courses" className="font-semibold text-amber-900 underline decoration-amber-900/30 underline-offset-2 hover:decoration-amber-900">
              Courses
            </Link>{" "}
            so the code matches (spacing is OK).
          </div>
        )}

        {!hasExtractableText && (
          <div className="alert-error" role="alert">
            No extractable text found in this petition’s files. PDFs or DOCX with real text are
            required for AI comparison.
          </div>
        )}

        {uwCourse && usesUwSyllabusFile && (
          <div className="alert-success" role="status">
            This catalog course has an <strong>official class syllabus on file</strong>. AI comparison
            uses the student materials against that syllabus.
          </div>
        )}

        {uwCourse && !usesUwSyllabusFile && (
          <div className="rounded-xl border border-slate-200/90 bg-slate-50/90 px-4 py-3 text-sm text-slate-700" role="status">
            No official class syllabus is on file for this course yet — comparison uses the learning outcomes
            and topics entered on the{" "}
            <Link href="/courses" className="link-default">
              Courses
            </Link>{" "}
            tab. Upload a syllabus there for syllabus-to-syllabus review.
          </div>
        )}

        {genError && (
          <div className="alert-error" role="alert">
            {genError}
          </div>
        )}

        {comp && (
          <>
            {(comp.course_level_concern || comp.pedagogy_mismatch) && (
              <div className="flex flex-col gap-2">
                {comp.course_level_concern && (
                  <div className="alert-warn">
                    Possible course level concern — review external vs. UW level carefully.
                  </div>
                )}
                {comp.pedagogy_mismatch && (
                  <div className="rounded-xl border border-orange-200/90 bg-orange-50 px-4 py-3 text-sm text-orange-950">
                    Pedagogy may not align with the UW course (e.g., project vs. seminar).
                  </div>
                )}
              </div>
            )}

            <div className="surface-card p-5 sm:p-6">
              <p className="text-sm leading-relaxed text-slate-800">{comp.summary}</p>
              <p className="mt-4 text-xs text-slate-500">
                AI-assisted comparison — for advisor reference only
              </p>
            </div>
          </>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="surface-card p-5 sm:p-6">
            <h2 className="section-label mb-5">External syllabus (extracted)</h2>
            {ext ? (
              <div className="space-y-5 text-sm text-slate-800">
                <ListBlock title="Course level (estimate)">
                  <p className="font-mono text-slate-900">{ext.course_level}</p>
                </ListBlock>
                <ListBlock title="Learning outcomes">
                  <ul className="list-inside list-disc space-y-1 text-slate-700">
                    {ext.learning_outcomes.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                </ListBlock>
                <ListBlock title="Topics covered">
                  <ul className="list-inside list-disc space-y-1 text-slate-700">
                    {ext.topics_covered.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                </ListBlock>
                <ListBlock title="Deliverables">
                  <ul className="list-inside list-disc space-y-1 text-slate-700">
                    {ext.deliverables.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                </ListBlock>
              </div>
            ) : (
              <p className="text-sm text-slate-600">
                Run <strong className="text-slate-800">Generate comparison</strong> to extract structure
                from uploads.
              </p>
            )}
          </section>

          <section className="surface-card p-5 sm:p-6">
            <h2 className="section-label mb-5">
              {refExt ? "UW class syllabus (extracted)" : "UW reference course (catalog)"}
            </h2>
            {uwCourse ? (
              <div className="space-y-5 text-sm text-slate-800">
                <p className="font-mono text-base font-semibold text-slate-900">{uwCourse.course_code}</p>
                <p className="text-slate-800">{uwCourse.title}</p>
                <p className="text-slate-600">
                  Level {uwCourse.level ?? "—"} · Pedagogy:{" "}
                  <span className="capitalize">{uwCourse.pedagogy_type}</span>
                </p>
                {usesUwSyllabusFile && (
                  <a
                    href={`/api/uw-courses/${uwCourse.id}/syllabus`}
                    target="_blank"
                    rel="noreferrer"
                    className="link-default inline-block text-sm"
                  >
                    Download official syllabus file
                  </a>
                )}
                {refExt ? (
                  <>
                    <ListBlock title="Course level (estimate)">
                      <p className="font-mono text-slate-900">{refExt.course_level}</p>
                    </ListBlock>
                    <ListBlock title="Learning outcomes">
                      <ul className="list-inside list-disc space-y-1 text-slate-700">
                        {refExt.learning_outcomes.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    </ListBlock>
                    <ListBlock title="Topics covered">
                      <ul className="list-inside list-disc space-y-1 text-slate-700">
                        {refExt.topics_covered.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    </ListBlock>
                    <ListBlock title="Deliverables">
                      <ul className="list-inside list-disc space-y-1 text-slate-700">
                        {refExt.deliverables.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    </ListBlock>
                  </>
                ) : (
                  <>
                    <ListBlock title="Learning outcomes">
                      <ul className="list-inside list-disc space-y-1 text-slate-700">
                        {uwOutcomes.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    </ListBlock>
                    <ListBlock title="Topics">
                      <ul className="list-inside list-disc space-y-1 text-slate-700">
                        {uwTopics.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    </ListBlock>
                  </>
                )}
              </div>
            ) : (
              <p className="text-sm text-slate-600">No matching catalog course.</p>
            )}
          </section>
        </div>

        {comp && (
          <section className="surface-card p-5 sm:p-6">
            <h2 className="section-label mb-6">Outcome comparison</h2>

            <div className="space-y-3">
              {comp.matched.map((m, i) => (
                <div
                  key={`${m.uw}-${i}`}
                  className={`grid gap-3 rounded-xl border p-4 text-sm sm:grid-cols-2 ${
                    m.strength === "strong"
                      ? "border-emerald-200/90 bg-emerald-50/60"
                      : "border-amber-200/90 bg-amber-50/50"
                  }`}
                >
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                      External
                    </span>
                    <p className="mt-1.5 text-slate-900">{m.external}</p>
                  </div>
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                      UW
                    </span>
                    <p className="mt-1.5 text-slate-900">{m.uw}</p>
                  </div>
                  <div className="text-xs font-medium text-slate-600 sm:col-span-2">
                    {m.strength === "strong" ? "Strong match" : "Partial match"}
                  </div>
                </div>
              ))}
            </div>

            {comp.missing_from_external.length > 0 && (
              <div className="mt-8">
                <h3 className="text-[10px] font-semibold uppercase tracking-wide text-rose-700">
                  UW outcomes not seen in external syllabus
                </h3>
                <ul className="mt-3 list-inside list-disc space-y-1.5 text-sm text-rose-900">
                  {comp.missing_from_external.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              </div>
            )}

            {comp.extra_in_external.length > 0 && (
              <div className="mt-8">
                <h3 className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                  Extra in external syllabus (not mapped to UW outcomes)
                </h3>
                <ul className="mt-3 list-inside list-disc space-y-1.5 rounded-xl border border-slate-200/80 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                  {comp.extra_in_external.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
