"use client";

import { useEffect, useState } from "react";

import { speak } from "@/lib/speech";

import type { ExerciseProps } from "./types";
import { Card, KeyHint, type Tone } from "./parts";

type Side = "left" | "right";
type Flash = { left: string; right: string; ok: boolean };

/**
 * match_pairs ("Select the matching pairs"): tap an English tile and a Spanish tile. Every attempt is
 * graded by the server at once; a wrong pair flashes red (and costs a heart in a lesson), a right one
 * flashes green and fades out. Keys 1-5 pick on the left, 6-0 on the right.
 */
export function MatchPairsExercise({ exercise, locked, onPair }: ExerciseProps) {
  const left = exercise.pairs?.left ?? [];
  const right = exercise.pairs?.right ?? [];
  const [selected, setSelected] = useState<Record<Side, string | null>>({ left: null, right: null });
  const [matched, setMatched] = useState<string[]>([]);
  const [flash, setFlash] = useState<Flash | null>(null);
  const busy = locked || flash !== null;

  const tap = async (side: Side, text: string) => {
    if (busy || matched.includes(text)) return;
    if (side === "right") speak(text, "es");
    const next = { ...selected, [side]: selected[side] === text ? null : text };
    setSelected(next);
    if (!next.left || !next.right) return;

    const result = await onPair([next.left, next.right]);
    if (!result) return setSelected({ left: null, right: null });
    setFlash({ left: next.left, right: next.right, ok: result.correct });
    setTimeout(
      () => {
        if (result.correct) setMatched((done) => [...done, next.left!, next.right!]);
        setFlash(null);
        setSelected({ left: null, right: null });
      },
      result.correct ? 350 : 600,
    );
  };

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const digit = "1234567890".indexOf(event.key);
      if (digit < 0) return;
      if (digit < left.length) void tap("left", left[digit]);
      else if (digit >= 5 && digit - 5 < right.length) void tap("right", right[digit - 5]);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const toneOf = (side: Side, text: string): Tone => {
    if (matched.includes(text)) return "done";
    if (flash && flash[side] === text) return flash.ok ? "right" : "wrong";
    return selected[side] === text ? "selected" : "idle";
  };

  const column = (side: Side, texts: string[], firstKey: number) => (
    <div className="flex flex-col gap-2.5">
      {texts.map((text, index) => {
        const tone = toneOf(side, text);
        return (
          <Card
            key={text}
            tone={tone}
            disabled={busy && tone !== "done"}
            aria-pressed={tone === "selected"}
            onClick={() => void tap(side, text)}
            className="flex h-[56px] items-center gap-3 px-4 disabled:opacity-100 sm:h-[52px]"
          >
            <KeyHint label={String((firstKey + index) % 10)} tone={tone} />
            <span className="flex-1 text-center">{text}</span>
            <span className="hidden w-[30px] sm:block" />
          </Card>
        );
      })}
    </div>
  );

  return (
    <div className="grid grid-cols-2 gap-4 sm:mx-[30px] sm:gap-[30px]">
      {column("left", left, 1)}
      {column("right", right, 6)}
    </div>
  );
}
