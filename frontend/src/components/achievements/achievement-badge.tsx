import type { Achievement } from "@/lib/api/types";
import { cn } from "@/lib/cn";

/**
 * Achievements with Duolingo's badge art in public/app/achievements: <key>.svg while levels remain,
 * <key>-gold.svg once the last level is reached.
 */
const WITH_ART = new Set(["wildfire", "sage", "scholar", "sharpshooter"]);

/**
 * An achievement's badge with its level along the bottom. Badges not yet reached are greyed out.
 * Size it with a width class; the label scales with it (11px on duolingo.com's 89px badge).
 */
export function AchievementBadge({ achievement, className }: { achievement: Achievement; className?: string }) {
  const { level, max_level: maxLevel } = achievement;
  const art = WITH_ART.has(achievement.key) ? achievement.key : "wildfire";
  const gold = level === maxLevel;
  return (
    <div
      role="img"
      aria-label={level > 0 ? `${achievement.title}, level ${level}` : `${achievement.title}, not reached yet`}
      className={cn(
        "@container relative aspect-[89/111] shrink-0 bg-contain bg-center bg-no-repeat",
        level === 0 && "opacity-40 grayscale",
        className,
      )}
      style={{ backgroundImage: `url(/app/achievements/${art}${gold ? "-gold" : ""}.svg)` }}
    >
      {level > 0 && (
        <span
          className={cn(
            "absolute inset-x-0 bottom-[10%] text-center text-[12.4cqw] leading-[1.8] font-bold uppercase",
            gold ? "text-duo-orange-shade" : "text-white",
          )}
        >
          Level {level}
        </span>
      )}
    </div>
  );
}
