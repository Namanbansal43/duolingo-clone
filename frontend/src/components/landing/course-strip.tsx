"use client";

import Link from "next/link";
import { useRef } from "react";

import { Flag } from "@/components/icons/flag";
import { comingSoon } from "@/lib/coming-soon";
import { COURSES, type Course } from "@/lib/languages";

/** Horizontally scrolling list of courses under the hero (desktop only, as on duolingo.com). */
export function CourseStrip() {
  const scrollerRef = useRef<HTMLUListElement>(null);

  const page = (direction: 1 | -1) => {
    const el = scrollerRef.current;
    el?.scrollBy({ left: direction * el.clientWidth * 0.75, behavior: "smooth" });
  };

  return (
    <nav aria-label="Courses" className="hidden border-y-2 border-line md:block">
      <div className="mx-auto flex h-[74px] max-w-[1122px] items-center gap-5 px-4">
        <ArrowButton direction="prev" onClick={() => page(-1)} />
        <ul
          ref={scrollerRef}
          className="flex flex-1 items-center gap-6 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        >
          {COURSES.map((course) => (
            <li key={course.flag} className="shrink-0">
              <CourseItem course={course} />
            </li>
          ))}
        </ul>
        <ArrowButton direction="next" onClick={() => page(1)} />
      </div>
    </nav>
  );
}

const itemClasses =
  "flex items-center gap-2.5 py-2 text-[14px] font-bold uppercase tracking-[0.7px] text-ink-soft outline-none focus-visible:underline";

function CourseItem({ course }: { course: Course }) {
  const content = (
    <>
      <Flag code={course.flag} />
      {course.label}
    </>
  );

  return course.available ? (
    <Link href="/learn" className={itemClasses}>
      {content}
    </Link>
  ) : (
    <button type="button" onClick={() => comingSoon(`The ${course.label} course`)} className={itemClasses}>
      {content}
    </button>
  );
}

function ArrowButton({ direction, onClick }: { direction: "prev" | "next"; onClick: () => void }) {
  return (
    <button
      type="button"
      aria-label={direction === "prev" ? "Previous courses" : "Next courses"}
      onClick={onClick}
      className="grid size-6 shrink-0 place-items-center text-ink-faint hover:text-ink-soft"
    >
      <svg viewBox="0 0 16 16" fill="none" className="size-3.5">
        <path
          d={direction === "prev" ? "M10 2L4 8L10 14" : "M6 2L12 8L6 14"}
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
}
