"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Spinner } from "@/components/Spinner";

type Course = {
  id: number;
  course_code: string;
  title: string | null;
  level: number | null;
  learning_outcomes: string;
  topics: string;
  pedagogy_type: string | null;
  syllabus_relpath: string | null;
};

function linesFromJson(json: string) {
  try {
    const arr = JSON.parse(json) as string[];
    return Array.isArray(arr) ? arr.join("\n") : "";
  } catch {
    return "";
  }
}

export default function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | "new" | null>(null);

  const [course_code, setCourseCode] = useState("");
  const [title, setTitle] = useState("");
  const [level, setLevel] = useState<number>(500);
  const [learningOutcomes, setLearningOutcomes] = useState("");
  const [topics, setTopics] = useState("");
  const [pedagogy_type, setPedagogyType] = useState<"project" | "text" | "mixed">(
    "project",
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [syllabusBanner, setSyllabusBanner] = useState<{
    tone: "success" | "warn";
    text: string;
  } | null>(null);
  const [syllabusBusyId, setSyllabusBusyId] = useState<number | null>(null);
  const syllabusInputRefs = useRef<Record<number, HTMLInputElement | null>>({});

  const load = useCallback(async () => {
    setLoadError(null);
    try {
      const res = await fetch("/api/uw-courses");
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setLoadError(
          typeof data.error === "string" ? data.error : "Could not load courses.",
        );
        setCourses([]);
        return;
      }
      setCourses(data.courses ?? []);
    } catch {
      setLoadError("Network error — could not load the catalog.");
      setCourses([]);
    }
  }, []);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      try {
        await load();
      } finally {
        setLoading(false);
      }
    })();
  }, [load]);

  const resetForm = () => {
    setCourseCode("");
    setTitle("");
    setLevel(500);
    setLearningOutcomes("");
    setTopics("");
    setPedagogyType("project");
    setError(null);
  };

  const openNew = () => {
    resetForm();
    setEditingId("new");
  };

  const openEdit = (c: Course) => {
    setEditingId(c.id);
    setCourseCode(c.course_code);
    setTitle(c.title ?? "");
    setLevel(c.level ?? 500);
    setLearningOutcomes(linesFromJson(c.learning_outcomes));
    setTopics(linesFromJson(c.topics));
    setPedagogyType(
      (c.pedagogy_type as "project" | "text" | "mixed") || "mixed",
    );
    setError(null);
  };

  const save = async () => {
    setSaving(true);
    setError(null);
    try {
      const lo = learningOutcomes
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean);
      const to = topics
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean);
      if (editingId === "new") {
        const res = await fetch("/api/uw-courses", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            course_code,
            title,
            level,
            learning_outcomes: lo,
            topics: to,
            pedagogy_type,
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          setError(typeof data.error === "string" ? data.error : "Save failed");
          return;
        }
        setEditingId(null);
        resetForm();
        await load();
        return;
      }
      if (typeof editingId === "number") {
        const res = await fetch(`/api/uw-courses/${editingId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            course_code,
            title,
            level,
            learning_outcomes: lo,
            topics: to,
            pedagogy_type,
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          setError(typeof data.error === "string" ? data.error : "Save failed");
          return;
        }
        setEditingId(null);
        resetForm();
        await load();
      }
    } catch {
      setError("Network error — changes were not saved.");
    } finally {
      setSaving(false);
    }
  };

  const uploadSyllabus = async (courseId: number, file: File) => {
    setSyllabusBusyId(courseId);
    setLoadError(null);
    setSyllabusBanner(null);
    try {
      const fd = new FormData();
      fd.set("file", file);
      const res = await fetch(`/api/uw-courses/${courseId}/syllabus`, {
        method: "POST",
        body: fd,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setLoadError(typeof data.error === "string" ? data.error : "Upload failed.");
        return;
      }
      const ext = data.catalogExtraction as
        | {
            filled?: boolean;
            learningOutcomeCount?: number;
            topicCount?: number;
            warning?: string;
          }
        | undefined;
      if (ext?.warning) {
        setSyllabusBanner({ tone: "warn", text: ext.warning });
      } else if (ext?.filled) {
        setSyllabusBanner({
          tone: "success",
          text: `Updated catalog from syllabus: ${ext.learningOutcomeCount ?? 0} learning outcomes, ${ext.topicCount ?? 0} topics.`,
        });
      }
      const updated = data.course as Course | undefined;
      if (updated && typeof editingId === "number" && editingId === courseId) {
        setLearningOutcomes(linesFromJson(updated.learning_outcomes));
        setTopics(linesFromJson(updated.topics));
      }
      await load();
    } catch {
      setLoadError("Network error — syllabus was not uploaded.");
    } finally {
      setSyllabusBusyId(null);
    }
  };

  const removeSyllabus = async (c: Course) => {
    if (!confirm(`Remove the official syllabus on file for ${c.course_code}?`)) return;
    setSyllabusBusyId(c.id);
    setLoadError(null);
    try {
      const res = await fetch(`/api/uw-courses/${c.id}/syllabus`, { method: "DELETE" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setLoadError(typeof data.error === "string" ? data.error : "Could not remove syllabus.");
        return;
      }
      await load();
    } catch {
      setLoadError("Network error — syllabus was not removed.");
    } finally {
      setSyllabusBusyId(null);
    }
  };

  const remove = async (c: Course) => {
    if (!confirm(`Delete ${c.course_code}?`)) return;
    try {
      const res = await fetch(`/api/uw-courses/${c.id}`, { method: "DELETE" });
      if (res.ok) await load();
      else setLoadError("Could not delete course.");
    } catch {
      setLoadError("Network error — delete did not complete.");
    }
  };

  return (
    <main className="min-h-[calc(100vh-3.5rem)] text-slate-900">
      <div className="page-container space-y-8">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
            UW course catalog
          </h1>
          <p className="max-w-2xl text-sm leading-relaxed text-slate-600">
            Upload the official class syllabus (PDF or DOCX) to store the file and automatically
            extract learning outcomes and topics. You can still edit fields below anytime.
          </p>
        </header>

        {syllabusBanner && (
          <div
            className={syllabusBanner.tone === "success" ? "alert-success" : "alert-warn"}
            role="status"
          >
            {syllabusBanner.text}
          </div>
        )}

        {loadError && (
          <div className="alert-error" role="alert">
            {loadError}
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2">
          <button type="button" onClick={openNew} className="btn-primary">
            + Add course
          </button>
          {editingId !== null && (
            <button
              type="button"
              onClick={() => {
                setEditingId(null);
                resetForm();
              }}
              className="btn-secondary"
            >
              Cancel
            </button>
          )}
        </div>

        {editingId !== null && (
          <div className="surface-card p-6 sm:p-8">
            <h2 className="text-sm font-semibold text-slate-800">
              {editingId === "new" ? "New course" : `Edit course #${editingId}`}
            </h2>
            {error && (
              <p className="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-900">
                {error}
              </p>
            )}
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="text-sm">
                <span className="mb-2 block font-medium text-slate-700">Course code</span>
                <input
                  className="spreadsheet-input w-full"
                  value={course_code}
                  onChange={(e) => setCourseCode(e.target.value)}
                  placeholder="TECHIN 510"
                />
              </label>
              <label className="text-sm">
                <span className="mb-2 block font-medium text-slate-700">Title</span>
                <input
                  className="spreadsheet-input w-full"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </label>
              <label className="text-sm">
                <span className="mb-2 block font-medium text-slate-700">Level (100–600)</span>
                <input
                  type="number"
                  className="spreadsheet-input w-full"
                  value={level}
                  onChange={(e) => setLevel(Number(e.target.value))}
                />
              </label>
              <label className="text-sm">
                <span className="mb-2 block font-medium text-slate-700">Pedagogy</span>
                <select
                  className="spreadsheet-input w-full"
                  value={pedagogy_type}
                  onChange={(e) =>
                    setPedagogyType(e.target.value as "project" | "text" | "mixed")
                  }
                >
                  <option value="project">Project-based</option>
                  <option value="text">Text / seminar</option>
                  <option value="mixed">Mixed</option>
                </select>
              </label>
              <label className="col-span-full text-sm sm:col-span-2">
                <span className="mb-2 block font-medium text-slate-700">
                  Learning outcomes (one per line → JSON)
                </span>
                <p className="mb-2 text-xs text-slate-500">
                  Upload the syllabus for this course in the table below to auto-fill outcomes and
                  topics (requires <code className="rounded bg-slate-100 px-1 font-mono text-[10px]">ANTHROPIC_API_KEY</code>).
                </p>
                <textarea
                  className="spreadsheet-input min-h-32 w-full font-mono text-xs"
                  value={learningOutcomes}
                  onChange={(e) => setLearningOutcomes(e.target.value)}
                />
              </label>
              <label className="col-span-full text-sm sm:col-span-2">
                <span className="mb-2 block font-medium text-slate-700">
                  Topics (one per line → JSON)
                </span>
                <textarea
                  className="spreadsheet-input min-h-32 w-full font-mono text-xs"
                  value={topics}
                  onChange={(e) => setTopics(e.target.value)}
                />
              </label>
            </div>
            <button
              type="button"
              disabled={saving}
              onClick={() => void save()}
              className="btn-primary mt-6 inline-flex items-center gap-2"
            >
              {saving ? (
                <>
                  <Spinner size="sm" className="text-white" />
                  Saving…
                </>
              ) : (
                "Save"
              )}
            </button>
          </div>
        )}

        <div className="surface-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-xs text-slate-700">
              <thead className="border-b border-slate-200 bg-slate-50/95 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="whitespace-nowrap px-4 py-3">Code</th>
                  <th className="px-4 py-3">Title</th>
                  <th className="whitespace-nowrap px-4 py-3">Level</th>
                  <th className="whitespace-nowrap px-4 py-3">Pedagogy</th>
                  <th className="whitespace-nowrap px-4 py-3">LOs</th>
                  <th className="whitespace-nowrap px-4 py-3">Topics</th>
                  <th className="min-w-[140px] px-4 py-3">Class syllabus</th>
                  <th className="whitespace-nowrap px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="p-12">
                      <div className="flex items-center justify-center gap-3 text-slate-600">
                        <Spinner size="md" />
                        <span className="text-sm font-medium">Loading catalog…</span>
                      </div>
                    </td>
                  </tr>
                ) : (
                  courses.map((c, rowIdx) => {
                    let loCount = 0;
                    let topicCount = 0;
                    try {
                      loCount = (JSON.parse(c.learning_outcomes) as unknown[]).length;
                    } catch {
                      loCount = 0;
                    }
                    try {
                      topicCount = (JSON.parse(c.topics) as unknown[]).length;
                    } catch {
                      topicCount = 0;
                    }
                    return (
                      <tr
                        key={c.id}
                        className={rowIdx % 2 === 0 ? "bg-white" : "bg-slate-50/50"}
                      >
                        <td className="whitespace-nowrap px-4 py-3 font-mono text-sm font-medium text-slate-900">
                          {c.course_code}
                        </td>
                        <td className="max-w-[200px] px-4 py-3 text-slate-800">{c.title}</td>
                        <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                          {c.level ?? "—"}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 capitalize text-slate-600">
                          {c.pedagogy_type}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 tabular-nums text-slate-600">
                          {loCount}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 tabular-nums text-slate-600">
                          {topicCount}
                        </td>
                        <td className="px-4 py-3 align-top">
                          <input
                            type="file"
                            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            className="hidden"
                            ref={(el) => {
                              syllabusInputRefs.current[c.id] = el;
                            }}
                            onChange={(e) => {
                              const f = e.target.files?.[0];
                              e.target.value = "";
                              if (f) void uploadSyllabus(c.id, f);
                            }}
                          />
                          <div className="flex flex-col gap-1.5">
                            {c.syllabus_relpath ? (
                              <>
                                <a
                                  href={`/api/uw-courses/${c.id}/syllabus`}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="link-default text-xs"
                                >
                                  View file
                                </a>
                                <button
                                  type="button"
                                  disabled={syllabusBusyId === c.id}
                                  className="text-left text-xs font-medium text-indigo-600 hover:text-indigo-800 disabled:opacity-50"
                                  onClick={() => syllabusInputRefs.current[c.id]?.click()}
                                >
                                  Replace…
                                </button>
                                <button
                                  type="button"
                                  disabled={syllabusBusyId === c.id}
                                  className="text-left text-xs font-medium text-rose-600 hover:text-rose-800 disabled:opacity-50"
                                  onClick={() => void removeSyllabus(c)}
                                >
                                  Remove
                                </button>
                              </>
                            ) : (
                              <button
                                type="button"
                                disabled={syllabusBusyId === c.id}
                                className="text-left text-xs font-medium text-indigo-600 hover:text-indigo-800 disabled:opacity-50"
                                onClick={() => syllabusInputRefs.current[c.id]?.click()}
                              >
                                {syllabusBusyId === c.id ? "Uploading…" : "Upload PDF/DOCX…"}
                              </button>
                            )}
                          </div>
                        </td>
                        <td className="whitespace-nowrap px-4 py-3">
                          <button
                            type="button"
                            className="link-default mr-3 text-xs"
                            onClick={() => openEdit(c)}
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            className="link-danger text-xs"
                            onClick={() => void remove(c)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
