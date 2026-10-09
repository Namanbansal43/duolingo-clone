import type { Achievement, AnswerResult, Completion, Hearts, LessonSession } from "@/lib/api/types";

/**
 * The lesson player as a state machine. The server grades answers and keeps score; this only decides
 * what the learner sees next. Exercises wait in a queue: a right answer removes the current one, a
 * wrong one sends it to the back, to come round again as a "previous mistake".
 */

export type Phase =
  | "answer" // working on the current exercise
  | "checking" // waiting for the server to grade it
  | "feedback" // the green or red bar is showing
  | "review" // "Let's review the exercise you missed!", before the mistakes come round again
  | "no-hearts" // out of hearts, in a lesson
  | "finishing" // every exercise answered; asking the server to complete the session
  | "ending"; // the result screens, one after another (see EndScreen)

/**
 * The screens after a finished lesson: always "Lesson complete!", then the streak celebration if today's
 * first lesson extended it, then one for each achievement that went up a level.
 */
export type EndScreen =
  | { kind: "complete" }
  | { kind: "streak" }
  | { kind: "achievement"; achievement: Achievement };

export type Feedback = {
  correct: boolean;
  heading: string;
  solution: string | null;
};

export type LessonState = {
  session: LessonSession;
  queue: number[]; // exercise ids still to answer; the first is on screen
  retried: number[]; // ids that came back after a mistake
  reviewShown: boolean;
  completed: number;
  total: number;
  combo: number; // right answers in a row
  turn: number; // increases whenever a new exercise appears, so its view starts afresh
  hearts: Hearts;
  phase: Phase;
  feedback: Feedback | null;
  result: Completion | null;
  endings: EndScreen[]; // result screens still to show; the first is on screen
};

export type LessonAction =
  | { type: "check" }
  | { type: "check-failed" }
  | { type: "answered"; result: AnswerResult }
  | { type: "hearts"; hearts: Hearts }
  | { type: "continue" }
  | { type: "skip-listening" }
  | { type: "refilled"; hearts: Hearts }
  | { type: "finished"; result: Completion }
  | { type: "next-screen" };

const PRAISE = ["Good job!", "Great job!", "Awesome!", "Nicely done!", "Amazing!", "Excellent!"];

export function initialState(session: LessonSession): LessonState {
  const done = new Set(session.completed_exercise_ids);
  const queue = session.exercises.map((e) => e.id).filter((id) => !done.has(id));
  const outOfHearts = session.mode === "lesson" && session.hearts.current === 0;
  return {
    session,
    queue,
    retried: [],
    reviewShown: false,
    completed: done.size,
    total: session.exercises.length,
    combo: 0,
    turn: 0,
    hearts: session.hearts,
    phase: queue.length === 0 ? "finishing" : outOfHearts ? "no-hearts" : "answer",
    feedback: null,
    result: null,
    endings: [],
  };
}

export function lessonReducer(state: LessonState, action: LessonAction): LessonState {
  switch (action.type) {
    case "check":
      return { ...state, phase: "checking" };
    case "check-failed":
      return { ...state, phase: "answer" };
    case "answered": {
      const { result } = action;
      return {
        ...state,
        phase: "feedback",
        hearts: result.hearts,
        combo: result.correct ? state.combo + 1 : 0,
        feedback: { correct: result.correct, heading: heading(result), solution: result.solution },
      };
    }
    case "hearts": {
      const outOfHearts = state.session.mode === "lesson" && action.hearts.current === 0;
      return { ...state, hearts: action.hearts, combo: 0, phase: outOfHearts ? "no-hearts" : state.phase };
    }
    case "continue":
      return state.phase === "feedback" ? afterFeedback(state) : { ...state, phase: "answer", turn: state.turn + 1 };
    case "skip-listening": {
      // "Can't listen now": every listening exercise left is dropped from this lesson.
      const listening = new Set(state.session.exercises.filter((e) => e.type === "listen").map((e) => e.id));
      const queue = state.queue.filter((id) => !listening.has(id));
      const dropped = state.queue.length - queue.length;
      return next({ ...state, queue, total: state.total - dropped });
    }
    case "refilled":
      return { ...state, hearts: action.hearts, phase: state.queue.length ? "answer" : "finishing" };
    case "finished":
      return { ...state, phase: "ending", result: action.result, endings: endScreens(action.result) };
    case "next-screen":
      return { ...state, endings: state.endings.slice(1) };
  }
}

function endScreens(result: Completion): EndScreen[] {
  return [
    { kind: "complete" },
    ...(result.streak.extended ? [{ kind: "streak" } as const] : []),
    ...result.achievements.map((achievement) => ({ kind: "achievement", achievement }) as const),
  ];
}

/** The current exercise is settled: right ones leave the queue, wrong ones go to the back. */
function afterFeedback(state: LessonState): LessonState {
  const [current, ...rest] = state.queue;
  if (state.feedback?.correct) {
    return next({ ...state, queue: rest, completed: state.completed + 1, feedback: null });
  }
  const retried = state.retried.includes(current) ? state.retried : [...state.retried, current];
  const moved = { ...state, queue: [...rest, current], retried, feedback: null };
  if (state.session.mode === "lesson" && state.hearts.current === 0) return { ...moved, phase: "no-hearts" };
  return next(moved);
}

/** What comes after the queue changed. */
function next(state: LessonState): LessonState {
  if (state.queue.length === 0) return { ...state, phase: "finishing" };
  const onlyMistakesLeft = state.queue.every((id) => state.retried.includes(id));
  if (onlyMistakesLeft && !state.reviewShown) return { ...state, phase: "review", reviewShown: true };
  return { ...state, phase: "answer", turn: state.turn + 1 };
}

function heading(result: AnswerResult): string {
  switch (result.verdict) {
    case "correct":
      return PRAISE[Math.floor(Math.random() * PRAISE.length)];
    case "other_solution":
      return "Another correct solution:";
    case "typo":
      return "You have a typo.";
    case "wrong":
      return result.solution === null ? "Incorrect" : "Correct solution:";
  }
}
