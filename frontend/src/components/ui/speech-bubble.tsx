import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

type SpeechBubbleProps = {
  /** Where the tail points: down at a character below, or left at a character beside it. */
  tail: "bottom" | "left";
  children: ReactNode;
  className?: string;
};

/** The bordered bubble Duo speaks in. The tail is a rotated square showing two of its borders. */
export function SpeechBubble({ tail, children, className }: SpeechBubbleProps) {
  return (
    <div
      className={cn(
        "relative rounded-xl border-2 border-line bg-page px-4 py-3",
        "text-[17px] font-medium leading-6 text-ink-strong sm:text-[20px]",
        className,
      )}
    >
      {children}
      <span
        aria-hidden
        className={cn(
          "absolute size-3.5 rotate-45 border-line bg-page",
          tail === "bottom"
            ? "-bottom-[9px] left-1/2 -translate-x-1/2 border-r-2 border-b-2"
            : "top-1/2 -left-[9px] -translate-y-1/2 border-b-2 border-l-2",
        )}
      />
    </div>
  );
}
