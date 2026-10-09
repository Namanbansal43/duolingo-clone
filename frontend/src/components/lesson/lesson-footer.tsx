import Image from "next/image";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

import type { Feedback } from "./lesson-state";

const ROW = "mx-auto flex w-full max-w-[1000px] items-center gap-4 px-4 py-4 sm:h-[140px] sm:px-10 sm:py-0";

type CheckFooterProps = {
  canCheck: boolean;
  checking: boolean;
  onSkip: () => void;
  onCheck: () => void;
  /** Shown between the two buttons, e.g. "Can't listen now". */
  middle?: ReactNode;
};

/** SKIP and CHECK. CHECK stays grey until there is an answer to check. */
export function CheckFooter({ canCheck, checking, onSkip, onCheck, middle }: CheckFooterProps) {
  return (
    <footer className="border-t-2 border-line">
      <div className={cn(ROW, "justify-between")}>
        <Button variant="outline" size="xl" onClick={onSkip} disabled={checking} className="px-6 text-ink-faint sm:min-w-[150px]">
          Skip
        </Button>
        {middle}
        <Button size="xl" onClick={onCheck} disabled={!canCheck || checking} className="flex-1 sm:min-w-[150px] sm:flex-none">
          Check
        </Button>
      </div>
    </footer>
  );
}

/** The signature feedback bar: green with a check for a right answer, red with the solution for a wrong one. */
export function FeedbackBar({ feedback, onContinue }: { feedback: Feedback; onContinue: () => void }) {
  const { correct } = feedback;
  return (
    <footer
      role="status"
      className={cn("animate-slide-up", correct ? "bg-duo-green-tint text-duo-green-shade" : "bg-duo-red-tint text-duo-red-shade")}
    >
      <div className={cn(ROW, "flex-col items-stretch sm:flex-row sm:items-center")}>
        <div className="flex flex-1 items-center gap-4">
          <span className="hidden size-20 shrink-0 items-center justify-center rounded-full bg-white sm:flex">
            <Image
              src={correct ? "/app/lesson/feedback-correct.svg" : "/app/lesson/feedback-wrong.svg"}
              width={correct ? 41 : 30}
              height={correct ? 29 : 30}
              alt=""
              className={correct ? "h-[29px] w-[41px]" : "size-[30px]"}
            />
          </span>
          <div className="min-w-0">
            <h2 className="text-[24px] leading-[30px] font-bold">{feedback.heading}</h2>
            {feedback.solution && <p className="text-[17px] leading-[26px] break-words">{feedback.solution}</p>}
          </div>
        </div>
        <Button
          variant={correct ? "primary" : "danger"}
          size="xl"
          onClick={onContinue}
          autoFocus
          className="w-full sm:w-auto sm:min-w-[150px]"
        >
          Continue
        </Button>
      </div>
    </footer>
  );
}
