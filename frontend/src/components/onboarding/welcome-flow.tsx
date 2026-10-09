"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { completeOnboarding } from "@/lib/api/endpoints";
import type { CatalogCourse, DailyGoalXp } from "@/lib/api/types";
import { comingSoon } from "@/lib/coming-soon";

import { CoursePicker } from "./course-picker";
import { DailyGoalStep } from "./daily-goal-step";
import { IntroStep } from "./intro-step";

type Step = "course" | "intro" | "goal";

/**
 * The "Get started" flow: pick a course, meet Duo, choose a daily goal. Nothing is saved until the
 * end, when POST /api/v1/me/onboarding starts the learner over as a new account with the course,
 * the goal and the browser's time zone, so the path begins at its first node.
 * Duolingo's survey screens (how did you hear about us, why are you learning...) are left out:
 * their answers would not be used anywhere.
 */
export function WelcomeFlow() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("course");
  const [course, setCourse] = useState<CatalogCourse | null>(null);
  const [goal, setGoal] = useState<DailyGoalXp | null>(null);
  const [saving, setSaving] = useState(false);

  const goTo = (next: Step) => {
    setStep(next);
    window.scrollTo(0, 0);
  };

  const pickCourse = (picked: CatalogCourse) => {
    if (!picked.is_available) {
      comingSoon(picked.title);
      return;
    }
    setCourse(picked);
    goTo("intro");
  };

  const finish = async () => {
    if (!course || goal === null) return;
    setSaving(true);
    try {
      await completeOnboarding({
        active_course_id: course.id,
        daily_goal_xp: goal,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      });
      router.push("/learn");
    } catch (error) {
      toast(error instanceof Error ? error.message : "Something went wrong. Please try again.");
      setSaving(false);
    }
  };

  switch (step) {
    case "course":
      return <CoursePicker onPick={pickCourse} />;
    case "intro":
      return <IntroStep onContinue={() => goTo("goal")} />;
    case "goal":
      return (
        <DailyGoalStep
          selected={goal}
          saving={saving}
          // The course is picked and Duo has said hello; the goal is the last step.
          progress={saving ? 1 : 2 / 3}
          onSelect={setGoal}
          onBack={() => goTo("intro")}
          onContinue={finish}
        />
      );
  }
}
