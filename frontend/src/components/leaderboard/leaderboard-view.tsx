"use client";

import { ArrowDown, ArrowUp, Clock } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { Fragment } from "react";

import { PageColumns } from "@/components/app/page-columns";
import { PageError } from "@/components/app/page-error";
import { RightRail } from "@/components/app/right-rail";
import { buttonClasses } from "@/components/ui/button";
import { getLeaderboard, getMe } from "@/lib/api/endpoints";
import type { League, Leaderboard, Me, Standing } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";
import { cn } from "@/lib/cn";

import { leagueTitle } from "./league-art";
import { LeagueStrip } from "./league-strip";
import { LetterAvatar } from "./letter-avatar";
import { WeekResultModal } from "./week-result-modal";

async function loadLeaderboard() {
  const [me, board] = await Promise.all([getMe(), getLeaderboard()]);
  return { me, board };
}

/**
 * /leaderboard: this week's league, laid out like duolingo.com's. Before the learner joins (leaderboards
 * locked, or no lesson yet this week) the list is a grey placeholder with START A LESSON.
 */
export function LeaderboardView() {
  const page = useApi(loadLeaderboard);

  if (page.status === "loading") return <LeaderboardSkeleton />;
  if (page.status === "error") return <PageError message={page.error.message} onRetry={page.retry} />;

  const { me, board } = page.data;
  return (
    <PageColumns me={me} rail={<RightRail me={me} />}>
      <div className="px-4 pb-12 md:px-0">
        <header className="pt-4 text-center lg:pt-0">
          <LeagueStrip leagues={board.leagues} current={board.league} />
          <h1 className="mt-6 text-[25px] leading-5 font-bold text-ink-strong">
            {board.league ? leagueTitle(board.league) : "Unlock Leaderboards!"}
          </h1>
          <Subtitle board={board} />
        </header>

        {board.joined && board.league ? (
          <Standings league={board.league} standings={board.standings} />
        ) : (
          <NotJoined me={me} showOwnRow={board.unlocked} />
        )}
      </div>
      {board.last_result && <WeekResultModal result={board.last_result} />}
    </PageColumns>
  );
}

function Subtitle({ board }: { board: Leaderboard }) {
  if (!board.unlocked) {
    const lessons = board.lessons_to_unlock;
    return <StartLesson text={`Complete ${lessons} more ${lessons === 1 ? "lesson" : "lessons"} to start competing`} />;
  }
  if (!board.joined) return <StartLesson text="Complete a lesson to join this week's leaderboard" />;
  const league = board.league;
  return (
    <>
      {league && league.promotion_count > 0 && (
        <p className="mt-5 text-[19px] leading-5 font-medium text-ink-soft">
          Top {league.promotion_count} advance to the next league
        </p>
      )}
      <p className="mt-3 flex items-center justify-center gap-1.5 text-[17px] font-bold text-duo-gold">
        <Clock className="size-5" strokeWidth={3} aria-hidden />
        {timeLeft(board.week_ends_at)}
      </p>
    </>
  );
}

function StartLesson({ text }: { text: string }) {
  return (
    <>
      <p className="mt-5 text-[19px] leading-5 font-medium text-ink-soft">{text}</p>
      <Link
        href="/learn"
        className={buttonClasses({
          variant: "outline",
          className: "mt-5 h-12 w-64 rounded-2xl text-[15px] tracking-[0.8px]",
        })}
      >
        Start a lesson
      </Link>
    </>
  );
}

/** Everyone in the league, with the promotion and demotion zones marked between the rows. */
function Standings({ league, standings }: { league: League; standings: Standing[] }) {
  const demotedFrom = standings.length - league.demotion_count + 1;
  return (
    <ol className="mt-6 border-t-2 border-line pt-4" aria-label={`${leagueTitle(league)} standings`}>
      {standings.map((row) => {
        const promoted = row.rank <= league.promotion_count;
        const demoted = league.demotion_count > 0 && row.rank >= demotedFrom;
        return (
          <Fragment key={row.user_id}>
            {league.demotion_count > 0 && row.rank === demotedFrom && <ZoneDivider kind="demotion" />}
            <li
              aria-current={row.is_me ? "true" : undefined}
              className={cn("flex h-[72px] items-center rounded-2xl pr-[34px] pl-[30px]", row.is_me && "bg-snow")}
            >
              <Rank rank={row.rank} tone={promoted ? "promoted" : demoted ? "demoted" : "neutral"} />
              <span className="ml-3">
                <LetterAvatar id={row.user_id} name={row.display_name} />
              </span>
              <span className="ml-4 min-w-0 flex-1 truncate text-[17px] font-bold text-ink">{row.display_name}</span>
              <span className="shrink-0 text-[17px] text-ink-soft">{row.xp} XP</span>
            </li>
            {row.rank === league.promotion_count && row.rank < standings.length && <ZoneDivider kind="promotion" />}
          </Fragment>
        );
      })}
    </ol>
  );
}

function Rank({ rank, tone }: { rank: number; tone: "promoted" | "demoted" | "neutral" }) {
  if (rank <= 3) {
    return (
      <span className="flex w-[41px] shrink-0 justify-center">
        <Image src={`/app/leagues/medal-${rank}.svg`} width={41} height={42} alt={`${rank}`} className="size-8" />
      </span>
    );
  }
  return (
    <span
      className={cn(
        "w-[41px] shrink-0 text-center text-[17px] font-bold",
        tone === "promoted" ? "text-duo-green" : tone === "demoted" ? "text-duo-red" : "text-ink",
      )}
    >
      {rank}
    </span>
  );
}

function ZoneDivider({ kind }: { kind: "promotion" | "demotion" }) {
  const Arrow = kind === "promotion" ? ArrowUp : ArrowDown;
  return (
    <li
      aria-hidden
      className={cn(
        "flex items-center justify-center gap-3 py-3 text-[15px] font-bold tracking-[0.8px] uppercase",
        kind === "promotion" ? "text-duo-green" : "text-duo-red",
      )}
    >
      <Arrow className="size-5" strokeWidth={3} />
      {kind === "promotion" ? "Promotion zone" : "Demotion zone"}
      <Arrow className="size-5" strokeWidth={3} />
    </li>
  );
}

/**
 * The grey placeholder list shown before the learner is in this week's league, and their own empty row,
 * pinned to the bottom of the screen as on duolingo.com (above the tab bar on phones).
 */
function NotJoined({ me, showOwnRow }: { me: Me; showOwnRow: boolean }) {
  return (
    <>
      <div aria-hidden className="relative mt-12 h-[480px] overflow-hidden">
        <Image src="/app/leagues/placeholder-ranks.svg" width={16} height={464} alt="" className="absolute top-0 left-7" />
        <Image src="/app/leagues/placeholder-learners.svg" width={208} height={480} alt="" className="absolute top-0 left-[68px]" />
        <Image src="/app/leagues/placeholder-xp.svg" width={48} height={462} alt="" className="absolute top-0 right-6" />
        <div className="absolute inset-x-0 bottom-0 h-40 bg-linear-to-b from-white/0 to-white" />
      </div>
      {showOwnRow && (
        <div className="sticky bottom-[94px] flex h-[72px] items-center rounded-2xl bg-snow pr-[34px] pl-[30px] text-ink-faint md:bottom-6">
          <span className="w-[41px] shrink-0 text-center text-[17px] font-bold">-</span>
          <span className="ml-3">
            <LetterAvatar id={me.id} name={me.display_name} dashed />
          </span>
          <span className="ml-auto text-[17px]">0 XP</span>
        </div>
      )}
    </>
  );
}

/** "6 days" until the league week ends, or hours on its last day. */
function timeLeft(endsAt: string): string {
  const hours = Math.max(0, (new Date(endsAt).getTime() - Date.now()) / 3_600_000);
  if (hours >= 24) {
    const days = Math.floor(hours / 24);
    return `${days} ${days === 1 ? "day" : "days"}`;
  }
  const whole = Math.max(1, Math.ceil(hours));
  return `${whole} ${whole === 1 ? "hour" : "hours"}`;
}

function LeaderboardSkeleton() {
  return (
    <div aria-busy className="mx-auto flex max-w-[1056px] gap-12 px-4 pt-[58px] md:px-6 lg:pt-6">
      <div className="mx-auto w-full max-w-[592px] lg:mx-0">
        <div className="mx-auto size-20 animate-pulse rounded-2xl bg-snow" />
        <div className="mx-auto mt-6 h-6 w-48 animate-pulse rounded-lg bg-snow" />
        <div className="mt-10 flex flex-col gap-2">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-[72px] animate-pulse rounded-2xl bg-snow" />
          ))}
        </div>
      </div>
      <div className="hidden w-[368px] shrink-0 flex-col gap-6 lg:flex">
        <div className="h-11 animate-pulse rounded-xl bg-snow" />
      </div>
    </div>
  );
}
