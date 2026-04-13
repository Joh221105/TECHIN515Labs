# GIX Career Services — Quick Eligibility Checker (5-Sentence Specification)

1. The widget collects three required inputs: GIX program (MSTI, MSEI, Graduate Certificate, or Non-degree/Visiting), graduation timing relative to the current quarter (within the next two quarters, three or more quarters remaining before degree completion, already graduated, or unknown/unsure), and CPT status (not on CPT, part-time CPT, full-time CPT, or CPT ending this quarter).

2. On submit, the tool displays eligibility for exactly four services—mock interviews, resume reviews, employer panels, and networking nights—using deterministic boolean rules only (no ML, no external APIs), and each row must show a short plain-language reason string.

3. If graduation is **already graduated**, the student is **not** eligible for any of the four services; the UI must show a single consolidated message directing them to alumni resources instead of implying current-student services.

4. **Mock interviews:** MSTI and MSEI students who are not graduated are eligible unless graduation is unknown, in which case status is “eligible pending verification” with a visible banner; Graduate Certificate students are eligible only if graduation is within two quarters; Non-degree/Visiting students are never automatically eligible and must show “human review required” for mock interviews.

5. **Resume reviews** are eligible for all not-graduated programs, but if graduation is unknown **or** the program is Non-degree/Visiting, the result must include a mandatory human-review banner; **employer panels** and **networking nights** share the same rules: MSTI/MSEI not graduated are eligible when CPT is not full-time, Graduate Certificate students are eligible only when within two quarters and CPT is not full-time, Non-degree/Visiting always requires human review, and **full-time CPT** always requires human review for panels and networking (part-time CPT and CPT ending this quarter follow the same eligibility as “not on CPT”).
