"use client";

import Image from "next/image";

import { Flag } from "@/components/icons/flag";
import type { Me } from "@/lib/api/types";
import { cn } from "@/lib/cn";
import { comingSoon } from "@/lib/coming-soon";
import { isFlagCode } from "@/lib/languages";

const itemClasses = "flex h-11 items-center gap-2.5 rounded-xl px-4 text-[15px] leading-5 font-bold";

/** Course flag, streak, gems and hearts: the top of the right rail, or the top bar on smaller screens. */
export function StatsBar({ me, className }: { me: Me; className?: string }) {
  const { streak, hearts } = me;
  const streakColor = streak.extended_today ? "text-duo-orange" : streak.length > 0 ? "text-ink-faint" : "text-line";

  return (
    <div className={cn("flex items-center justify-between", className)}>
      {/* Only Spanish can be studied, so there is no other course to switch to yet. */}
      <button
        type="button"
        onClick={() => comingSoon("Switching courses")}
        title={me.active_course?.title}
        aria-label={`Learning ${me.active_course?.title ?? "no course yet"}`}
        className={cn(itemClasses, "hover:bg-snow")}
      >
        {me.active_course && isFlagCode(me.active_course.learning_language) && (
          <Flag code={me.active_course.learning_language} width={31} className="rounded-[18%]" />
        )}
      </button>
      <div className={itemClasses} title={`${streak.length} day streak`}>
        <Image
          src={streak.extended_today ? "/app/stats/streak.svg" : "/app/stats/streak-off.svg"}
          width={23}
          height={28}
          alt=""
          className="h-7 w-[23px] object-contain"
        />
        <span className={streakColor}>{streak.length}</span>
        <span className="sr-only">day streak</span>
      </div>
      <div className={itemClasses} title={`${me.gems} gems`}>
        <Image src="/app/stats/gem.svg" width={22} height={28} alt="" className="h-7 w-[22px] object-contain" />
        <span className="text-duo-blue">{me.gems}</span>
        <span className="sr-only">gems</span>
      </div>
      <div className={itemClasses} title={`${hearts.current} of ${hearts.max} hearts`}>
        <Image src="/app/stats/heart.svg" width={28} height={28} alt="" className="size-7 object-contain" />
        <span className="text-duo-red">{hearts.current}</span>
        <span className="sr-only">hearts</span>
      </div>
    </div>
  );
}
