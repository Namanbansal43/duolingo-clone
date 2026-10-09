import type { League } from "@/lib/api/types";

/** Duolingo's badge for a league, in public/app/leagues ("bronze.svg" ... "diamond.svg"). */
export function leagueBadge(league: League): string {
  return `/app/leagues/${league.name.toLowerCase()}.svg`;
}

/** "Bronze League". */
export function leagueTitle(league: League): string {
  return `${league.name} League`;
}
