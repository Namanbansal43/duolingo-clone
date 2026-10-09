"use client";

import Image from "next/image";
import { useCallback, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { getMe, refillHearts } from "@/lib/api/endpoints";
import type { Hearts, Me } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";
import { appNow } from "@/lib/clock";

const REFILL_GEMS = 350; // HEART_REFILL_GEMS on the server

type OutOfHeartsProps = {
  hearts: Hearts;
  onRefilled: (me: Me) => void;
  /** Practice a finished node to earn a heart back; left out when there is nothing to practice yet. */
  onPractice?: () => Promise<void>;
  onNoThanks: () => void;
};

/** No hearts left: wait for one to come back, refill with gems, or practice to earn one. */
export function OutOfHearts({ hearts, onRefilled, onPractice, onNoThanks }: OutOfHeartsProps) {
  const me = useApi(useCallback(() => getMe(), []));
  const [busy, setBusy] = useState(false);
  const gems = me.status === "success" ? me.data.gems : null;

  const run = async (action: () => Promise<void>) => {
    setBusy(true);
    try {
      await action();
    } catch (error) {
      toast(error instanceof Error ? error.message : "Something went wrong. Please try again.");
      setBusy(false);
    }
  };

  return (
    <Modal label="Out of hearts">
      <Image
        src="/app/lesson/heart.svg"
        width={33}
        height={32}
        alt=""
        className="mx-auto h-[86px] w-[88px] opacity-40 grayscale"
      />
      <h2 className="mt-4 text-[24px] leading-8 font-bold text-ink">You ran out of hearts!</h2>
      <p className="mt-2 text-[17px] leading-6 text-ink-soft">
        {hearts.next_heart_at
          ? `Your next heart comes back in ${minutesUntil(hearts.next_heart_at)} min. Refill now or practice to earn one.`
          : "Refill now or practice to earn one."}
      </p>
      <div className="mt-6 flex flex-col gap-3">
        <Button
          variant="secondary"
          size="lg"
          fullWidth
          disabled={busy || (gems !== null && gems < REFILL_GEMS)}
          onClick={() => run(async () => onRefilled(await refillHearts()))}
        >
          Refill
          <Image src="/app/stats/gem.svg" width={24} height={30} alt="" className="ml-2 h-5 w-4" />
          {REFILL_GEMS}
        </Button>
        {onPractice && (
          <Button size="lg" fullWidth disabled={busy} onClick={() => run(onPractice)}>
            Practice to earn hearts
          </Button>
        )}
        <button
          type="button"
          onClick={onNoThanks}
          disabled={busy}
          className="w-full rounded-xl py-1.5 text-[15px] font-bold tracking-[0.7px] text-duo-blue uppercase hover:bg-snow"
        >
          No thanks
        </button>
      </div>
      {gems !== null && (
        <p className="mt-3 text-[13px] text-ink-faint">You have {gems} gems</p>
      )}
    </Modal>
  );
}

function minutesUntil(iso: string): number {
  return Math.max(1, Math.ceil((new Date(iso).getTime() - appNow()) / 60_000));
}
