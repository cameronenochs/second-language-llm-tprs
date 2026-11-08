import { Link, createFileRoute } from "@tanstack/react-router";
import { ChevronRight } from "lucide-react";
import { TopBar } from "@/components/theme-toggle";
import { levelNote } from "@/lesson/course";
import { LEVELS } from "@/lesson/levels";

export const Route = createFileRoute("/")({ component: LevelsPage });

function LevelsPage() {
  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-xl flex-col px-5 py-12 sm:py-16">
      <TopBar>
        <p className="font-sans text-sm tracking-wide text-muted">Spanish</p>
      </TopBar>
      <h1 className="mt-3 font-display text-6xl leading-none text-ink">Láminas</h1>
      <p className="mt-5 max-w-md text-lg leading-relaxed text-ink">
        Pick a level, then a step. Each step plays pictures with the speech that
        goes with them. Nothing on the page translates it.
      </p>
      <ul className="mt-10 flex flex-col gap-3">
        {LEVELS.map((level) => (
          <li key={level.id}>
            <Link
              to="/levels/$levelId"
              params={{ levelId: level.id }}
              className="flex items-center justify-between gap-4 rounded-plate border border-rule bg-plate px-5 py-5 hover:border-ink"
            >
              <span>
                <span className="block font-display text-3xl leading-none text-ink">
                  {level.title}
                </span>
                <span className="mt-2 block text-base text-ink">{level.summary}</span>
                <span className="mt-1 block font-sans text-sm text-muted">{levelNote(level)}</span>
              </span>
              <ChevronRight aria-hidden="true" className="size-5 shrink-0 text-muted" />
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-auto pt-16 font-sans text-sm text-muted">
        In the comprehension tradition of Harris Winitz.
      </p>
    </main>
  );
}
