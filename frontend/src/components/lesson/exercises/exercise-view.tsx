import { RotateCcw } from "lucide-react";
import type { ComponentType } from "react";

import type { ExerciseType } from "@/lib/api/types";

import { ChoiceExercise } from "./choice-exercise";
import { MatchPairsExercise } from "./match-pairs-exercise";
import { TypeAnswerExercise } from "./type-answer-exercise";
import type { ExerciseProps } from "./types";
import { WordBankExercise } from "./word-bank-exercise";

/** Which view plays which exercise type. A new type needs a view here and nothing else in the player. */
const VIEWS: Record<ExerciseType, ComponentType<ExerciseProps>> = {
  multiple_choice: ChoiceExercise,
  fill_blank: ChoiceExercise,
  word_bank: WordBankExercise,
  listen: WordBankExercise,
  type_answer: TypeAnswerExercise,
  match_pairs: MatchPairsExercise,
};

/** One exercise: its badge, its instruction ("Write this in English") and the view for its type. */
export function ExerciseView({ retry, ...props }: ExerciseProps & { retry: boolean }) {
  const View = VIEWS[props.exercise.type];
  return (
    <div className="w-full">
      {retry && (
        <p className="mb-2 flex items-center gap-2 text-[15px] font-bold tracking-[0.5px] text-duo-orange uppercase">
          <span className="flex size-6 items-center justify-center rounded-full bg-duo-orange text-white">
            <RotateCcw className="size-3.5" strokeWidth={3.5} />
          </span>
          Previous mistake
        </p>
      )}
      <h1 className="mb-6 text-[24px] leading-tight font-bold text-ink-strong sm:mb-8 sm:text-[32px] sm:leading-10">
        {props.exercise.instruction}
      </h1>
      <View {...props} />
    </div>
  );
}
