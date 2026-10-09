"use client";

import { Clock } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

import { PageColumns } from "@/components/app/page-columns";
import { PageError } from "@/components/app/page-error";
import { RailCard, RightRail } from "@/components/app/right-rail";
import { buttonClasses } from "@/components/ui/button";
import { getMe } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/use-api";
import { appNow } from "@/lib/clock";

import { DailyQuest } from "./daily-quest";

/**
 * /quests, laid out like duolingo.com's Quests page. The brief asks for a daily goal indicator, so the one
 * quest is the learner's daily goal ("Earn 20 XP"), filled by today's XP and refreshed at midnight in their
 * time zone. Further quests and monthly challenges show as "unlock soon", as duolingo.com shows them to a
 * new learner.
 */
export function QuestsView() {
  const page = useApi(getMe);

  if (page.status === "loading") return <QuestsSkeleton />;
  if (page.status === "error") return <PageError message={page.error.message} onRetry={page.retry} />;

  const me = page.data;
  return (
    <PageColumns
      me={me}
      rail={
        <RightRail me={me}>
          <MonthlyChallengeCard />
        </RightRail>
      }
    >
      <div className="px-4 pt-4 pb-12 md:px-0 lg:pt-0">
        <section className="relative flex min-h-[200px] items-center overflow-hidden rounded-2xl bg-quest-banner p-6 sm:min-h-[232px]">
          <div className="max-w-[340px] text-white max-sm:max-w-[60%]">
            <h1 className="text-[25px] leading-[34px] font-bold">Welcome!</h1>
            <p className="mt-2 text-[17px] leading-6 font-medium">
              Complete quests to earn rewards! Quests refresh every day.
            </p>
          </div>
          <Image
            src="/app/quests/welcome.svg"
            width={172}
            height={184}
            alt=""
            priority
            className="absolute right-6 w-[120px] sm:w-[172px]"
          />
        </section>

        <div className="mt-[30px] flex items-center justify-between">
          <h2 className="text-[25px] leading-7 font-bold text-ink">Daily Quests</h2>
          <p className="flex items-center gap-1.5 text-[17px] leading-5 font-bold text-duo-orange uppercase">
            <Clock className="size-5" strokeWidth={3} aria-hidden />
            <span className="sr-only">Time left: </span>
            {untilMidnight(me.timezone)}
          </p>
        </div>

        <div className="mt-3 rounded-2xl border-2 border-line px-[25px] py-5">
          <DailyQuest xp={me.xp_today} goal={me.daily_goal_xp} size="page" />
        </div>

        <div className="mt-4 flex h-[100px] items-center gap-[22px] rounded-2xl border-2 border-line bg-snow px-[18px]">
          <Image src="/app/quests/locked.svg" width={60} height={60} alt="" className="size-[60px] shrink-0" />
          <p className="text-[19px] leading-7 font-bold text-ink-faint">More quests unlock soon</p>
        </div>
      </div>
    </PageColumns>
  );
}

/** duolingo.com's rail card for a learner whose monthly challenges haven't started. */
function MonthlyChallengeCard() {
  return (
    <RailCard className="pt-[26px]">
      <div className="flex gap-2">
        <div className="min-w-0 flex-1">
          <h2 className="text-[17px] leading-7 font-bold text-ink-strong">Monthly challenges unlock soon!</h2>
          <p className="mt-2 text-[17px] leading-6 font-medium text-ink-soft">
            Complete each month&rsquo;s challenge to earn exclusive badges
          </p>
        </div>
        <Image src="/app/quests/monthly-challenge.svg" width={116} height={138} alt="" className="-mr-[18px] h-[138px] w-[116px] shrink-0" />
      </div>
      <Link
        href="/learn"
        className={buttonClasses({ variant: "outline", fullWidth: true, className: "mt-7 h-[50px] rounded-2xl text-[15px] tracking-[0.8px]" })}
      >
        Start a lesson
      </Link>
    </RailCard>
  );
}

/** Time left until the daily quest refreshes at midnight in the learner's time zone: "12 hours", "40 minutes". */
function untilMidnight(timezone: string): string {
  const parts = new Intl.DateTimeFormat("en-US", { timeZone: timezone, hour: "numeric", minute: "numeric", hourCycle: "h23" })
    .formatToParts(new Date(appNow()));
  const part = (type: string) => Number(parts.find((p) => p.type === type)?.value ?? 0);
  const minutes = 24 * 60 - (part("hour") * 60 + part("minute"));
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60);
    return `${hours} ${hours === 1 ? "hour" : "hours"}`;
  }
  return `${minutes} ${minutes === 1 ? "minute" : "minutes"}`;
}

function QuestsSkeleton() {
  return (
    <div aria-busy className="mx-auto flex max-w-[1056px] gap-12 px-4 pt-[58px] md:px-6 lg:pt-6">
      <div className="mx-auto w-full max-w-[592px] lg:mx-0">
        <div className="h-[232px] animate-pulse rounded-2xl bg-snow" />
        <div className="mt-[30px] h-7 w-44 animate-pulse rounded-lg bg-snow" />
        <div className="mt-3 h-[113px] animate-pulse rounded-2xl bg-snow" />
      </div>
      <div className="hidden w-[368px] shrink-0 flex-col gap-6 lg:flex">
        <div className="h-11 animate-pulse rounded-xl bg-snow" />
        <div className="h-[254px] animate-pulse rounded-2xl bg-snow" />
      </div>
    </div>
  );
}
