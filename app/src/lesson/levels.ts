import { getLevel as find, LEVELS as BASE, withManifests, type Manifest } from "./course";

// Vite inlines every exported lesson at build time; an empty folder gives no extra steps.
const manifests = Object.values(
  import.meta.glob<Manifest>("./content/*.json", { eager: true, import: "default" }),
);

export const LEVELS = withManifests(BASE, manifests);

export function getLevel(id: string) {
  return find(id, LEVELS);
}
