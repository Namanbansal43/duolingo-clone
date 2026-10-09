"use client";

import { useEffect, useState } from "react";

import { speak } from "@/lib/speech";

import type { ExerciseProps } from "./types";
import { Card, KeyHint, PromptBubble } from "./parts";

/**
 * multiple_choice ("Select the correct meaning") and fill_blank ("Fill in the blank"): a prompt and a
 * list of numbered choices. Number keys pick a choice, as on Duolingo.
 */
export function ChoiceExercise({ exercise, locked, feedback, onAnswer }: ExerciseProps) {
  const [chosen, setChosen] = useState<number | null>(null);
  const isBlank = exercise.type === "fill_blank";
  // The choices are in the other language from the prompt: Spanish when the prompt is English.
  const choicesInSpanish = isBlank || exercise.prompt_language !== "es";

  const choose = (id: number) => {
    if (locked) return;
    setChosen(id);
    onAnswer({ option_ids: [id] });
    const option = exercise.options.find((o) => o.id === id);
    if (option && choicesInSpanish) speak(option.text, "es");
  };

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (locked || event.target instanceof HTMLTextAreaElement) return;
      const option = exercise.options[Number(event.key) - 1];
      if (option) choose(option.id);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const toneOf = (id: number) => {
    if (id !== chosen) return "idle";
    if (feedback) return feedback.correct ? "right" : "wrong";
    return "selected";
  };
  const chosenText = exercise.options.find((o) => o.id === chosen)?.text;

  return (
    <div className="flex flex-col gap-6">
      {isBlank ? (
        <PromptBubble speakText={exercise.prompt?.replace("___", chosenText ?? "")} language="es">
          <BlankSentence sentence={exercise.prompt ?? ""} filled={chosenText} />
        </PromptBubble>
      ) : (
        <PromptBubble speakText={exercise.prompt ?? undefined} language={exercise.prompt_language}>
          {exercise.prompt}
        </PromptBubble>
      )}
      <div role="radiogroup" aria-label="Choices" className="flex flex-col gap-2">
        {exercise.options.map((option, index) => (
          <Card
            key={option.id}
            role="radio"
            aria-checked={option.id === chosen}
            tone={toneOf(option.id)}
            disabled={locked}
            onClick={() => choose(option.id)}
            className="flex min-h-[60px] items-center gap-4 px-4 py-2 text-left"
          >
            <KeyHint label={String(index + 1)} tone={toneOf(option.id)} />
            <span className="flex-1 text-center">{option.text}</span>
            <span className="hidden w-[30px] sm:block" />
          </Card>
        ))}
      </div>
    </div>
  );
}

/** "Me ___ Ana." with the gap drawn as a line, or filled with the chosen word. */
function BlankSentence({ sentence, filled }: { sentence: string; filled?: string }) {
  const [before, after] = sentence.split("___");
  return (
    <>
      {before}
      <span
        className={
          filled
            ? "border-b-2 border-duo-blue-border px-1 text-duo-blue-shade"
            : "inline-block w-16 border-b-2 border-ink-faint align-baseline"
        }
      >
        {filled ?? " "}
      </span>
      {after}
    </>
  );
}
