import assert from "node:assert/strict";
import test from "node:test";
import { isThemeName, readTheme, THEME_KEY, writeTheme } from "./theme.ts";

test("theme storage falls back to light", () => {
  const saved = new Map<string, string>();
  const storage = {
    getItem: (key: string) => saved.get(key) ?? null,
    setItem: (key: string, value: string) => {
      saved.set(key, value);
    },
  };
  assert.equal(readTheme(storage), "light");
  assert.equal(isThemeName("dim"), false);
  writeTheme(storage, "dark");
  assert.equal(saved.get(THEME_KEY), "dark");
  assert.equal(readTheme(storage), "dark");
  saved.set(THEME_KEY, "cream");
  assert.equal(readTheme(storage), "light");
});
