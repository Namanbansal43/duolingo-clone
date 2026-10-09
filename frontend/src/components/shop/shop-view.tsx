"use client";

import Image from "next/image";
import { useState } from "react";
import { toast } from "sonner";

import { CreateProfileCard } from "@/components/app/create-profile";
import { PageColumns } from "@/components/app/page-columns";
import { PageError } from "@/components/app/page-error";
import { DailyQuestCard, RightRail } from "@/components/app/right-rail";
import { LeagueCard } from "@/components/leaderboard/league-card";
import { Button } from "@/components/ui/button";
import { getLeaderboard, getMe, refillHearts } from "@/lib/api/endpoints";
import type { Me } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";
import { comingSoon } from "@/lib/coming-soon";
import { cn } from "@/lib/cn";

// Matches HEART_REFILL_GEMS in backend/app/services/rules.py, which decides the real price.
const REFILL_PRICE = 350;

async function loadShop() {
  const [me, board] = await Promise.all([getMe(), getLeaderboard()]);
  return { me, board };
}

/**
 * /shop, laid out like duolingo.com's. Gems are mocked, as the brief allows: they come from the starting
 * balance and treasure chests, never from money. The one thing to buy is the brief's mocked heart refill.
 * Like duolingo.com, a guest is asked to create a profile before spending.
 */
export function ShopView() {
  const page = useApi(loadShop);

  if (page.status === "loading") return <ShopSkeleton />;
  if (page.status === "error") return <PageError message={page.error.message} onRetry={page.retry} />;

  const { me, board } = page.data;
  return (
    <PageColumns
      me={me}
      rail={
        <RightRail me={me}>
          <LeagueCard board={board} />
          <DailyQuestCard xp={me.xp_today} goal={me.daily_goal_xp} />
          {me.is_guest && <CreateProfileCard />}
        </RightRail>
      }
    >
      <div className="relative px-4 pt-4 pb-12 md:px-0">
        <div aria-hidden={me.is_guest} className={cn(me.is_guest && "pointer-events-none opacity-20")}>
          <section>
            <h2 className="text-[24px] leading-[26px] font-bold text-ink-strong">Hearts</h2>
            <ul className="mt-[25px]">
              <li className="flex items-start gap-[10px] border-t-2 border-line py-[17px]">
                <Image src="/app/shop/refill-hearts.svg" width={100} height={100} alt="" className="size-20 shrink-0 sm:size-[100px]" />
                <div className="min-w-0 flex-1 pt-[5px]">
                  <h3 className="text-[19px] leading-5 font-bold text-ink-strong">Refill Hearts</h3>
                  <p className="mt-4 text-[17px] leading-[29.75px] font-medium text-ink-soft">
                    Get full hearts so you can worry less about making mistakes in a lesson
                  </p>
                </div>
                <RefillButton me={me} onRefilled={page.refresh} />
              </li>
            </ul>
          </section>
        </div>
        {me.is_guest && <GuestOverlay gems={me.gems} />}
      </div>
    </PageColumns>
  );
}

function RefillButton({ me, onRefilled }: { me: Me; onRefilled: () => Promise<void> }) {
  const [buying, setBuying] = useState(false);
  const full = me.hearts.current >= me.hearts.max;
  const buy = async () => {
    setBuying(true);
    try {
      await refillHearts();
      await onRefilled();
      toast("Your hearts are full again!");
    } catch (error) {
      toast(error instanceof Error ? error.message : "Couldn't refill your hearts. Please try again.");
    } finally {
      setBuying(false);
    }
  };
  return (
    <Button
      variant="outline"
      disabled={full || buying || me.gems < REFILL_PRICE}
      onClick={() => void buy()}
      className={cn(
        "mt-[5px] h-[50px] shrink-0 rounded-2xl px-4 text-[15px] tracking-[0.8px]",
        // Disabled stays an outlined button with greyed text, as on duolingo.com.
        "disabled:translate-y-0 disabled:bg-page disabled:text-line disabled:shadow-[0_2px_0_var(--color-line)]",
      )}
    >
      {full ? (
        "Full"
      ) : (
        <>
          <span className="max-sm:hidden">Get for:</span>
          <Image src="/app/stats/gem.svg" width={22} height={28} alt="gems" className="h-[26px] w-6 object-contain" />
          {REFILL_PRICE}
        </>
      )}
    </Button>
  );
}

/** duolingo.com's prompt over the shop for a guest, whose gems can't be spent until they have a profile. */
function GuestOverlay({ gems }: { gems: number }) {
  return (
    <div className="absolute inset-x-4 top-4 flex flex-col items-center bg-linear-to-b from-page via-page/80 to-page/30 pt-8 pb-10 text-center md:inset-x-0">
      <p className="max-w-[460px] text-[24px] leading-8 font-medium text-ink-strong sm:text-[28px] sm:leading-9">
        You earned {gems} gems! Create a profile to spend them in the store!
      </p>
      <Button
        size="lg"
        onClick={() => comingSoon("Creating a profile")}
        className="mt-10 w-full max-w-[320px] rounded-2xl text-[15px] tracking-[0.8px]"
      >
        Create a profile
      </Button>
    </div>
  );
}

function ShopSkeleton() {
  return (
    <div aria-busy className="mx-auto flex max-w-[1056px] gap-12 px-4 pt-[58px] md:px-6 lg:pt-6">
      <div className="mx-auto w-full max-w-[592px] lg:mx-0">
        <div className="mt-4 h-7 w-32 animate-pulse rounded-lg bg-snow" />
        <div className="mt-8 h-[120px] animate-pulse rounded-2xl bg-snow" />
      </div>
      <div className="hidden w-[368px] shrink-0 flex-col gap-6 lg:flex">
        <div className="h-11 animate-pulse rounded-xl bg-snow" />
        <div className="h-[175px] animate-pulse rounded-2xl bg-snow" />
      </div>
    </div>
  );
}
