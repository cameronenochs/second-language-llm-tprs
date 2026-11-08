import assert from "node:assert/strict";
import test from "node:test";
import { getLevel, getStep, isPlayable, LEVELS, levelNote, withManifests } from "./course.ts";
import { isRevealMode, readReveal, writeReveal } from "./reveal.ts";

test("level 1 lesson 1 is the only playable step", () => {
  const level = getLevel("1");
  assert.ok(level);
  assert.equal(levelNote(level), "1 of 3 ready");
  const lesson = getStep(level, "1");
  assert.ok(lesson);
  assert.equal(isPlayable(lesson), true);
  assert.equal(lesson.rounds.length, 20);
  assert.equal(isPlayable(getStep(level, "2")!), false);
});

test("later levels are selectable and empty", () => {
  const level = getLevel("2");
  assert.ok(level);
  assert.equal(level.steps.length, 0);
  assert.equal(levelNote(level), "No steps yet");
  assert.equal(getLevel("missing"), undefined);
});

test("reveal mode ignores unknown stored values", () => {
  const saved = new Map<string, string>();
  const storage = {
    getItem: (key: string) => saved.get(key) ?? null,
    setItem: (key: string, value: string) => {
      saved.set(key, value);
    },
  };
  assert.equal(readReveal(storage), "together");
  assert.equal(isRevealMode("nope"), false);
  writeReveal(storage, "delayed");
  assert.equal(readReveal(storage), "delayed");
  saved.set("laminas-reveal", "picture");
  assert.equal(readReveal(storage), "together");
});

test("exported lessons join their level and bad manifests are skipped", () => {
  const plates = [
    { image: "/a.png", audio: "/a.mp3" },
    { image: "/b.png", audio: "/b.mp3" },
  ];
  const levels = withManifests(LEVELS, [
    { language: "latin", level: "1", lesson: 1, plates, rounds: [0, 1, 0] },
    { language: "latin", level: "1", lesson: 2, plates, rounds: [0, 5] },
  ]);
  const level = getLevel("1", levels)!;
  assert.equal(level.steps.length, 4);
  const step = getStep(level, "latin-1")!;
  assert.equal(step.title, "Latin · Lesson 1");
  assert.equal(isPlayable(step), true);
  assert.equal(getStep(level, "latin-2"), undefined);
  assert.equal(getLevel("1")!.steps.length, 3);
});
