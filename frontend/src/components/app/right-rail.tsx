import Image from "next/image";
import type { ReactNode } from "react";

import { ComingSoonLink } from "@/components/landing/coming-soon-link";
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
  const done = Math.min(xp, goal);
  return (
    <RailCard>
      <div className="flex items-center justify-between">
        <h2 className="text-[19px] leading-7 font-bold text-ink">Daily Quests</h2>
        <ComingSoonLink
          feature="Quests"
          className="text-[15px] leading-[18px] font-bold tracking-[0.8px] text-duo-blue uppercase hover:brightness-110"
        >
          View all
        </ComingSoonLink>
      </div>
      <div className="mt-6 flex items-center gap-[22px]">
        <Image src="/app/cards/quest-xp.svg" width={60} height={60} alt="" className="size-[60px] shrink-0 object-contain" />
        <div className="min-w-0 flex-1">
          <p className="text-[17px] leading-6 font-bold text-ink">Earn {goal} XP</p>
          <div className="mt-[14px] flex items-center">
            <div
              role="progressbar"
              aria-label="Daily goal"
              aria-valuemin={0}
              aria-valuemax={goal}
              aria-valuenow={done}
              className="relative h-[18px] flex-1 overflow-hidden rounded-l-[9px] bg-line"
            >
              <div className="h-full rounded-r-[9px] bg-duo-gold transition-[width] duration-500" style={{ width: `${(done / goal) * 100}%` }} />
              <span
                className={`absolute inset-0 flex items-center justify-center text-[14px] leading-[18px] font-bold tracking-[0.56px] ${done > 0 ? "text-duo-gold-shade" : "text-ink-faint"}`}
              >
                {done} / {goal}
              </span>
            </div>
            <Image src="/app/cards/quest-chest.svg" width={35} height={35} alt="" className="-ml-px size-[35px] shrink-0 object-contain pl-0.5" />
          </div>
        </div>
      </div>
    </RailCard>
  );
}
