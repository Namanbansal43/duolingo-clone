"use client";

import { AchievementBadge } from "@/components/achievements/achievement-badge";
import { PageError } from "@/components/app/page-error";
import { ProgressBar } from "@/components/ui/progress-bar";
import { getAchievements } from "@/lib/api/endpoints";
import type { Achievement } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";

/** /profile/achievements ("View all"): every achievement with its level and progress towards the next. */
export function AchievementsView() {
  const achievements = useApi(getAchievements);

  if (achievements.status === "error") {
    return <PageError message={achievements.error.message} onRetry={achievements.retry} />;
  }
  return (
    <main className="mx-auto max-w-[654px] px-4 pt-6 pb-12 md:pt-[70px]">
      <h1 className="text-[24px] leading-[26px] font-bold text-ink-strong">Achievements</h1>
      {achievements.status === "loading" ? (
        <div aria-busy className="mt-4 h-[548px] animate-pulse rounded-2xl bg-snow" />
      ) : (
        <ul className="mt-4 rounded-2xl border-2 border-line">
          {achievements.data.map((achievement) => (
            <AchievementRow key={achievement.key} achievement={achievement} />
          ))}
        </ul>
      )}
    </main>
  );
}

function AchievementRow({ achievement }: { achievement: Achievement }) {
  const shown = Math.min(achievement.value, achievement.goal);
  return (
    <li className="flex gap-5 border-b-2 border-line p-4 last:border-b-0 sm:gap-[30px] sm:px-5 sm:py-5">
      <AchievementBadge achievement={achievement} className="w-[64px] sm:w-[77px]" />
      <div className="flex min-w-0 flex-1 flex-col justify-center">
        <div className="flex justify-between gap-3">
          <h2 className="mb-1.5 truncate text-[19px] leading-[1.5] font-bold text-ink-strong">{achievement.title}</h2>
          <p className="text-[17px] text-ink-faint">
            {shown}/{achievement.goal}
          </p>
        </div>
        <ProgressBar value={shown / achievement.goal} label={`${achievement.title} progress`} tone="gold" />
        <p className="mt-2.5 text-[17px] leading-5 font-medium text-ink-soft">{achievement.description}</p>
      </div>
    </li>
  );
}
