import { ArrowLeft } from "lucide-react";

import { AnimatedIllustration } from "@/components/ui/animated-illustration";
import { Button } from "@/components/ui/button";
import { ProgressBar } from "@/components/ui/progress-bar";
import { SpeechBubble } from "@/components/ui/speech-bubble";
import type { DailyGoalXp } from "@/lib/api/types";
import { cn } from "@/lib/cn";
import { DAILY_GOALS } from "@/lib/daily-goals";

import { OnboardingFooter } from "./onboarding-footer";

const CLIPBOARD = [{ src: "/onboarding/duo-clipboard.json" }];

type DailyGoalStepProps = {
  selected: DailyGoalXp | null;
  saving: boolean;
  progress: number;
  onSelect: (xp: DailyGoalXp) => void;
  onBack: () => void;
  onContinue: () => void;
};

/**
 * Step 3, "What's your daily learning goal?". A form with native radio buttons, so arrow keys
 * move the choice and Enter continues, as on Duolingo.
 */
export function DailyGoalStep({ selected, saving, progress, onSelect, onBack, onContinue }: DailyGoalStepProps) {
  return (
    <form
      className="grid min-h-svh grid-rows-[auto_1fr_auto]"
      onSubmit={(event) => {
        event.preventDefault();
        onContinue();
      }}
    >
      <header className="mx-auto flex w-full max-w-[1084px] items-center gap-4 px-4 pt-6 sm:px-6 sm:pt-[41px]">
        <button
          type="button"
          onClick={onBack}
          aria-label="Back"
          className="rounded-md text-ink-faint outline-none hover:brightness-75 focus-visible:ring-4 focus-visible:ring-duo-blue-border"
        >
          <ArrowLeft className="size-[18px]" strokeWidth={3} />
        </button>
        <ProgressBar value={progress} label="Setup progress" className="flex-1" />
      </header>

      <main className="mx-auto w-full max-w-[1084px] px-4 sm:px-6">
        <div className="mt-6 flex items-center sm:mt-[39px]">
          <AnimatedIllustration
            posters={["/onboarding/duo-clipboard.svg"]}
            layers={CLIPBOARD}
            width={645}
            height={486}
            priority
            className="w-[100px] shrink-0 sm:w-[140px]"
          />
          <SpeechBubble tail="left">What&rsquo;s your daily learning goal?</SpeechBubble>
        </div>

        <fieldset className="mx-auto mt-8 flex max-w-[484px] flex-col gap-4 pb-5 sm:mt-[59px]">
          <legend className="sr-only">Daily learning goal</legend>
          {DAILY_GOALS.map((goal) => {
            const checked = selected === goal.xp;
            return (
              <label
                key={goal.xp}
                className={cn(
                  "flex h-[62px] cursor-pointer items-center justify-between rounded-xl border-2 border-b-4 px-4 text-[17px] leading-6",
                  "transition-colors active:translate-y-[2px] active:border-b-2",
                  "has-[:focus-visible]:ring-4 has-[:focus-visible]:ring-duo-blue-border",
                  checked
                    ? "border-duo-blue-border bg-duo-blue-tint text-duo-blue-shade"
                    : "border-line bg-white text-ink hover:bg-snow",
                )}
              >
                <input
                  type="radio"
                  name="daily-goal"
                  value={goal.xp}
                  checked={checked}
                  onChange={() => onSelect(goal.xp)}
                  className="sr-only"
                />
                <span className="font-bold">{goal.minutes} min / day</span>
                <span className="font-medium">{goal.label}</span>
              </label>
            );
          })}
        </fieldset>
      </main>

      <OnboardingFooter>
        <Button type="submit" size="xl" disabled={selected === null || saving}>
          Continue
        </Button>
      </OnboardingFooter>
    </form>
  );
}
