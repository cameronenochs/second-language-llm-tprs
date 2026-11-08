import { useLayoutEffect, useSyncExternalStore, type ReactNode } from "react";
import {
  applyTheme,
  currentTheme,
  readTheme,
  subscribeTheme,
  writeTheme,
  type ThemeName,
} from "@/lesson/theme";

export function ThemeBoot() {
  useLayoutEffect(() => {
    applyTheme(readTheme(window.localStorage));
  }, []);
  return null;
}

export function ThemeToggle() {
  const theme = useSyncExternalStore(subscribeTheme, currentTheme, () => "light" as ThemeName);
  const dark = theme === "dark";

  return (
    <button
      type="button"
      aria-pressed={dark}
      onClick={() => {
        const next: ThemeName = dark ? "light" : "dark";
        writeTheme(window.localStorage, next);
        applyTheme(next);
      }}
      className="inline-flex h-11 shrink-0 items-center justify-center rounded-full border border-rule bg-plate px-4 font-sans text-sm font-semibold text-ink"
    >
      {dark ? "Light" : "Dark"}
    </button>
  );
}

export function TopBar({ children }: { children?: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <div className="min-w-0">{children}</div>
      <ThemeToggle />
    </div>
  );
}
