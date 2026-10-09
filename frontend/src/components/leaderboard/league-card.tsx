import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";

import { RailCard } from "@/components/app/right-rail";
import type { Leaderboard } from "@/lib/api/types";

import { leagueBadge, leagueTitle } from "./league-art";

/**
 * The right-rail league card on /learn: how many lessons until leaderboards open, then the learner's
 * league and rank this week.
 */
export function LeagueCard({ board }: { board: Leaderboard }) {
  if (!board.league) {
    const lessons = board.lessons_to_unlock;
    return (
      <RailCard>
        <h2 className="text-[19px] leading-7 font-bold text-ink">Unlock Leaderboards!</h2>
        <CardBody image="/app/cards/league-locked.svg" wide>
          <p className="text-[17px] leading-[25px] font-medium text-ink-soft">
            Complete {lessons} more {lessons === 1 ? "lesson" : "lessons"} to start competing
          </p>
        </CardBody>
      </RailCard>
    );
  }

  const me = board.standings.find((row) => row.is_me);
  return (
    <RailCard>
      <div className="flex items-center justify-between">
        <h2 className="text-[19px] leading-7 font-bold text-ink">{leagueTitle(board.league)}</h2>
        <Link
          href="/leaderboard"
          className="text-[15px] leading-[18px] font-bold tracking-[0.8px] text-duo-blue uppercase hover:brightness-110"
        >
          View league
        </Link>
      </div>
      <CardBody image={leagueBadge(board.league)}>
        {me ? (
          <>
            <p className="text-[17px] leading-6 font-bold text-ink">You&rsquo;re ranked #{me.rank}</p>
            <p className="text-[15px] leading-5 text-ink-soft">You&rsquo;ve earned {me.xp} XP this week so far</p>
          </>
        ) : (
          <p className="text-[17px] leading-[25px] font-medium text-ink-soft">
            Complete a lesson to join this week&rsquo;s leaderboard
          </p>
        )}
      </CardBody>
    </RailCard>
  );
}

function CardBody({ image, wide = false, children }: { image: string; wide?: boolean; children: ReactNode }) {
  return (
    <div className="mt-7 flex items-center gap-3 pb-1">
      <Image
        src={image}
        width={wide ? 70 : 44}
        height={50}
        alt=""
        className={wide ? "h-[50px] w-[70px] shrink-0 object-contain" : "h-[50px] w-11 shrink-0 object-contain"}
      />
      <div className="pl-2">{children}</div>
    </div>
  );
}
