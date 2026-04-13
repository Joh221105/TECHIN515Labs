import { useMemo, useState, type FormEvent } from "react";
import {
  evaluateEligibility,
  type Cpt,
  type EligibilityInput,
  type Graduation,
  type Program,
} from "./eligibility";

const emptyInput: EligibilityInput = { program: "", graduation: "", cpt: "" };

function outcomeBadgeClass(outcome: string): string {
  switch (outcome) {
    case "eligible":
      return "badge badge-eligible";
    case "not_eligible":
      return "badge badge-not";
    case "pending_verification":
      return "badge badge-pending";
    case "human_review":
      return "badge badge-human";
    default:
      return "badge badge-not";
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

export default function App() {
  const [input, setInput] = useState<EligibilityInput>(emptyInput);
  const [submitted, setSubmitted] = useState(false);
  const [attemptedSubmit, setAttemptedSubmit] = useState(false);

  const evaluation = useMemo(() => {
    if (!submitted) return null;
    return evaluateEligibility(input);
  }, [input, submitted]);

  const validationError =
    attemptedSubmit && (!input.program || !input.graduation || !input.cpt);

  function onSubmit(e: FormEvent) {
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
    <div className="app">
      <header>
        <p className="eyebrow">GIX Career Services</p>
        <h1>Quick Eligibility Checker</h1>
        <p className="lede">
          Enter your program, graduation timing, and CPT status. Results are informational and may
          require staff confirmation.
        </p>
      </header>

      <form className="panel" onSubmit={onSubmit} noValidate>
        <div className="field">
          <label htmlFor="program">GIX program</label>
          <select
            id="program"
            value={input.program}
            onChange={(e) =>
              setInput((s) => ({ ...s, program: e.target.value as Program | "" }))
            }
          >
            <option value="">Select program…</option>
            <option value="MSTI">MSTI</option>
            <option value="MSEI">MSEI</option>
            <option value="CERTIFICATE">Graduate Certificate</option>
            <option value="VISITING">Non-degree / Visiting</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="graduation">Graduation timing (relative to now)</label>
          <select
            id="graduation"
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

        <div className="field">
          <label htmlFor="cpt">CPT status</label>
          <select
            id="cpt"
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

        {validationError ? (
          <p className="validation" role="alert">
            Please select all three fields before checking eligibility.
          </p>
        ) : null}

        <div className="actions">
          <button type="submit" className="btn btn-primary">
            Check eligibility
          </button>
          <button type="button" className="btn btn-ghost" onClick={resetForm}>
            Reset
          </button>
        </div>
      </form>

      {evaluation ? (
        <section className="results" aria-live="polite">
          {evaluation.globalBanner ? (
            <div className="global-banner">{evaluation.globalBanner}</div>
          ) : null}

          {evaluation.graduatedBlock ? (
            <div className="alumni-note">
              <strong>Heads up</strong>
              {evaluation.graduatedBlock}
            </div>
          ) : null}

          <div className="cards">
            {evaluation.rows.map((row) => (
              <article key={row.id} className="card">
                <span className={outcomeBadgeClass(row.outcome)}>{outcomeLabel(row.outcome)}</span>
                <h2>{row.label}</h2>
                <p>{row.reason}</p>
                {row.humanReviewBanner ? (
                  <span className="row-banner">
                    Human review banner: confirm with Career Services.
                  </span>
                ) : null}
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
