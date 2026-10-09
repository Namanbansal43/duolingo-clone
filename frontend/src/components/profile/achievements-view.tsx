"use client";

import { AchievementBadge } from "@/components/achievements/achievement-badge";
import { PageError } from "@/components/app/page-error";
import { ProgressBar } from "@/components/ui/progress-bar";
import { getAchievements, getMe } from "@/lib/api/endpoints";
import type { Achievement } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";

import { GuestProfile } from "./guest-profile";

async function loadAchievements() {
  const [me, achievements] = await Promise.all([getMe(), getAchievements()]);
  return { isGuest: me.is_guest, achievements };
}

/**
 * /profile/achievements ("View all"): every achievement with its level and progress towards the next.
 * A guest has no profile yet, so they are asked to create one, as on /profile.
 */
export function AchievementsView() {
  const page = useApi(loadAchievements);

  if (page.status === "error") return <PageError message={page.error.message} onRetry={page.retry} />;
  if (page.status === "success" && page.data.isGuest) {
    return (
      <main className="mx-auto max-w-[592px] md:pt-6">
        <GuestProfile />
      </main>
    );
  }
  return (
    <main className="mx-auto max-w-[654px] px-4 pt-6 pb-12 md:pt-[70px]">
      {page.status === "loading" ? (
        <div aria-busy className="mt-[42px] h-[548px] animate-pulse rounded-2xl bg-snow" />
      ) : (
        <>
          <h1 className="text-[24px] leading-[26px] font-bold text-ink-strong">Achievements</h1>
          <ul className="mt-4 rounded-2xl border-2 border-line">
            {page.data.achievements.map((achievement) => (
              <AchievementRow key={achievement.key} achievement={achievement} />
            ))}
          </ul>
        </>
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
