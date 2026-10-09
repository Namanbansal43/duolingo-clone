import Image from "next/image";

import type { League } from "@/lib/api/types";
import { cn } from "@/lib/cn";

import { leagueBadge } from "./league-art";

// duolingo.com: the current league's badge is 80 x 91 and centred; the others are 52 x 58, 28px apart.
const SMALL = 52;
const GAP = 28;

/**
 * The row of league badges across the top of the leaderboard, centred on the learner's league. Leagues
 * already passed show their badge, leagues above are locked. With `current` null (leaderboards locked) every
 * badge is locked.
 */
export function LeagueStrip({ leagues, current }: { leagues: League[]; current: League | null }) {
  const position = current?.position ?? 1;
  const index = leagues.findIndex((league) => league.position === position);
  return (
    <div className="relative h-[91px] overflow-hidden" aria-hidden>
      <div
        className="absolute top-0 left-1/2 flex h-full items-center"
        style={{ gap: GAP, transform: `translateX(-${index * (SMALL + GAP) + 40}px)` }}
      >
        {leagues.map((league) => {
          const isCurrent = league.position === position;
          const reached = current !== null && league.position <= position;
          return (
            <Image
              key={league.id}
              src={reached ? leagueBadge(league) : "/app/leagues/locked.svg"}
              width={isCurrent ? 80 : SMALL}
              height={isCurrent ? 91 : 58}
              alt=""
              className={cn("shrink-0", isCurrent ? "h-[91px] w-20" : "h-[58px] w-[52px]")}
            />
          );
        })}
      </div>
    </div>
  );
}
