import { Link, createFileRoute } from "@tanstack/react-router";
import { ChevronRight } from "lucide-react";
import { TopBar } from "@/components/theme-toggle";
import { isPlayable } from "@/lesson/course";
import { getLevel } from "@/lesson/levels";

export const Route = createFileRoute("/levels/$levelId/")({ component: StepsPage });

function StepsPage() {
  const { levelId } = Route.useParams();
  const level = getLevel(levelId);

  if (!level) {
    return (
      <main className="mx-auto flex min-h-dvh w-full max-w-xl flex-col px-5 py-10">
        <TopBar />
        <h1 className="mt-8 font-display text-5xl text-ink">That level is not in the course.</h1>
        <Link to="/" className="mt-8 inline-flex h-12 items-center font-sans text-base font-semibold text-accent">
          All levels
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-xl flex-col px-5 py-10 sm:py-14">
      <TopBar>
        <Link
          to="/"
          className="inline-flex h-11 w-fit items-center font-sans text-sm font-semibold text-muted"
        >
          Levels
        </Link>
      </TopBar>
      <h1 className="mt-3 font-display text-5xl leading-none text-ink">{level.title}</h1>
      <p className="mt-4 text-lg leading-relaxed text-ink">{level.summary}</p>
      {level.steps.length === 0 ? (
        <p className="mt-10 text-lg leading-relaxed text-muted">No steps in this level yet.</p>
      ) : (
        <ul className="mt-10 flex flex-col gap-3">
          {level.steps.map((step, index) => (
            <li key={step.id}>
              <Link
                to="/levels/$levelId/steps/$stepId"
                params={{ levelId: level.id, stepId: step.id }}
                className="flex items-center justify-between gap-4 rounded-plate border border-rule bg-plate px-5 py-5 hover:border-ink"
              >
                <span>
                  <span className="block font-sans text-sm text-muted">Step {index + 1}</span>
                  <span className="mt-1 block font-display text-3xl leading-none text-ink">
                    {step.title}
                  </span>
                  <span className="mt-2 block text-base text-muted">
                    {isPlayable(step) ? step.detail : "No pictures yet"}
                  </span>
                </span>
                <ChevronRight aria-hidden="true" className="size-5 shrink-0 text-muted" />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
