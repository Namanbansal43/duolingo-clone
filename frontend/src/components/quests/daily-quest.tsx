import Image from "next/image";

import { cn } from "@/lib/cn";

/**
 * The daily quest, "Earn N XP": the learner's daily goal as duolingo.com shows it, an XP bolt, the
 * progress bar towards the goal and the reward chest at its end. The right rail shows it a little smaller
 * than the Quests page.
 */
export function DailyQuest({ xp, goal, size }: { xp: number; goal: number; size: "rail" | "page" }) {
  const done = Math.min(xp, goal);
  const page = size === "page";
  return (
    <div className="flex items-center gap-[22px]">
      <Image src="/app/cards/quest-xp.svg" width={60} height={60} alt="" className="size-[60px] shrink-0 object-contain" />
      <div className="min-w-0 flex-1">
        <p className={cn("font-bold text-ink", page ? "text-[19px] leading-[26px]" : "text-[17px] leading-6")}>
          Earn {goal} XP
        </p>
        <div className={cn("flex items-center", page ? "mt-2.5" : "mt-[14px]")}>
          <div
            role="progressbar"
            aria-label="Daily goal"
            aria-valuemin={0}
            aria-valuemax={goal}
            aria-valuenow={done}
            className={cn("relative flex-1 overflow-hidden bg-line", page ? "h-5 rounded-l-[10px]" : "h-[18px] rounded-l-[9px]")}
          >
            <div
              className={cn("h-full bg-duo-gold transition-[width] duration-500", page ? "rounded-r-[10px]" : "rounded-r-[9px]")}
              style={{ width: `${(done / goal) * 100}%` }}
            />
            <span
              className={cn(
                "absolute inset-0 flex items-center justify-center text-[14px] font-bold tracking-[0.56px]",
                page ? "leading-5" : "leading-[18px]",
                done > 0 ? "text-duo-gold-shade" : "text-ink-faint",
              )}
            >
              {done} / {goal}
            </span>
          </div>
          <Image src="/app/cards/quest-chest.svg" width={35} height={35} alt="" className="-ml-px size-[35px] shrink-0 object-contain pl-0.5" />
        </div>
      </div>
    </div>
  );
}
