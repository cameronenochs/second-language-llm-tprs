export type ThemeName = "light" | "dark";

export const THEME_KEY = "laminas-theme";

export const THEME_COLOR: Record<ThemeName, string> = {
  light: "#e8edf2",
  dark: "#12171e",
};

export function isThemeName(value: unknown): value is ThemeName {
  return value === "light" || value === "dark";
}

export function readTheme(storage: Pick<Storage, "getItem"> | null): ThemeName {
  if (!storage) return "light";
  try {
    const value = storage.getItem(THEME_KEY);
    return isThemeName(value) ? value : "light";
  } catch {
    return "light";
  }
}

export function writeTheme(storage: Pick<Storage, "setItem"> | null, theme: ThemeName) {
  if (!storage) return;
  try {
    storage.setItem(THEME_KEY, theme);
  } catch {
    /* private mode and disabled storage can throw */
  }
}

/** Runs before paint so a saved dark theme does not flash light. */
export const themeBootScript = `try{var t=localStorage.getItem("${THEME_KEY}");if(t==="dark")document.documentElement.setAttribute("data-theme","dark");}catch(e){}`;

let current: ThemeName = "light";
const listeners = new Set<() => void>();

function emit() {
  for (const listener of listeners) listener();
}

export function applyTheme(theme: ThemeName) {
  current = theme;
  document.documentElement.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", THEME_COLOR[theme]);
  emit();
}

export function subscribeTheme(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function currentTheme() {
  return current;
}
