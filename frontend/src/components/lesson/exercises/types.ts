import type { AnswerBody, AnswerResult, Exercise } from "@/lib/api/types";

import type { Feedback } from "../lesson-state";

/** What every exercise view gets from the lesson player. */
export type ExerciseProps = {
  exercise: Exercise;
  /** True while the answer is being checked and while the feedback bar shows: no more changes. */
  locked: boolean;
  feedback: Feedback | null;
  /** The answer so far; null while it isn't complete enough to check (CHECK stays grey). */
  onAnswer: (answer: AnswerBody | null) => void;
  /** match_pairs only: grade one attempted pair right away. Resolves to null if the request failed. */
  onPair: (pair: [string, string]) => Promise<AnswerResult | null>;
};
