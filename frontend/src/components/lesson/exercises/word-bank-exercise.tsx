"use client";

import { Turtle, Volume2 } from "lucide-react";
import { useEffect, useState } from "react";

import { cn } from "@/lib/cn";
import { canSpeak, speak } from "@/lib/speech";

import type { ExerciseProps } from "./types";
import { Card, PromptBubble } from "./parts";

/**
 * word_bank ("Write this in English") and listen ("Tap what you hear"): build the answer by tapping
 * tiles. Tapped tiles move up onto the answer lines and leave a grey gap behind; tapping one on the
 * lines sends it back.
 */
export function WordBankExercise({ exercise, locked, onAnswer }: ExerciseProps) {
  const [picked, setPicked] = useState<number[]>([]);
  const isListen = exercise.type === "listen";
  // Tiles are Spanish when the answer is Spanish: when listening, or translating from English.
  const tilesInSpanish = isListen || exercise.prompt_language === "en";
  const sentence = exercise.prompt ?? "";

  // Spanish sentences are read out as they appear.
  const readAloud = isListen || exercise.prompt_language === "es";
  useEffect(() => {
    if (readAloud) speak(sentence, "es");
  }, [readAloud, sentence]);

  const update = (next: number[]) => {
    setPicked(next);
    onAnswer(next.length ? { option_ids: next } : null);
  };
  const pick = (id: number) => {
    if (locked) return;
    update([...picked, id]);
    const tile = exercise.options.find((o) => o.id === id);
    if (tile && tilesInSpanish) speak(tile.text, "es");
  };
  const unpick = (id: number) => !locked && update(picked.filter((p) => p !== id));
  const textOf = (id: number) => exercise.options.find((o) => o.id === id)?.text ?? "";

  return (
    <div className="flex flex-col gap-6">
      {isListen ? (
        <ListenButtons sentence={sentence} />
      ) : (
        <PromptBubble speakText={sentence} language={exercise.prompt_language}>
          {sentence}
        </PromptBubble>
      )}

      {/* Two ruled lines the answer is built on. */}
      <div className="flex min-h-[124px] flex-wrap content-start gap-x-2 gap-y-2 bg-[linear-gradient(transparent_58px,var(--color-line)_58px,var(--color-line)_60px,transparent_60px)] bg-[length:100%_62px] px-1 pt-1.5">
        {picked.map((id) => (
          <Card key={id} disabled={locked} onClick={() => unpick(id)} className="h-[52px] px-4">
            {textOf(id)}
          </Card>
        ))}
      </div>

      <div className="flex flex-wrap justify-center gap-2">
        {exercise.options.map((tile) => {
          const used = picked.includes(tile.id);
          return used ? (
            // The gap a tapped tile leaves, the same size as the tile.
            <span key={tile.id} aria-hidden className="h-[50px] rounded-xl bg-line px-4 text-[19px] leading-[50px] text-transparent">
              {tile.text}
            </span>
          ) : (
            <Card key={tile.id} disabled={locked} onClick={() => pick(tile.id)} className={cn("h-[52px] px-4")}>
              {tile.text}
            </Card>
          );
        })}
      </div>
    </div>
  );
}

/** The big speaker (normal speed) and the turtle (slow) of "Tap what you hear". */
function ListenButtons({ sentence }: { sentence: string }) {
  if (!canSpeak()) {
    return <p className="text-center text-ink-soft">Audio isn&rsquo;t available in this browser.</p>;
  }
  return (
    <div className="flex items-end justify-center gap-4">
      <button
        type="button"
        aria-label="Play the sentence"
        onClick={() => speak(sentence, "es")}
        className="flex size-[120px] items-center justify-center rounded-3xl bg-duo-blue text-white shadow-[0_6px_0_var(--color-duo-blue-shade)] outline-none hover:brightness-105 focus-visible:ring-4 focus-visible:ring-duo-blue-border active:translate-y-[6px] active:shadow-none"
      >
        <Volume2 className="size-14" strokeWidth={2.5} fill="currentColor" />
      </button>
      <button
        type="button"
        aria-label="Play it slowly"
        onClick={() => speak(sentence, "es", { slow: true })}
        className="flex size-[80px] items-center justify-center rounded-2xl bg-duo-blue text-white shadow-[0_5px_0_var(--color-duo-blue-shade)] outline-none hover:brightness-105 focus-visible:ring-4 focus-visible:ring-duo-blue-border active:translate-y-[5px] active:shadow-none"
      >
        <Turtle className="size-9" strokeWidth={2.25} />
      </button>
    </div>
  );
}
