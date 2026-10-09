import { cn } from "@/lib/cn";

type ProgressBarProps = {
  /** 0 to 1. */
  value: number;
  label: string;
  /** Orange while a lesson is on a run of right answers. */
  tone?: "green" | "orange";
  className?: string;
};

/** Duolingo's progress bar: a grey track and a green fill with a faint highlight stripe along its top. */
export function ProgressBar({ value, label, tone = "green", className }: ProgressBarProps) {
  const percent = Math.round(Math.min(Math.max(value, 0), 1) * 100);
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={percent}
      className={cn("h-4 overflow-hidden rounded-full bg-line", className)}
    >
      <div
        className={cn(
          "relative h-full rounded-full transition-[width,background-color] duration-500 ease-out",
          tone === "orange" ? "bg-duo-orange" : "bg-duo-green",
        )}
        style={{ width: `${percent}%` }}
      >
        <div className="absolute inset-x-1 top-1 h-[3px] rounded-full bg-white/20" />
      </div>
    </div>
  );
}
