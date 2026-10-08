"use client";

import Link from "next/link";

import { RightRail } from "@/components/app/right-rail";
import { StatsBar } from "@/components/app/stats-bar";
import { Button, buttonClasses } from "@/components/ui/button";
import { getMe, getPath } from "@/lib/api/endpoints";
import { useApi } from "@/lib/api/use-api";

import { CoursePath } from "./course-path";

/** The learner and the path of their active course (the path needs the course id, so these load in turn). */
async function loadLearn() {
  const me = await getMe();
  const path = me.active_course ? await getPath(me.active_course.id) : null;
  return { me, path };
}

/**
 * /learn: the learning path in the middle, stats and cards on the right (wide screens), or a stats
 * bar across the top (narrower screens). Layout widths are duolingo.com's: a path column up to 592px,
 * a 48px gap and a 368px right rail.
 */
export function LearnView() {
  const learn = useApi(loadLearn);

  if (learn.status === "loading") return <LearnSkeleton />;
  if (learn.status === "error") {
    return (
      <div className="flex min-h-[60svh] flex-col items-center justify-center gap-6 px-4 text-center">
        <p className="text-[17px] text-ink-soft">{learn.error.message}</p>
        <Button variant="secondary" onClick={learn.retry}>
          Try again
        </Button>
      </div>
    );
  }

  const { me, path } = learn.data;
  return (
    <>
      <div className="sticky top-0 z-20 bg-white lg:hidden">
        <StatsBar me={me} className="mx-auto h-[58px] max-w-[592px] px-1" />
      </div>
      <div className="mx-auto flex max-w-[1056px] gap-12 md:px-6">
        <main className="mx-auto min-w-0 max-w-[592px] flex-1 lg:mx-0 lg:pt-6">
          {path ? (
            <CoursePath path={path} onChange={learn.refresh} />
          ) : (
            <div className="flex min-h-[60svh] flex-col items-center justify-center gap-6 px-4 text-center">
              <p className="text-[19px] font-bold text-ink">Pick a course to start learning.</p>
              <Link href="/welcome" className={buttonClasses({ size: "lg" })}>
                Choose a course
              </Link>
            </div>
          )}
        </main>
        <aside className="hidden w-[368px] shrink-0 lg:block">
          <div className="sticky top-0 pt-6 pb-6">
            <RightRail me={me} />
          </div>
        </aside>
      </div>
    </>
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
