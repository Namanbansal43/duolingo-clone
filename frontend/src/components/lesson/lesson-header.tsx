import Image from "next/image";

import { ProgressBar } from "@/components/ui/progress-bar";
import type { Hearts } from "@/lib/api/types";

// From this many right answers in a row the bar turns orange and counts the run, as on Duolingo.
const COMBO_FROM = 5;

type LessonHeaderProps = {
  progress: number;
  combo: number;
  hearts: Hearts;
  onQuit: () => void;
};

/** Close button, the lesson's progress bar, and the hearts left. */
export function LessonHeader({ progress, combo, hearts, onQuit }: LessonHeaderProps) {
  const onRun = combo >= COMBO_FROM;
  return (
    <header className="mx-auto flex w-full max-w-[1000px] items-center gap-4 px-4 pt-5 sm:gap-6 sm:px-0 sm:pt-[50px]">
      <button
        type="button"
        onClick={onQuit}
        aria-label="Quit lesson"
        className="shrink-0 rounded-md outline-none hover:brightness-75 focus-visible:ring-4 focus-visible:ring-duo-blue-border"
      >
        <Image src="/app/lesson/close.svg" width={18} height={18} alt="" className="size-[18px]" />
      </button>
      <div className="relative flex-1">
        {onRun && (
          <p className="absolute -top-[22px] left-1/2 -translate-x-1/2 text-[13px] font-bold tracking-[0.6px] whitespace-nowrap text-duo-orange uppercase">
            {combo} in a row
          </p>
        )}
        <ProgressBar value={progress} label="Lesson progress" tone={onRun ? "orange" : "green"} />
      </div>
      <p className="flex shrink-0 items-center gap-1.5 text-[17px] font-bold text-duo-red" title={`${hearts.current} hearts`}>
        <Image src="/app/lesson/heart.svg" width={33} height={32} alt="" className="h-8 w-[33px]" />
        {hearts.current}
        <span className="sr-only">hearts</span>
      </p>
    </header>
  );
}
