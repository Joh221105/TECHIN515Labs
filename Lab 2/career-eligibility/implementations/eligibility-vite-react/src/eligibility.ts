/**
 * Rule engine for GIX Career Services Quick Eligibility Checker.
 * Source of truth: ../../../SPEC.md
 */

export type Program = "MSTI" | "MSEI" | "CERTIFICATE" | "VISITING";
export type Graduation = "WITHIN_2" | "THREE_PLUS" | "GRADUATED" | "UNKNOWN";
export type Cpt = "NONE" | "PART_TIME" | "FULL_TIME" | "ENDING";

export type ServiceId = "mock" | "resume" | "panels" | "networking";

export type OutcomeKind =
  | "eligible"
  | "not_eligible"
  | "pending_verification"
  | "human_review";

export interface ServiceResult {
  id: ServiceId;
  label: string;
  outcome: OutcomeKind;
  reason: string;
  humanReviewBanner?: boolean;
}

export interface EligibilityEvaluation {
  graduatedBlock?: string;
  rows: ServiceResult[];
  globalBanner?: string;
}

export interface EligibilityInput {
  program: Program | "";
  graduation: Graduation | "";
  cpt: Cpt | "";
}

function isFullTimeCpt(cpt: Cpt): boolean {
  return cpt === "FULL_TIME";
}

function panelsNetworkingBase(args: {
  program: Program;
  graduation: Graduation;
  cpt: Cpt;
}): Omit<ServiceResult, "id" | "label"> {
  const { program, graduation, cpt } = args;

  if (graduation === "GRADUATED") {
    return {
      outcome: "not_eligible",
      reason: "Alumni should use alumni career resources, not current-student event slots.",
    };
  }

  if (program === "VISITING") {
    return {
      outcome: "human_review",
      reason: "Non-degree/visiting status requires Career Services to confirm access.",
    };
  }

  if (isFullTimeCpt(cpt)) {
    return {
      outcome: "human_review",
      reason: "Full-time CPT may affect event participation—staff must confirm.",
    };
  }

  switch (program) {
    case "MSTI":
    case "MSEI":
      if (graduation === "UNKNOWN") {
        return {
          outcome: "pending_verification",
          reason: "Eligibility looks likely for MSTI/MSEI; confirm your graduation timeline with the office.",
        };
      }
      return {
        outcome: "eligible",
        reason: "MSTI/MSEI current students may register for this offering (CPT not full-time).",
      };
    case "CERTIFICATE":
      if (graduation === "THREE_PLUS") {
        return {
          outcome: "not_eligible",
          reason: "Graduate Certificate students are eligible only within two quarters of completion.",
        };
      }
      if (graduation === "UNKNOWN") {
        return {
          outcome: "pending_verification",
          reason: "Certificate window depends on your timeline—Career Services will verify.",
        };
      }
      return {
        outcome: "eligible",
        reason: "Graduate Certificate student within the two-quarter window.",
      };
  }
}

function mockInterviewResult(args: {
  program: Program;
  graduation: Graduation;
  cpt: Cpt;
}): Omit<ServiceResult, "id" | "label"> {
  const { program, graduation } = args;

  if (graduation === "GRADUATED") {
    return {
      outcome: "not_eligible",
      reason: "Mock interviews are for current students; alumni should use alumni resources.",
    };
  }

  switch (program) {
    case "VISITING":
      return {
        outcome: "human_review",
        reason: "Mock interviews are not auto-assigned for Non-degree/Visiting—please meet with staff.",
      };
    case "MSTI":
    case "MSEI":
      if (graduation === "UNKNOWN") {
        return {
          outcome: "pending_verification",
          reason: "MSTI/MSEI students usually qualify; confirm graduation timing with Career Services.",
        };
      }
      return {
        outcome: "eligible",
        reason: "MSTI/MSEI students are eligible for mock interviews.",
      };
    case "CERTIFICATE":
      if (graduation === "WITHIN_2") {
        return {
          outcome: "eligible",
          reason: "Certificate students within two quarters of completion are eligible.",
        };
      }
      if (graduation === "THREE_PLUS") {
        return {
          outcome: "not_eligible",
          reason: "Certificate students must be within two quarters of completion for mock interviews.",
        };
      }
      return {
        outcome: "pending_verification",
        reason: "Eligibility depends on your completion timeline—Career Services will verify.",
      };
  }
}

function resumeResult(args: {
  program: Program;
  graduation: Graduation;
}): Omit<ServiceResult, "id" | "label"> {
  const { program, graduation } = args;

  if (graduation === "GRADUATED") {
    return {
      outcome: "not_eligible",
      reason: "Use alumni resume resources; current-student resume reviews do not apply.",
    };
  }

  const needsBanner = program === "VISITING" || graduation === "UNKNOWN";
  return {
    outcome: "eligible",
    reason: needsBanner
      ? "You may book a resume review, but staff must confirm details first."
      : "Current students may book a resume review.",
    humanReviewBanner: needsBanner,
  };
}

export function evaluateEligibility(input: EligibilityInput): EligibilityEvaluation | null {
  if (!input.program || !input.graduation || !input.cpt) {
    return null;
  }

  const program = input.program as Program;
  const graduation = input.graduation as Graduation;
  const cpt = input.cpt as Cpt;

  if (graduation === "GRADUATED") {
    return {
      graduatedBlock:
        "You indicated you are already graduated. Current-student career events are not available through this checker. Please contact GIX Career Services for alumni resources.",
      rows: [
        {
          id: "mock",
          label: "Mock interviews",
          outcome: "not_eligible",
          reason: "Not eligible — alumni pathway.",
        },
        {
          id: "resume",
          label: "Resume reviews",
          outcome: "not_eligible",
          reason: "Not eligible — use alumni resources.",
        },
        {
          id: "panels",
          label: "Employer panels",
          outcome: "not_eligible",
          reason: "Not eligible — alumni pathway.",
        },
        {
          id: "networking",
          label: "Networking nights",
          outcome: "not_eligible",
          reason: "Not eligible — alumni pathway.",
        },
      ],
    };
  }

  const mock = mockInterviewResult({ program, graduation, cpt });
  const resume = resumeResult({ program, graduation });
  const pnArgs = { program, graduation, cpt };
  const panels = { ...panelsNetworkingBase(pnArgs), id: "panels" as const, label: "Employer panels" };
  const networking = {
    ...panelsNetworkingBase(pnArgs),
    id: "networking" as const,
    label: "Networking nights",
  };

  const rows: ServiceResult[] = [
    { id: "mock", label: "Mock interviews", ...mock },
    { id: "resume", label: "Resume reviews", ...resume },
    panels,
    networking,
  ];

  const anyPending = rows.some((r) => r.outcome === "pending_verification");
  const anyHuman = rows.some((r) => r.outcome === "human_review" || r.humanReviewBanner);

  let globalBanner: string | undefined;
  if (anyHuman && anyPending) {
    globalBanner =
      "Human review and timeline verification may both be required—email or book with Career Services.";
  } else if (anyHuman) {
    globalBanner = "Human review required for at least one service—contact GIX Career Services.";
  } else if (anyPending) {
    globalBanner = "Pending verification: confirm your graduation timeline with Career Services.";
  }

  return { rows, globalBanner };
}
