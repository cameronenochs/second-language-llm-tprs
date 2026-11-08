/** Five Level-1 plates. Filenames stay opaque so the page never prints the Spanish. */
export const PLATES = [
  { image: "/lesson/plate-1.jpg", audio: "/audio/plate-1.mp3" },
  { image: "/lesson/plate-2.jpg", audio: "/audio/plate-2.mp3" },
  { image: "/lesson/plate-3.jpg", audio: "/audio/plate-3.mp3" },
  { image: "/lesson/plate-4.jpg", audio: "/audio/plate-4.mp3" },
  { image: "/lesson/plate-5.jpg", audio: "/audio/plate-5.mp3" },
] as const;

/**
 * Twenty rounds. Each of the five plates appears four times.
 * No plate is heard twice in a row. Returns are spaced (distributed),
 * and the order changes across the lesson so it is not one loop repeated.
 *
 * Gaps between repeats: plate 1 → 6,4,6 · 2 → 4,7,7 · 3 → 6,6,4 · 4 → 6,4,4 · 5 → 3,4,4.
 */
export const ROUND_ORDER = [
  0, 1, 2, 3, 4, 1, 0, 4, 2, 3, 0, 4, 1, 3, 2, 4, 0, 3, 2, 1,
] as const;

export const PAUSE_MS = 3000;
export const LOOK_MS = 700;

export type Plate = { image: string; audio: string };

export type Step = {
  id: string;
  title: string;
  detail: string;
  plates: readonly Plate[];
  rounds: readonly number[];
};

export type Level = {
  id: string;
  title: string;
  summary: string;
  steps: readonly Step[];
};

const EMPTY = "No pictures yet";

/** A lesson written by `scripts/export_course.py` into `src/lesson/content/`. */
export type Manifest = {
  language: string;
  level: string;
  lesson: number;
  plates: readonly Plate[];
  rounds: readonly number[];
};

export const LEVELS: readonly Level[] = [
  {
    id: "1",
    title: "Level 1",
    summary: "Single words",
    steps: [
      {
        id: "1",
        title: "Lesson 1",
        detail: "Five pictures, heard four times each",
        plates: PLATES,
        rounds: ROUND_ORDER,
      },
      {
        id: "2",
        title: "Lesson 2",
        detail: EMPTY,
        plates: [],
        rounds: [],
      },
      {
        id: "3",
        title: "Lesson 3",
        detail: EMPTY,
        plates: [],
        rounds: [],
      },
    ],
  },
  {
    id: "2",
    title: "Level 2",
    summary: "Short phrases",
    steps: [],
  },
  {
    id: "3",
    title: "Level 3",
    summary: "Short scenes",
    steps: [],
  },
];

function isValidManifest(m: Manifest): boolean {
  return (
    m.plates.length > 0 &&
    m.rounds.length > 0 &&
    m.rounds.every((r) => Number.isInteger(r) && r >= 0 && r < m.plates.length)
  );
}

/** Append each generated lesson to its level as a step with id `<language>-<lesson>`. */
export function withManifests(levels: readonly Level[], manifests: readonly Manifest[]): Level[] {
  return levels.map((level) => {
    const extra = manifests
      .filter((m) => m.level === level.id && isValidManifest(m))
      .sort((a, b) => a.language.localeCompare(b.language) || a.lesson - b.lesson)
      .map((m) => ({
        id: `${m.language}-${m.lesson}`,
        title: `${m.language[0].toUpperCase()}${m.language.slice(1)} · Lesson ${m.lesson}`,
        detail: `${m.plates.length} pictures, ${m.rounds.length} rounds`,
        plates: m.plates,
        rounds: m.rounds,
      }));
    return { ...level, steps: [...level.steps, ...extra] };
  });
}

export function getLevel(id: string, levels: readonly Level[] = LEVELS): Level | undefined {
  return levels.find((level) => level.id === id);
}

export function getStep(level: Level, id: string): Step | undefined {
  return level.steps.find((step) => step.id === id);
}

export function isPlayable(step: Step): boolean {
  return step.plates.length > 0 && step.rounds.length > 0;
}

export function levelNote(level: Level): string {
  if (level.steps.length === 0) return "No steps yet";
  const ready = level.steps.filter(isPlayable).length;
  if (ready === 0) return "No pictures yet";
  return `${ready} of ${level.steps.length} ready`;
}
