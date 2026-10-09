"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useReducer, useRef, useState } from "react";
import { toast } from "sonner";

import { OutOfHearts } from "@/components/app/out-of-hearts";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api/client";
import {
  answerExercise,
  completeSession,
  getCurrentSession,
  getMe,
  getPath,
  quitSession,
  startSession,
} from "@/lib/api/endpoints";
import type { AnswerBody, LessonSession } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";
import { playSound } from "@/lib/sounds";

import { AchievementUnlocked, LeaderboardUnlocked, LessonComplete, ReviewIntro, StreakExtended } from "./celebrations";
import { ExerciseView } from "./exercises/exercise-view";
import { CheckFooter, FeedbackBar } from "./lesson-footer";
import { LessonHeader } from "./lesson-header";
import { initialState, lessonReducer } from "./lesson-state";
import { QuitDialog } from "./quit-dialog";

/**
 * The full-screen lesson. It plays the learner's session in progress (started from the path), so a
 * refresh carries on where it was; with no session in progress it goes back to the path.
 */
export function LessonPlayer() {
  const router = useRouter();
  const current = useApi(useCallback(() => getCurrentSession(), []));
  const missing = current.status === "error" && current.error.code === "session_not_found";

  useEffect(() => {
    if (missing) router.replace("/learn");
  }, [missing, router]);

  if (current.status === "loading" || missing) return <LessonLoading />;
  if (current.status === "error") {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center gap-6 px-4 text-center">
        <p className="text-[19px] font-bold text-ink">{current.error.message}</p>
        <Button variant="secondary" size="lg" onClick={current.retry}>
          Try again
        </Button>
      </div>
    );
  }
  return <Lesson key={current.data.id} session={current.data} onReload={current.retry} />;
}

function Lesson({ session, onReload }: { session: LessonSession; onReload: () => void }) {
  const router = useRouter();
  const [state, dispatch] = useReducer(lessonReducer, session, initialState);
  const [answer, setAnswer] = useState<AnswerBody | null>(null);
  const [quitting, setQuitting] = useState(false);
  const completing = useRef(false);
  const exercise = session.exercises.find((e) => e.id === state.queue[0]);
  const { phase } = state;

  const leave = useCallback(() => router.push("/learn"), [router]);

  const submit = async (body: AnswerBody) => {
    if (!exercise) return;
    dispatch({ type: "check" });
    try {
      const result = await answerExercise(session.id, exercise.id, body);
      playSound(result.correct ? "correct" : "wrong");
      dispatch({ type: "answered", result });
    } catch (error) {
      dispatch({ type: "check-failed" });
      if (error instanceof ApiError && error.code === "out_of_hearts") {
        dispatch({ type: "hearts", hearts: { ...state.hearts, current: 0 } });
      } else {
        toast(error instanceof Error ? error.message : "Couldn't check that answer. Please try again.");
      }
    }
  };

  // match_pairs: each attempted pair is graded at once; the exercise is done when every pair is.
  const onPair = async (pair: [string, string]) => {
    if (!exercise) return null;
    try {
      const result = await answerExercise(session.id, exercise.id, { pair });
      if (result.exercise_completed) {
        playSound("correct");
        dispatch({ type: "answered", result });
      } else {
        if (!result.correct) playSound("wrong");
        dispatch({ type: "hearts", hearts: result.hearts });
      }
      return result;
    } catch (error) {
      toast(error instanceof Error ? error.message : "Couldn't check that pair. Please try again.");
      return null;
    }
  };

  const proceed = () => {
    setAnswer(null);
    dispatch({ type: "continue" });
  };

  const endSession = async () => {
    await quitSession(session.id).catch(() => {});
    leave();
  };

  // Quitting straight away loses nothing, so only a lesson with progress asks first.
  const hasProgress = state.completed > session.completed_exercise_ids.length || state.retried.length > 0;
  const quit = () => (hasProgress ? setQuitting(true) : void endSession());

  // Out of hearts: practice a finished node of the path to earn one back.
  const practice = async () => {
    await quitSession(session.id).catch(() => {});
    const me = await getMe();
    const path = me.active_course ? await getPath(me.active_course.id) : null;
    const node = path?.units
      .flatMap((unit) => unit.nodes)
      .filter((n) => n.state === "completed" && n.kind !== "chest")
      .at(-1);
    if (!node) {
      toast("Finish a lesson first; then you can practice it to earn hearts.");
      leave();
      return;
    }
    await startSession(node.id);
    onReload();
  };

  // Every exercise answered: the server completes the session (once, even under React's strict mode).
  useEffect(() => {
    if (phase !== "finishing" || completing.current) return;
    completing.current = true;
    completeSession(session.id).then(
      (result) => {
        playSound("complete");
        dispatch({ type: "finished", result });
      },
      (error: unknown) => {
        toast(error instanceof Error ? error.message : "Couldn't finish the lesson.");
        leave();
      },
    );
  }, [phase, session.id, leave]);

  // Enter checks, then continues, as on Duolingo. Footer and dialog buttons handle Enter themselves;
  // a focused choice or tile in the exercise doesn't (Enter there means "check", not "pick again").
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      const ownButton = target instanceof HTMLButtonElement && !target.closest("main");
      if (event.key !== "Enter" || quitting || ownButton) return;
      if (phase === "answer" && answer) {
        event.preventDefault();
        void submit(answer);
      } else if (phase === "feedback" || phase === "review") {
        event.preventDefault();
        proceed();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (phase === "ending" && state.result) {
    const [screen, ...later] = state.endings;
    const onContinue = () => (later.length > 0 ? dispatch({ type: "next-screen" }) : leave());
    switch (screen?.kind) {
      case "complete":
        return <LessonComplete result={state.result} onContinue={onContinue} />;
      case "streak":
        return <StreakExtended length={state.result.streak.length} onContinue={onContinue} />;
      case "leaderboard":
        return <LeaderboardUnlocked onContinue={onContinue} />;
      case "achievement":
        return <AchievementUnlocked key={screen.achievement.key} achievement={screen.achievement} onContinue={onContinue} />;
    }
  }
  if (phase === "finishing" || phase === "ending") return <LessonLoading />;

  return (
    <div className="flex min-h-svh flex-col">
      <LessonHeader progress={state.completed / state.total} combo={state.combo} hearts={state.hearts} onQuit={quit} />

      {phase === "review" ? (
        <ReviewIntro onContinue={proceed} />
      ) : (
        <>
          <main className="flex flex-1 justify-center px-4 py-6 sm:items-center sm:py-10">
            <div className="w-full max-w-[600px]">
              {exercise && (
                <ExerciseView
                  key={`${state.turn}-${exercise.id}`}
                  exercise={exercise}
                  retry={state.retried.includes(exercise.id)}
                  locked={phase !== "answer"}
                  feedback={state.feedback}
                  onAnswer={setAnswer}
                  onPair={onPair}
                />
              )}
            </div>
          </main>
          {phase === "feedback" && state.feedback ? (
            <FeedbackBar feedback={state.feedback} onContinue={proceed} />
          ) : (
            <CheckFooter
              canCheck={answer !== null}
              checking={phase === "checking"}
              onSkip={() => void submit({ skipped: true })}
              onCheck={() => answer && void submit(answer)}
              middle={
                exercise?.type === "listen" && (
                  <button
                    type="button"
                    onClick={() => {
                      setAnswer(null);
                      dispatch({ type: "skip-listening" });
                    }}
                    className="hidden rounded-xl px-3 py-2 text-[15px] font-bold tracking-[0.7px] text-ink-faint uppercase hover:bg-snow sm:block"
                  >
                    Can&rsquo;t listen now
                  </button>
                )
              }
            />
          )}
        </>
      )}

      {phase === "no-hearts" && (
        <OutOfHearts
          hearts={state.hearts}
          onRefilled={(me) => {
            setAnswer(null);
            dispatch({ type: "refilled", hearts: me.hearts });
          }}
          onPractice={practice}
          onNoThanks={endSession}
        />
      )}
      {quitting && <QuitDialog onStay={() => setQuitting(false)} onQuit={endSession} />}
    </div>
  );
}

function LessonLoading() {
  return (
    <div className="grid min-h-svh place-items-center" aria-busy="true" aria-label="Loading lesson">
      <Image src="/app/path/duo.svg" width={1080} height={1080} alt="" priority className="size-48 animate-pulse" />
    </div>
  );
}
