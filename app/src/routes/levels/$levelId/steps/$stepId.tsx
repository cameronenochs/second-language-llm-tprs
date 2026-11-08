import { Link, createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { LessonView } from "@/components/lesson-view";
import { ModePicker } from "@/components/mode-picker";
import { TopBar } from "@/components/theme-toggle";
import { getStep, isPlayable } from "@/lesson/course";
import { getLevel } from "@/lesson/levels";
import { readReveal, writeReveal, type RevealMode } from "@/lesson/reveal";

export const Route = createFileRoute("/levels/$levelId/steps/$stepId")({
  component: StepPage,
});

function StepPage() {
  const { levelId, stepId } = Route.useParams();
  const level = getLevel(levelId);
  const step = level ? getStep(level, stepId) : undefined;
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [run, setRun] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [reveal, setReveal] = useState<RevealMode>("together");

  useEffect(() => {
    setReveal(readReveal(window.localStorage));
  }, []);

  useEffect(() => {
    if (!step || !isPlayable(step)) return;
    for (const plate of step.plates) {
      const clip = new Audio();
      clip.preload = "auto";
      clip.src = plate.audio;
      const img = new Image();
      img.src = plate.image;
    }
  }, [step]);

  if (!level || !step) {
    return (
      <main className="mx-auto flex min-h-dvh w-full max-w-xl flex-col px-5 py-10">
        <TopBar />
        <h1 className="mt-8 font-display text-5xl text-ink">That step is not in the course.</h1>
        <Link to="/" className="mt-8 inline-flex h-12 items-center font-sans text-base font-semibold text-accent">
          All levels
        </Link>
      </main>
    );
  }

  function choose(mode: RevealMode) {
    setReveal(mode);
    writeReveal(window.localStorage, mode);
  }

  function audioElement() {
    if (!audioRef.current) {
      const audio = new Audio();
      audio.preload = "auto";
      audioRef.current = audio;
    }
    return audioRef.current;
  }

  function begin() {
    const audio = audioElement();
    audio.src = step!.plates[step!.rounds[0]].audio;
    const pending = audio.play();
    const start = () => {
      audio.pause();
      try {
        audio.currentTime = 0;
      } catch {
        /* not seekable yet */
      }
      setRun((n) => n + 1);
      setPlaying(true);
    };
    if (pending) pending.then(start).catch(start);
    else start();
  }

  if (!isPlayable(step)) {
    return (
      <main className="mx-auto flex min-h-dvh w-full max-w-3xl flex-col px-5 py-5">
        <TopBar>
          <Link
            to="/levels/$levelId"
            params={{ levelId: level.id }}
            className="inline-flex h-11 w-fit items-center font-sans text-sm font-semibold text-muted"
          >
            Steps
          </Link>
        </TopBar>
        <h1 className="mt-4 font-display text-5xl leading-none text-ink">{step.title}</h1>
        <div className="plate mt-6 flex min-h-64 flex-1 items-center justify-center px-6 text-center">
          <p className="max-w-sm text-lg leading-relaxed text-ink">No pictures in this step yet.</p>
        </div>
      </main>
    );
  }

  if (playing && audioRef.current) {
    return (
      <LessonView
        audio={audioRef.current}
        run={run}
        title={step.title}
        plates={step.plates}
        rounds={step.rounds}
        reveal={reveal}
        onBack={() => setPlaying(false)}
        onRepeat={() => setRun((n) => n + 1)}
      />
    );
  }

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-xl flex-col px-5 py-10 sm:py-14">
      <TopBar>
        <Link
          to="/levels/$levelId"
          params={{ levelId: level.id }}
          className="inline-flex h-11 w-fit items-center font-sans text-sm font-semibold text-muted"
        >
          {level.title}
        </Link>
      </TopBar>
      <p className="mt-4 font-sans text-sm tracking-wide text-muted">{level.summary}</p>
      <h1 className="mt-2 font-display text-5xl leading-none text-ink">{step.title}</h1>
      <p className="mt-4 max-w-md text-lg leading-relaxed text-ink">{step.detail}</p>
      <div className="mt-8">
        <p className="mb-3 font-sans text-sm font-semibold text-muted">When the picture appears</p>
        <ModePicker value={reveal} onChange={choose} />
      </div>
      <button
        type="button"
        onClick={begin}
        className="mt-8 inline-flex h-12 w-fit items-center justify-center rounded-full bg-accent px-7 font-sans text-base font-semibold text-accent-ink hover:bg-accent-deep"
      >
        Begin
      </button>
      <p className="mt-6 max-w-md text-base leading-relaxed text-muted">
        Listen all the way through. Don’t say the words out loud.
      </p>
    </main>
  );
}
