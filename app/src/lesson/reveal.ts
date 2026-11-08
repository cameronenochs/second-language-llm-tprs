export type RevealMode = "together" | "delayed";

const KEY = "laminas-reveal";

export function isRevealMode(value: unknown): value is RevealMode {
  return value === "together" || value === "delayed";
}

export function readReveal(storage: Pick<Storage, "getItem"> | null): RevealMode {
  if (!storage) return "together";
  try {
    const value = storage.getItem(KEY);
    return isRevealMode(value) ? value : "together";
  } catch {
    return "together";
  }
}

export function writeReveal(storage: Pick<Storage, "setItem"> | null, mode: RevealMode) {
  if (!storage) return;
  try {
    storage.setItem(KEY, mode);
  } catch {
    /* private mode and disabled storage can throw */
  }
}
