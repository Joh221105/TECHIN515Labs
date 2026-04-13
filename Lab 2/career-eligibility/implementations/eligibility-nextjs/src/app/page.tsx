"use client";

import { useMemo, useState } from "react";
import {
  evaluateEligibility,
  type Cpt,
  type EligibilityInput,
  type Graduation,
  type Program,
} from "@/lib/eligibility";

const emptyInput: EligibilityInput = { program: "", graduation: "", cpt: "" };

function outcomeStyles(outcome: string): string {
  switch (outcome) {
    case "eligible":
      return "bg-emerald-50 text-emerald-900 ring-emerald-200";
    case "not_eligible":
      return "bg-slate-100 text-slate-700 ring-slate-200";
    case "pending_verification":
      return "bg-amber-50 text-amber-950 ring-amber-200";
    case "human_review":
      return "bg-orange-50 text-orange-950 ring-orange-200";
    default:
      return "bg-slate-50 text-slate-800 ring-slate-200";
  }
}

function outcomeLabel(outcome: string): string {
  switch (outcome) {
    case "eligible":
      return "Eligible";
    case "not_eligible":
      return "Not eligible";
    case "pending_verification":
      return "Eligible pending verification";
    case "human_review":
      return "Human review required";
    default:
      return outcome;
  }
}

export default function Home() {
  const [input, setInput] = useState<EligibilityInput>(emptyInput);
  const [submitted, setSubmitted] = useState(false);
  const [attemptedSubmit, setAttemptedSubmit] = useState(false);

  const evaluation = useMemo(() => {
    if (!submitted) return null;
    return evaluateEligibility(input);
  }, [input, submitted]);

  const validationError =
    attemptedSubmit && (!input.program || !input.graduation || !input.cpt);

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setAttemptedSubmit(true);
    if (!input.program || !input.graduation || !input.cpt) {
      setSubmitted(false);
      return;
    }
    setSubmitted(true);
  }

  function resetForm() {
    setInput(emptyInput);
    setSubmitted(false);
    setAttemptedSubmit(false);
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <header className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-wide text-indigo-600">
          GIX Career Services
        </p>
        <h1 className="mt-1 text-3xl font-bold text-slate-900">Quick Eligibility Checker</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600">
          Enter your program, graduation timing, and CPT status. Results are informational only and
          may require staff confirmation.
        </p>
      </header>

      <form
        onSubmit={onSubmit}
        className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm ring-1 ring-slate-950/5"
        noValidate
      >
        <div className="grid gap-6 sm:grid-cols-1">
          <div>
            <label htmlFor="program" className="block text-sm font-medium text-slate-800">
              GIX program
            </label>
            <select
              id="program"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              value={input.program}
              onChange={(e) => setInput((s) => ({ ...s, program: e.target.value as Program | "" }))}
            >
              <option value="">Select program…</option>
              <option value="MSTI">MSTI</option>
              <option value="MSEI">MSEI</option>
              <option value="CERTIFICATE">Graduate Certificate</option>
              <option value="VISITING">Non-degree / Visiting</option>
            </select>
          </div>

          <div>
            <label htmlFor="graduation" className="block text-sm font-medium text-slate-800">
              Graduation timing (relative to now)
            </label>
            <select
              id="graduation"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              value={input.graduation}
              onChange={(e) =>
                setInput((s) => ({ ...s, graduation: e.target.value as Graduation | "" }))
              }
            >
              <option value="">Select timing…</option>
              <option value="WITHIN_2">Within the next two quarters</option>
              <option value="THREE_PLUS">Three or more quarters remaining</option>
              <option value="GRADUATED">Already graduated</option>
              <option value="UNKNOWN">Unknown / unsure</option>
            </select>
          </div>

          <div>
            <label htmlFor="cpt" className="block text-sm font-medium text-slate-800">
              CPT status
            </label>
            <select
              id="cpt"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              value={input.cpt}
              onChange={(e) => setInput((s) => ({ ...s, cpt: e.target.value as Cpt | "" }))}
            >
              <option value="">Select CPT status…</option>
              <option value="NONE">Not on CPT</option>
              <option value="PART_TIME">Part-time CPT</option>
              <option value="FULL_TIME">Full-time CPT</option>
              <option value="ENDING">CPT ending this quarter</option>
            </select>
          </div>
        </div>

        {validationError && (
          <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800 ring-1 ring-red-200" role="alert">
            Please select all three fields before checking eligibility.
          </p>
        )}

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="submit"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Check eligibility
          </button>
          <button
            type="button"
            onClick={resetForm}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-800 shadow-sm hover:bg-slate-50"
          >
            Reset
          </button>
        </div>
      </form>

      {evaluation && (
        <section className="mt-8 space-y-4" aria-live="polite">
          {evaluation.globalBanner && (
            <div className="rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950">
              {evaluation.globalBanner}
            </div>
          )}

          {evaluation.graduatedBlock && (
            <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 ring-1 ring-slate-950/5">
              <p className="font-medium text-slate-900">Heads up</p>
              <p className="mt-1">{evaluation.graduatedBlock}</p>
            </div>
          )}

          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm ring-1 ring-slate-950/5">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-600">
                <tr>
                  <th className="px-4 py-3">Service</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {evaluation.rows.map((row) => (
                  <tr key={row.id}>
                    <td className="px-4 py-3 font-medium text-slate-900">{row.label}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${outcomeStyles(row.outcome)}`}
                      >
                        {outcomeLabel(row.outcome)}
                      </span>
                      {row.humanReviewBanner && (
                        <span className="mt-2 block text-xs font-semibold text-orange-800">
                          Human review banner: confirm with Career Services.
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-700">{row.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  );
}
