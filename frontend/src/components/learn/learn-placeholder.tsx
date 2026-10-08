"use client";

import Link from "next/link";

import { Logo } from "@/components/brand/logo";
import { Flag } from "@/components/icons/flag";
import { Button, buttonClasses } from "@/components/ui/button";
import { getMe } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/use-api";
import { dailyGoalFor } from "@/lib/daily-goals";
import { isFlagCode } from "@/lib/languages";

/**
 * Temporary /learn page: confirms what the "Get started" flow saved, read back from the API.
 * The learning path replaces it.
 */
export function LearnPlaceholder() {
  const me = useApi(getMe);

  return (
    <main className="mx-auto flex min-h-svh max-w-[480px] flex-col items-center justify-center gap-8 px-4 text-center">
      <Logo />
      {me.status === "loading" && <p className="text-ink-soft">Loading...</p>}
      {me.status === "error" && (
        <>
          <p className="text-ink-soft">{me.error.message}</p>
          <Button variant="secondary" onClick={me.retry}>
            Try again
          </Button>
        </>
      )}
      {me.status === "success" && (
        <>
          <h1 className="text-[28px] font-bold text-ink">You&rsquo;re all set, {me.data.display_name}!</h1>
          <dl className="grid w-full grid-cols-[auto_1fr] gap-x-6 gap-y-3 rounded-2xl border-2 border-line p-5 text-left text-[17px]">
            <dt className="text-ink-soft">Course</dt>
            <dd className="flex items-center gap-2 font-bold text-ink">
              {me.data.active_course && isFlagCode(me.data.active_course.learning_language) && (
                <Flag code={me.data.active_course.learning_language} width={28} />
              )}
              {me.data.active_course?.title ?? "None yet"}
            </dd>
            <dt className="text-ink-soft">Daily goal</dt>
            <dd className="font-bold text-ink">
              {dailyGoalFor(me.data.daily_goal_xp).minutes} min / day &middot; {dailyGoalFor(me.data.daily_goal_xp).label}
            </dd>
            <dt className="text-ink-soft">Time zone</dt>
            <dd className="font-bold text-ink">{me.data.timezone}</dd>
          </dl>
          <p className="text-ink-soft">Your learning path is coming in the next step.</p>
          <Link href="/welcome" className={buttonClasses({ variant: "outline", size: "lg" })}>
            Change course or goal
          </Link>
        </>
      )}
    </main>
  );
}
