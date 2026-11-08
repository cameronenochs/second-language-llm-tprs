import { Pause, Play } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { TopBar } from "@/components/theme-toggle";
import { LOOK_MS, PAUSE_MS, type Plate } from "@/lesson/course";
import type { RevealMode } from "@/lesson/reveal";

type LessonViewProps = {
  audio: HTMLAudioElement;
  run: number;
  title: string;
  plates: readonly Plate[];
  rounds: readonly number[];
  reveal: RevealMode;
  onBack: () => void;
  onRepeat: () => void;
};

function cancelError() {
  return new DOMException("cancelled", "AbortError");
}

function isCancel(err: unknown) {
  return err instanceof DOMException && err.name === "AbortError";
}

function isBlocked(err: unknown) {
  if (!(err instanceof Error)) return false;
  return err.name === "NotAllowedError" || err.message.includes("NotAllowed");
}

export function LessonView({
  audio,
  run,
  title,
  plates,
  rounds,
  reveal,
  onBack,
  onRepeat,
}: LessonViewProps) {
  const [index, setIndex] = useState(0);
  const [hearing, setHearing] = useState<0 | 1 | 2>(0);
  const [speaking, setSpeaking] = useState(false);
  const [covered, setCovered] = useState(reveal === "delayed");
  const [done, setDone] = useState(false);
  const [needsTap, setNeedsTap] = useState(false);
  const [failed, setFailed] = useState(false);
  const [held, setHeld] = useState(false);
  const [jumpId, setJumpId] = useState(0);
  const tapRef = useRef<(() => void) | null>(null);
  const toggleRef = useRef<(() => void) | null>(null);
  const startRef = useRef(0);

  useEffect(() => {
    startRef.current = 0;
  }, [run]);

  function goTo(at: number) {
    audio.pause();
    startRef.current = at;
    setDone(false);
    setFailed(false);
    setHeld(false);
    setCovered(reveal === "delayed");
    setJumpId((n) => n + 1);
  }

  useEffect(() => {
    let userPaused = false;
    const resumeResolvers: Array<() => void> = [];
    let activeSleep: { freeze: () => void; thaw: () => void } | null = null;
    let playback: { freeze: () => void; thaw: () => void } | null = null;

    let cancelReject: (err: unknown) => void = () => {};
    const cancelled = new Promise<never>((_, reject) => {
      cancelReject = reject;
    });
    const until = <T,>(promise: Promise<T>) => Promise.race([promise, cancelled]);
    const timers = new Set<number>();
    const detachers: Array<() => void> = [];
    const from = startRef.current;

    const gate = () => {
      if (!userPaused) return Promise.resolve();
      return new Promise<void>((resolve) => {
        resumeResolvers.push(resolve);
      });
    };

    const pauseLesson = () => {
      if (userPaused) return;
      userPaused = true;
      setHeld(true);
      activeSleep?.freeze();
      if (playback) {
        playback.freeze();
        audio.pause();
      }
    };

    const playLesson = () => {
      if (!userPaused) return;
      userPaused = false;
      setHeld(false);
      activeSleep?.thaw();
      playback?.thaw();
      const waiting = resumeResolvers.splice(0);
      for (const resume of waiting) resume();
    };

    toggleRef.current = () => {
      if (userPaused) playLesson();
      else pauseLesson();
    };

    const sleep = (ms: number) =>
      gate().then(
        () =>
          new Promise<void>((resolve) => {
            let left = ms;
            const arm = () => {
              const started = Date.now();
              const id = window.setTimeout(() => {
                timers.delete(id);
                activeSleep = null;
                resolve();
              }, Math.max(0, left));
              timers.add(id);
              activeSleep = {
                freeze: () => {
                  window.clearTimeout(id);
                  timers.delete(id);
                  left -= Date.now() - started;
                },
                thaw: () => arm(),
              };
            };
            arm();
          }),
      );

    const load = async (src: string) => {
      const abs = new URL(src, window.location.href).href;
      if (audio.src !== abs) {
        audio.src = src;
        audio.load();
      }
      if (audio.readyState >= HTMLMediaElement.HAVE_FUTURE_DATA) return;
      await new Promise<void>((resolve, reject) => {
        const ok = () => {
          cleanup();
          resolve();
        };
        const bad = () => {
          cleanup();
          reject(new Error("audio"));
        };
        const cleanup = () => {
          audio.removeEventListener("canplay", ok);
          audio.removeEventListener("error", bad);
        };
        audio.addEventListener("canplay", ok);
        audio.addEventListener("error", bad);
      });
    };

    const playOnce = () =>
      gate().then(
        () =>
          new Promise<void>((resolve, reject) => {
            let settled = false;
            const finish = () => {
              if (settled) return;
              settled = true;
              cleanup();
              resolve();
            };
            const fail = (err: unknown) => {
              if (settled) return;
              settled = true;
              cleanup();
              reject(err instanceof Error ? err : new Error("audio"));
            };
            const onEnd = () => finish();
            const onErr = () => fail(new Error("audio"));
            let safety = 0;
            let safetyLeft = 8000;
            const armSafety = () => {
              const started = Date.now();
              safety = window.setTimeout(finish, Math.max(0, safetyLeft));
              timers.add(safety);
              playback = {
                freeze: () => {
                  window.clearTimeout(safety);
                  timers.delete(safety);
                  safetyLeft -= Date.now() - started;
                },
                thaw: () => {
                  armSafety();
                  audio.play().catch((err: unknown) => {
                    if (
                      userPaused &&
                      err instanceof DOMException &&
                      err.name === "AbortError"
                    ) {
                      return;
                    }
                    fail(err);
                  });
                },
              };
            };
            const cleanup = () => {
              detach();
              window.clearTimeout(safety);
              timers.delete(safety);
              if (playback) playback = null;
            };
            const detach = () => {
              audio.removeEventListener("ended", onEnd);
              audio.removeEventListener("error", onErr);
            };
            detachers.push(detach);
            const startAudio = () => {
              audio.play().catch((err: unknown) => {
                if (
                  userPaused &&
                  err instanceof DOMException &&
                  err.name === "AbortError"
                ) {
                  return;
                }
                fail(err);
              });
            };
            audio.addEventListener("ended", onEnd);
            audio.addEventListener("error", onErr);
            try {
              audio.currentTime = 0;
            } catch {
              /* seek can throw before metadata; play still starts at 0 */
            }
            armSafety();
            startAudio();
          }),
      );

    const say = async (src: string, which: 1 | 2) => {
      await gate();
      await load(src);
      setSpeaking(true);
      setHearing(which);
      try {
        await playOnce();
      } catch (err) {
        if (!isBlocked(err)) throw err;
        audio.pause();
        setSpeaking(false);
        setNeedsTap(true);
        await until(
          new Promise<void>((resolve) => {
            tapRef.current = () => {
              tapRef.current = null;
              setNeedsTap(false);
              resolve();
            };
          }),
        );
        setSpeaking(true);
        await playOnce();
      }
      setSpeaking(false);
    };

    setHeld(false);

    (async () => {
      try {
        setDone(false);
        setFailed(false);
        setNeedsTap(false);
        setHearing(0);
        setSpeaking(false);
        for (let i = from; i < rounds.length; i++) {
          setIndex(i);
          setHearing(0);
          setSpeaking(false);
          const plate = plates[rounds[i]];
          const delayed = reveal === "delayed";
          setCovered(delayed);
          if (!delayed) await until(sleep(LOOK_MS));
          await until(say(plate.audio, 1));
          if (delayed) {
            setCovered(false);
            await until(sleep(LOOK_MS));
          }
          await until(sleep(PAUSE_MS));
          await until(say(plate.audio, 2));
          await until(sleep(PAUSE_MS));
        }
        setDone(true);
        setSpeaking(false);
      } catch (err) {
        if (isCancel(err)) return;
        setSpeaking(false);
        setFailed(true);
      }
    })();

    return () => {
      toggleRef.current = null;
      cancelReject(cancelError());
      for (const id of timers) window.clearTimeout(id);
      for (const detach of detachers) detach();
      audio.pause();
      tapRef.current = null;
    };
  }, [audio, plates, reveal, rounds, run, jumpId]);

  const round = index + 1;
  const status = held
    ? "Paused"
    : speaking
      ? covered
        ? "Listen"
        : hearing === 1
          ? "First hearing"
          : "Again"
      : covered
        ? "Listen"
        : hearing === 0
          ? "Look"
          : "Silence";

  if (done) {
    return (
      <main className="mx-auto flex min-h-dvh w-full max-w-xl flex-col px-5 py-5">
        <TopBar />
        <div className="flex flex-1 flex-col justify-center">
        <p className="font-sans text-sm tracking-wide text-muted">{title}</p>
        <h1 className="mt-2 font-display text-5xl leading-tight text-ink">Finished.</h1>
        <p className="mt-4 max-w-md text-lg leading-relaxed text-ink">
          {rounds.length} rounds. Each picture came back spaced between the others,
          rather than drilled in a row.
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={onRepeat}
            className="inline-flex h-12 items-center justify-center rounded-full bg-accent px-6 font-sans text-base font-semibold text-accent-ink hover:bg-accent-deep"
          >
            Play again
          </button>
          <button
            type="button"
            onClick={onBack}
            className="inline-flex h-12 items-center justify-center rounded-full border border-rule bg-plate px-6 font-sans text-base font-semibold text-ink"
          >
            Back to steps
          </button>
        </div>
        <div className="mt-10">
          <p className="mb-2 font-sans text-sm text-muted">Jump to a round</p>
          <RoundJump total={rounds.length} current={rounds.length} onPick={goTo} />
        </div>
        </div>
      </main>
    );
  }

  const plate = plates[rounds[index]];

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-3xl flex-col px-5 py-5">
      <header>
        <TopBar>
          <button
            type="button"
            onClick={onBack}
            className="inline-flex h-11 items-center font-sans text-sm font-semibold text-muted"
          >
            Steps
          </button>
        </TopBar>
        <div className="mt-2 flex items-center justify-between gap-3">
          <p className="font-sans text-sm text-muted">
            {reveal === "delayed" ? "Listen first" : "Picture stays"}
          </p>
          <p className="font-sans text-sm tabular-nums text-ink">
            {round} <span className="text-muted">/ {rounds.length}</span>
          </p>
        </div>
      </header>

      <div className="plate relative mt-4 flex min-h-64 flex-1 items-center justify-center overflow-hidden">
        {covered || !plate ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-5 bg-paper px-6 text-center">
            <span className={speaking && !held ? "bars is-on" : "bars"} aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
            <p className="font-display text-4xl text-ink">Listen</p>
          </div>
        ) : (
          <img
            key={`${run}-${jumpId}-${index}`}
            src={plate.image}
            alt=""
            className="plate-in h-full max-h-[62dvh] w-full object-contain p-6"
          />
        )}
        {needsTap ? (
          <div className="absolute inset-0 flex items-center justify-center bg-plate/95">
            <button
              type="button"
              onClick={() => tapRef.current?.()}
              className="inline-flex h-12 items-center justify-center rounded-full bg-accent px-6 font-sans text-base font-semibold text-accent-ink hover:bg-accent-deep"
            >
              Tap to hear
            </button>
          </div>
        ) : null}
      </div>

      <footer className="mt-5 flex flex-col gap-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3" aria-live="polite">
            <span className={speaking && !held ? "bars is-on" : "bars"} aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
            <p className="font-sans text-sm text-muted">
              {failed ? "The recording didn’t play." : status}
            </p>
          </div>
          {failed ? null : (
            <button
              type="button"
              onClick={() => toggleRef.current?.()}
              disabled={needsTap}
              aria-pressed={held}
              className="inline-flex h-11 items-center gap-2 rounded-full border border-rule bg-plate px-4 font-sans text-sm font-semibold text-ink disabled:opacity-50"
            >
              {held ? <Play aria-hidden="true" className="size-4" /> : <Pause aria-hidden="true" className="size-4" />}
              {held ? "Play" : "Pause"}
            </button>
          )}
        </div>
        {failed ? (
          <button
            type="button"
            onClick={onRepeat}
            className="inline-flex h-12 w-fit items-center justify-center rounded-full bg-accent px-6 font-sans text-base font-semibold text-accent-ink hover:bg-accent-deep"
          >
            Try again
          </button>
        ) : (
          <div className="flex flex-col gap-2">
            <p className="font-sans text-sm text-muted">Jump to a round</p>
            <RoundJump total={rounds.length} current={index} onPick={goTo} />
          </div>
        )}
      </footer>
    </main>
  );
}

function RoundJump({
  total,
  current,
  onPick,
}: {
  total: number;
  current: number;
  onPick: (index: number) => void;
}) {
  return (
    <div className="grid grid-cols-5 gap-1 sm:grid-cols-10">
      {Array.from({ length: total }, (_, i) => {
        const place = i < current ? "past" : i === current ? "current" : "future";
        return (
          <button
            key={i}
            type="button"
            aria-label={`Round ${i + 1}`}
            aria-current={place === "current" ? "step" : undefined}
            onClick={() => onPick(i)}
            className={
              place === "current"
                ? "h-11 rounded-md bg-accent font-sans text-xs font-semibold text-accent-ink"
                : place === "past"
                  ? "h-11 rounded-md bg-mark font-sans text-xs font-semibold text-mark-ink"
                  : "h-11 rounded-md border border-rule bg-plate font-sans text-xs font-semibold text-muted"
            }
          >
            {i + 1}
          </button>
        );
      })}
    </div>
  );
}
