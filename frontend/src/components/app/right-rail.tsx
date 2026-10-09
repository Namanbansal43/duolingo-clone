import Link from "next/link";
import type { ReactNode } from "react";

import { ComingSoonLink } from "@/components/landing/coming-soon-link";
import { DailyQuest } from "@/components/quests/daily-quest";
import type { Me } from "@/lib/api/types";
import { cn } from "@/lib/cn";

import { StatsBar } from "./stats-bar";

const FOOTER_LINKS = ["About", "Blog", "Store", "Efficacy", "Careers", "Investors", "Terms", "Privacy"];

/** The right-hand column on wide screens: stats, the page's cards, footer links. */
export function RightRail({ me, children }: { me: Me; children?: ReactNode }) {
  return (
    <div className="flex flex-col gap-6">
      <StatsBar me={me} />
      {children}
      <ul className="flex flex-wrap justify-center gap-x-5 gap-y-4 px-2.5">
        {FOOTER_LINKS.map((label) => (
          <li key={label}>
            <ComingSoonLink
              feature={`The ${label} page`}
              className="text-[13px] leading-4 font-bold text-ink-faint uppercase hover:brightness-75"
            >
              {label}
            </ComingSoonLink>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function RailCard({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cn("rounded-2xl border-2 border-line p-[18px]", className)}>{children}</section>;
}

export function DailyQuestCard({ xp, goal }: { xp: number; goal: number }) {
  return (
    <RailCard>
      <div className="flex items-center justify-between">
        <h2 className="text-[19px] leading-7 font-bold text-ink">Daily Quests</h2>
        <Link
          href="/quests"
          className="text-[15px] leading-[18px] font-bold tracking-[0.8px] text-duo-blue uppercase hover:brightness-110"
        >
          View all
        </Link>
      </div>
      <div className="mt-6">
        <DailyQuest xp={xp} goal={goal} size="rail" />
      </div>
    </RailCard>
  );
}
