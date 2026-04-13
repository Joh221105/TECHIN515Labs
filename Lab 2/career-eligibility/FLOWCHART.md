# Eligibility Decision Flowchart

The diagram below uses **Mermaid** (renders in GitHub, VS Code, and many Markdown viewers). It includes **at least three decision branches** (graduation path, program path, CPT path) and marks where **human review** is required instead of a fully automatic yes/no.

```mermaid
flowchart TD
  Start([Student opens Quick Eligibility Checker]) --> Inputs[Enter program, graduation timing, CPT status]
  Inputs --> V{Valid required fields?}
  V -->|No| Err[Show validation message; do not crash]
  V -->|Yes| G{Graduation = already graduated?}

  G -->|Yes| Alumni[Outcome: Not eligible for current-student services — direct to alumni / career resources]
  Alumni --> End1([End])

  G -->|No| P{Program branch}
  P -->|MSTI or MSEI| C{CPT = full-time?}
  P -->|Graduate Certificate| Q{Within 2 quarters?}
  P -->|Non-degree / Visiting| HR1[**Human review** — do not auto-qualify for mock interviews, panels, or networking]

  Q -->|No| CertNo[Certificate: mock/panels/networking not auto-eligible by timing rule]
  Q -->|Yes| C2{CPT = full-time?}

  C -->|Yes| HR2[**Human review** — panels & networking; confirm CPT compatibility]
  C -->|No| MSEI_OK[Apply MSTI/MSEI eligibility for panels & networking]

  C2 -->|Yes| HR3[**Human review** — panels & networking]
  C2 -->|No| CertOK[Certificate within window: may auto-qualify per spec]

  HR1 --> U{Graduation unknown?}
  HR2 --> MockBranch
  HR3 --> MockBranch
  MSEI_OK --> MockBranch
  CertNo --> MockBranch
  CertOK --> MockBranch

  U -->|Yes| HR4[**Human review** — resume row + any “pending verification” banner]
  U -->|No| ResumeNote[Resume: eligible with human-review banner for Visiting]

  MockBranch{Mock interviews branch} --> MockRules[Apply mock rules: MSTI/MSEI eligible; Cert only if ≤2 quarters; Visiting = human review; Unknown grad = pending verification]
  MockRules --> Out[Render four service rows + reasons + banners]
  ResumeNote --> Out
  HR4 --> Out
  Out --> End2([End])
```

## Where human review belongs (edge cases)

| Situation | Why not fully automatic |
|-----------|-------------------------|
| Non-degree / Visiting | Program standing and service access vary case-by-case. |
| Unknown graduation | Cannot verify student timeline or certificate window. |
| Full-time CPT for panels / networking | Work authorization and event participation may need staff confirmation. |
| Any conflicting or incomplete inputs | Staff should reconcile before promising a slot. |

The **tool should never auto-deny** in a way that blocks the student from contacting Career Services; “human review required” should invite them to book or email, not show a hard error.
