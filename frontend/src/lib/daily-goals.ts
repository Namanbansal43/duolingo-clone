import type { DailyGoalXp } from "@/lib/api/types";

/**
 * The four daily goals. Duolingo shows them in minutes but stores XP, with the same pairing
 * used here: 5 min = 10 XP, 10 min = 20 XP, 15 min = 30 XP, 20 min = 50 XP.
 */
export const DAILY_GOALS: { xp: DailyGoalXp; minutes: number; label: string }[] = [
  { xp: 10, minutes: 5, label: "Casual" },
  { xp: 20, minutes: 10, label: "Regular" },
  { xp: 30, minutes: 15, label: "Serious" },
  { xp: 50, minutes: 20, label: "Intense" },
];

export const dailyGoalFor = (xp: DailyGoalXp) => DAILY_GOALS.find((goal) => goal.xp === xp)!;
