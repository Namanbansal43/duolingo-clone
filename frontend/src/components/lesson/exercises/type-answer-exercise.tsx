"use client";

import { useEffect, useRef, useState } from "react";

import { speak } from "@/lib/speech";

import type { ExerciseProps } from "./types";
import { PromptBubble } from "./parts";

// Keys for the letters an English keyboard lacks, shown under the box when the answer is Spanish.
const SPANISH_KEYS = ["á", "é", "í", "ó", "ú", "ü", "ñ", "¿", "¡"];

/** type_answer: translate the prompt by typing it. */
export function TypeAnswerExercise({ exercise, locked, onAnswer }: ExerciseProps) {
  const [text, setText] = useState("");
  const box = useRef<HTMLTextAreaElement>(null);
  const intoSpanish = exercise.prompt_language === "en";

  useEffect(() => {
    box.current?.focus();
    if (exercise.prompt_language === "es" && exercise.prompt) speak(exercise.prompt, "es");
  }, [exercise.prompt, exercise.prompt_language]);

  const update = (next: string) => {
    setText(next);
    onAnswer(next.trim() ? { text: next } : null);
  };

  // Accent keys type at the cursor, like the real keys would.
  const insert = (letter: string) => {
    const field = box.current;
    if (!field || locked) return;
    const { selectionStart: start, selectionEnd: end } = field;
    update(text.slice(0, start) + letter + text.slice(end));
    requestAnimationFrame(() => {
      field.focus();
      field.setSelectionRange(start + letter.length, start + letter.length);
    });
  };

  return (
    <div className="flex flex-col gap-6">
      <PromptBubble speakText={exercise.prompt ?? undefined} language={exercise.prompt_language}>
        {exercise.prompt}
      </PromptBubble>
      <div>
        <textarea
          ref={box}
          value={text}
          readOnly={locked}
          onChange={(event) => update(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) event.preventDefault(); // Enter checks instead
          }}
          placeholder={`Type in ${intoSpanish ? "Spanish" : "English"}`}
          aria-label="Your answer"
          autoCapitalize="off"
          autoComplete="off"
          spellCheck={false}
          className="block h-[155px] w-full resize-none rounded-[10px] border-2 border-line bg-snow px-3 py-2.5 text-[19px] leading-6 text-ink-strong outline-none placeholder:text-ink-faint"
        />
        {intoSpanish && (
          <div className="mt-3 flex flex-wrap gap-1">
            {SPANISH_KEYS.map((letter) => (
              <button
                key={letter}
                type="button"
                tabIndex={-1}
                onClick={() => insert(letter)}
                className="h-8 min-w-8 rounded-lg border-2 border-line px-2 text-[15px] font-bold text-ink-faint hover:bg-snow"
              >
                {letter}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
