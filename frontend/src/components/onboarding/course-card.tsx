import { Flag } from "@/components/icons/flag";
import type { CatalogCourse } from "@/lib/api/types";
import { isFlagCode } from "@/lib/languages";

const compact = new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 2 });

function learnersLabel(course: CatalogCourse) {
  if (!course.is_available) return "Coming soon";
  return `${compact.format(course.learners)} ${course.learners === 1 ? "learner" : "learners"}`;
}

/** A course tile on the "I want to learn..." screen. */
export function CourseCard({ course, onSelect }: { course: CatalogCourse; onSelect: (course: CatalogCourse) => void }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(course)}
      className="flex h-[217px] w-full flex-col items-center justify-center rounded-2xl border-2 border-b-4 border-line bg-white px-3 pt-3 pb-6 outline-none transition-[filter] hover:brightness-90 focus-visible:ring-4 focus-visible:ring-duo-blue-border active:translate-y-[2px] active:border-b-2"
    >
      {/* Duolingo leaves this gap above the flag, which keeps tiles with and without a subtitle aligned. */}
      <span aria-hidden className="h-5" />
      {isFlagCode(course.learning_language) && <Flag code={course.learning_language} width={88} />}
      <span className="mt-2.5 text-[17px] leading-[20.4px] font-bold text-ink">{course.title}</span>
      <span className="mt-1.5 text-[17px] leading-[19.55px] font-medium text-ink-soft">{learnersLabel(course)}</span>
    </button>
  );
}
