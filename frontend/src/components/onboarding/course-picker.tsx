import { SiteHeader } from "@/components/landing/site-header";
import { Button } from "@/components/ui/button";
import { getCourses } from "@/lib/api/endpoints";
import type { CatalogCourse } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";

import { CourseCard } from "./course-card";

const gridClasses =
  "mx-auto mt-10 grid grid-cols-2 gap-x-[13px] gap-y-6 sm:mt-[86px] sm:grid-cols-3 md:w-fit md:grid-cols-[repeat(4,200px)]";

/** Step 1, "I want to learn...": every course from the API; only available ones can be picked. */
export function CoursePicker({ onPick }: { onPick: (course: CatalogCourse) => void }) {
  const courses = useApi(getCourses);

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[876px] px-4 pb-12">
        <h1 className="mt-8 text-center text-[24px] leading-10 font-bold text-ink sm:mt-[68px] sm:text-[32px]">
          I want to learn...
        </h1>

        {courses.status === "error" ? (
          <div className="mt-16 flex flex-col items-center gap-6 text-center">
            <p className="text-[17px] text-ink-soft">{courses.error.message}</p>
            <Button variant="secondary" onClick={courses.retry}>
              Try again
            </Button>
          </div>
        ) : (
          <ul className={gridClasses} aria-busy={courses.status === "loading"}>
            {courses.status === "loading"
              ? Array.from({ length: 8 }, (_, i) => (
                  <li key={i} className="h-[217px] animate-pulse rounded-2xl border-2 border-b-4 border-line bg-snow" />
                ))
              : courses.data.map((course) => (
                  <li key={course.id}>
                    <CourseCard course={course} onSelect={onPick} />
                  </li>
                ))}
          </ul>
        )}
      </main>
    </>
  );
}
