"use client";

import Link from "next/link";

import { CreateProfileCard } from "@/components/app/create-profile";
import { PageColumns } from "@/components/app/page-columns";
import { PageError } from "@/components/app/page-error";
import { DailyQuestCard, LeagueCard, RightRail } from "@/components/app/right-rail";
import { buttonClasses } from "@/components/ui/button";
import { getMe, getPath } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/use-api";

import { CoursePath } from "./course-path";

/** The learner and the path of their active course (the path needs the course id, so these load in turn). */
async function loadLearn() {
  const me = await getMe();
  const path = me.active_course ? await getPath(me.active_course.id) : null;
  return { me, path };
}

/** /learn: the learning path, with the leaderboard and daily quest cards in the right rail. */
export function LearnView() {
  const learn = useApi(loadLearn);

  if (learn.status === "loading") return <LearnSkeleton />;
  if (learn.status === "error") return <PageError message={learn.error.message} onRetry={learn.retry} />;

  const { me, path } = learn.data;
  return (
    <PageColumns
      me={me}
      rail={
        <RightRail me={me}>
          <LeagueCard lessonsCompleted={me.lessons_completed} />
          <DailyQuestCard xp={me.xp_today} goal={me.daily_goal_xp} />
          {me.is_guest && <CreateProfileCard />}
        </RightRail>
      }
    >
      {path ? (
        <CoursePath path={path} hearts={me.hearts} onChange={learn.refresh} />
      ) : (
        <div className="flex min-h-[60svh] flex-col items-center justify-center gap-6 px-4 text-center">
          <p className="text-[19px] font-bold text-ink">Pick a course to start learning.</p>
          <Link href="/welcome" className={buttonClasses({ size: "lg" })}>
            Choose a course
          </Link>
        </div>
      )}
    </PageColumns>
  );
}

function LearnSkeleton() {
  return (
    <div aria-busy className="mx-auto flex max-w-[1056px] gap-12 px-4 pt-[58px] md:px-6 lg:pt-6">
      <div className="mx-auto w-full max-w-[592px] lg:mx-0">
        <div className="h-[90px] animate-pulse rounded-[13px] bg-line" />
        <div className="mt-[81px] flex flex-col items-center gap-6">
          {[0, -45, -70, -45, 0].map((offset, i) => (
            <div key={i} className="h-[65px] w-[70px] animate-pulse rounded-[50%] bg-line" style={{ transform: `translateX(${offset}px)` }} />
          ))}
        </div>
      </div>
      <div className="hidden w-[368px] shrink-0 flex-col gap-6 lg:flex">
        <div className="h-11 animate-pulse rounded-xl bg-snow" />
        <div className="h-[150px] animate-pulse rounded-2xl bg-snow" />
        <div className="h-[166px] animate-pulse rounded-2xl bg-snow" />
      </div>
    </div>
  );
}
