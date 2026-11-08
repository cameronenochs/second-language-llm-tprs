import type { RevealMode } from "@/lesson/reveal";

const OPTIONS: { id: RevealMode; title: string; body: string }[] = [
  {
    id: "together",
    title: "Picture stays",
    body: "You see the picture, then you hear it.",
  },
  {
    id: "delayed",
    title: "Listen first",
    body: "You hear it once. Then the picture appears.",
  },
];

export function ModePicker({
  value,
  onChange,
}: {
  value: RevealMode;
  onChange: (mode: RevealMode) => void;
}) {
  return (
    <div className="grid gap-3" role="radiogroup" aria-label="When the picture appears">
      {OPTIONS.map((option) => {
        const selected = value === option.id;
        return (
          <button
            key={option.id}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onChange(option.id)}
            className={
              selected
                ? "rounded-plate border-2 border-accent bg-plate px-5 py-4 text-left"
                : "rounded-plate border-2 border-rule bg-plate px-5 py-4 text-left hover:border-ink"
            }
          >
            <span className="block font-sans text-base font-semibold text-ink">{option.title}</span>
            <span className="mt-1 block text-base leading-relaxed text-muted">{option.body}</span>
          </button>
        );
      })}
    </div>
  );
}
