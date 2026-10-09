import Image from "next/image";
import { Target, Timer } from "lucide-react";
import type { ReactNode } from "react";

import { AchievementBadge } from "@/components/achievements/achievement-badge";
import { AnimatedIllustration } from "@/components/ui/animated-illustration";
import { Button } from "@/components/ui/button";
import { SpeechBubble } from "@/components/ui/speech-bubble";
import type { Achievement, Completion } from "@/lib/api/types";
import { cn } from "@/lib/cn";
import { comingSoon } from "@/lib/coming-soon";

const WAVE = [{ src: "/onboarding/duo-wave.json", loopFrom: null }];

/** A full-screen step of the lesson's ending: content in the middle, a footer with its buttons. */
function Screen({ children, footer }: { children: ReactNode; footer: ReactNode }) {
  return (
    <div className="grid min-h-svh grid-rows-[1fr_auto]">
      <main className="flex flex-col items-center justify-center px-4 py-8 text-center">{children}</main>
      <footer className="border-t-2 border-line">
        <div className="mx-auto flex w-full max-w-[1000px] items-center justify-between gap-4 px-4 py-4 sm:h-[140px] sm:px-10 sm:py-0">
          {footer}
        </div>
      </footer>
    </div>
  );
}

/** "Let's review the exercise you missed!", before the mistakes come round again. */
export function ReviewIntro({ onContinue }: { onContinue: () => void }) {
  return (
    <div className="flex flex-1 flex-col">
      <div className="flex flex-1 items-end justify-center px-4">
        <div className="flex items-center gap-2">
          <Image src="/app/path/duo.svg" width={1080} height={1080} alt="" className="-mr-[52px] -mb-[60px] -ml-[68px] size-[260px]" />
          <SpeechBubble tail="left">Let&rsquo;s review the exercise you missed!</SpeechBubble>
        </div>
      </div>
      <footer className="border-t-2 border-line">
        <div className="mx-auto flex w-full max-w-[1000px] justify-end px-4 py-4 sm:h-[140px] sm:items-center sm:px-10 sm:py-0">
          <Button size="xl" onClick={onContinue} autoFocus className="w-full sm:w-auto sm:min-w-[150px]">
            Continue
          </Button>
        </div>
      </footer>
    </div>
  );
}

/** "Lesson complete!": the XP earned, accuracy and time, in Duolingo's three stat cards. */
export function LessonComplete({ result, onContinue }: { result: Completion; onContinue: () => void }) {
  const minutes = Math.floor(result.duration_seconds / 60);
  const seconds = String(result.duration_seconds % 60).padStart(2, "0");
  return (
    <Screen
      footer={
        <>
          <Button variant="outline" size="xl" onClick={() => comingSoon("Lesson review")} className="hidden text-ink-faint sm:inline-flex">
            Review lesson
          </Button>
          <Button variant="secondary" size="xl" onClick={onContinue} autoFocus className="w-full sm:w-auto sm:min-w-[150px]">
            Continue
          </Button>
        </>
      }
    >
      <AnimatedIllustration
        posters={["/onboarding/duo-wave.svg"]}
        layers={WAVE}
        width={916}
        height={939}
        fit="cover-bottom"
        priority
        className="h-[190px] w-[390px] max-w-full"
      />
      <h1 className="mt-6 animate-pop-in text-[32px] font-bold text-duo-gold">Lesson complete!</h1>
      <div className="mt-8 flex flex-wrap justify-center gap-4">
        <StatCard label="Total XP" color="var(--color-duo-gold)">
          <Image src="/app/cards/quest-xp.svg" width={56} height={56} alt="" className="size-6" />
          {result.xp_earned}
        </StatCard>
        <StatCard label={accuracyLabel(result.accuracy)} color="var(--color-duo-green)">
          <Target className="size-6" strokeWidth={3} />
          {result.accuracy}%
        </StatCard>
        <StatCard label={result.duration_seconds < 120 ? "Speedy" : "Committed"} color="var(--color-duo-blue)">
          <Timer className="size-6" strokeWidth={3} />
          {minutes}:{seconds}
        </StatCard>
      </div>
    </Screen>
  );
}

function StatCard({ label, color, children }: { label: string; color: string; children: ReactNode }) {
  return (
    <div className="w-[140px] animate-pop-in rounded-2xl border-2 sm:w-[150px]" style={{ borderColor: color, backgroundColor: color }}>
      <p className="py-1 text-[13px] font-bold tracking-[0.6px] text-white uppercase">{label}</p>
      <p
        className="flex items-center justify-center gap-2 rounded-[14px] bg-white py-4 text-[20px] font-bold"
        style={{ color }}
      >
        {children}
      </p>
    </div>
  );
}

function accuracyLabel(accuracy: number): string {
  if (accuracy === 100) return "Amazing";
  if (accuracy >= 80) return "Great";
  return "Good";
}

const WEEKDAYS = ["Su", "M", "Tu", "W", "Th", "F", "Sa"];

/** The streak celebration after today's first lesson: the flame, the new count, and the days around today. */
export function StreakExtended({ length, onContinue }: { length: number; onContinue: () => void }) {
  // Up to two streak days before today, then the days to come.
  const before = Math.min(length - 1, 2);
  const days = Array.from({ length: 5 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() + i - before);
    return { label: WEEKDAYS[date.getDay()], done: i <= before, today: i === before };
  });
  return (
    <Screen
      footer={
        <Button variant="secondary" size="xl" onClick={onContinue} autoFocus className="ml-auto w-full sm:w-auto sm:min-w-[150px]">
          Continue
        </Button>
      }
    >
      <Image src="/app/stats/streak.svg" width={25} height={30} alt="" className="h-[120px] w-[100px] animate-pop-in" />
      <p className="mt-4 bg-linear-to-b from-duo-gold to-duo-orange bg-clip-text font-display text-[110px] leading-none text-transparent">
        {length}
      </p>
      <p className="text-[26px] font-bold text-duo-orange">day streak</p>
      <div className="mt-8 w-[340px] max-w-full rounded-2xl border-2 border-line">
        <div className="flex justify-center gap-3 px-4 pt-3 pb-4">
          {days.map((day) => (
            <div key={day.label} className="flex w-10 flex-col items-center gap-2">
              <span className={cn("text-[15px] font-bold", day.today ? "text-duo-orange" : "text-ink-faint")}>{day.label}</span>
              <span
                className={cn(
                  "flex size-[34px] items-center justify-center rounded-full",
                  day.done ? "bg-duo-orange text-white" : "bg-line",
                )}
              >
                {day.done && <span aria-hidden className="text-[18px] font-bold">&#10003;</span>}
              </span>
            </div>
          ))}
        </div>
        <p className="border-t-2 border-line px-4 py-3 text-[17px] leading-6 text-ink-soft">
          Practice each day so your streak won&rsquo;t reset!
        </p>
      </div>
    </Screen>
  );
}

/** An achievement went up a level: its badge at the new level, and what the next one needs. */
export function AchievementUnlocked({ achievement, onContinue }: { achievement: Achievement; onContinue: () => void }) {
  const last = achievement.level === achievement.max_level;
  return (
    <Screen
      footer={
        <Button variant="secondary" size="xl" onClick={onContinue} autoFocus className="ml-auto w-full sm:w-auto sm:min-w-[150px]">
          Continue
        </Button>
      }
    >
      <AchievementBadge achievement={achievement} className="w-[150px] animate-pop-in" />
      <h1 className="mt-8 text-[32px] leading-10 font-bold text-duo-gold">Achievement unlocked!</h1>
      <p className="mt-3 text-[21px] font-bold text-ink">
        {achievement.title}, level {achievement.level}
      </p>
      <p className="mt-1 text-[17px] leading-6 text-ink-soft">
        {last ? "That's the top level. Amazing!" : `Next level: ${achievement.description}`}
      </p>
    </Screen>
  );
}
