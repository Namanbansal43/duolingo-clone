"use client";

import Image from "next/image";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import type { WeekResult } from "@/lib/api/types";

import { leagueBadge, leagueTitle } from "./league-art";

/**
 * How last week's league ended, in duolingo.com's words ("You finished #3 and advanced to the Silver
 * League"). Shown once per week: the browser remembers which result was seen.
 */
export function WeekResultModal({ result }: { result: WeekResult }) {
  const key = `league-result-seen:${result.week_start}`;
  const [open, setOpen] = useState(() => !readFlag(key));

  if (!open) return null;
  const close = () => {
    writeFlag(key);
    setOpen(false);
  };
  return (
    <Modal label="Last week's league" onClose={close}>
      <Image src={leagueBadge(result.next_league)} width={80} height={91} alt="" className="mx-auto h-[91px] w-20" />
      <h2 className="mt-5 text-[24px] leading-8 font-bold text-ink-strong">{message(result)}</h2>
      <Button variant="secondary" size="lg" fullWidth onClick={close} autoFocus className="mt-6">
        Continue
      </Button>
    </Modal>
  );
}

function message({ rank, outcome, league, next_league: next }: WeekResult): string {
  switch (outcome) {
    case "promoted":
      return `You finished #${rank} and advanced to the ${leagueTitle(next)}`;
    case "demoted":
      return `You finished #${rank} and dropped down to the ${leagueTitle(next)}`;
    case "stayed":
      return `You finished #${rank} and kept your position in the ${leagueTitle(league)}`;
  }
}

// The flag is only a convenience: without storage (private windows) the result simply shows again.
function readFlag(key: string): boolean {
  try {
    return window.localStorage.getItem(key) === "1";
  } catch {
    return false;
  }
}

function writeFlag(key: string): void {
  try {
    window.localStorage.setItem(key, "1");
  } catch {
    // storage unavailable: nothing to remember
  }
}
