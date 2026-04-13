import { getDb } from "./db";

type SeedCourse = {
  course_code: string;
  title: string;
  level: number;
  learning_outcomes: string[];
  topics: string[];
  pedagogy_type: string;
};

const GIX_COURSES: SeedCourse[] = [
  {
    course_code: "TECHIN 510",
    title: "Global Innovation Studio I",
    level: 500,
    learning_outcomes: [
      "Frame ambiguous stakeholder problems and translate them into testable hypotheses.",
      "Prototype and iterate solutions using human-centered design methods.",
      "Collaborate effectively in cross-cultural, interdisciplinary teams.",
      "Communicate product concepts through storytelling, demos, and concise documentation.",
    ],
    topics: [
      "Needfinding and qualitative user research",
      "Journey maps and stakeholder analysis",
      "Rapid prototyping (digital and physical)",
      "Team dynamics and agile rituals",
      "Ethics of emerging technology in society",
    ],
    pedagogy_type: "project",
  },
  {
    course_code: "TECHIN 515",
    title: "Data Science & Machine Learning for Physical Computing",
    level: 500,
    learning_outcomes: [
      "Collect, clean, and visualize sensor and interaction data from physical devices.",
      "Select and train supervised models appropriate for embedded constraints.",
      "Evaluate model performance with reproducible experiments and baselines.",
      "Integrate inference pipelines with hardware prototypes safely and responsibly.",
    ],
    topics: [
      "Time-series signals and feature engineering",
      "Classical ML vs. lightweight deep models",
      "Edge deployment and latency tradeoffs",
      "Debugging data drift and failure modes",
      "Privacy, consent, and dataset documentation",
    ],
    pedagogy_type: "mixed",
  },
  {
    course_code: "TECHIN 594",
    title: "Innovation Leadership & Venture Formation",
    level: 500,
    learning_outcomes: [
      "Assess market and technology risk for early-stage innovation projects.",
      "Construct a lean business model and MVP roadmap tied to user evidence.",
      "Pitch to diverse audiences using clear metrics and defensible assumptions.",
      "Identify governance, IP, and partnership issues common in university spinouts.",
    ],
    topics: [
      "Opportunity discovery and competitive landscaping",
      "Unit economics and pricing probes",
      "Pilot design with measurable success criteria",
      "Team roles in startup vs. corporate innovation contexts",
      "Responsible scaling and stakeholder alignment",
    ],
    pedagogy_type: "text",
  },
];

function main() {
  const db = getDb();
  const stmt = db.prepare(`
    INSERT INTO uw_courses (course_code, title, level, learning_outcomes, topics, pedagogy_type)
    VALUES (@course_code, @title, @level, @learning_outcomes, @topics, @pedagogy_type)
    ON CONFLICT(course_code) DO UPDATE SET
      title = excluded.title,
      level = excluded.level,
      learning_outcomes = excluded.learning_outcomes,
      topics = excluded.topics,
      pedagogy_type = excluded.pedagogy_type
  `);

  for (const c of GIX_COURSES) {
    stmt.run({
      course_code: c.course_code,
      title: c.title,
      level: c.level,
      learning_outcomes: JSON.stringify(c.learning_outcomes),
      topics: JSON.stringify(c.topics),
      pedagogy_type: c.pedagogy_type,
    });
  }

  console.log(`Seeded ${GIX_COURSES.length} UW courses.`);
}

main();
