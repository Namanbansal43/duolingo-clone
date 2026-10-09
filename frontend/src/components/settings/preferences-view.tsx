"use client";

import { useState, type ReactNode } from "react";
import { toast } from "sonner";

import { PageError } from "@/components/app/page-error";
import { getMe, updateMe } from "@/lib/api/endpoints";
import type { DailyGoalXp, DarkModeChoice, Me, UserSettings } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";
import { DAILY_GOALS } from "@/lib/daily-goals";
import { usePreferences } from "@/lib/preferences";

import { SelectField } from "./select-field";
import { SettingsLayout, SettingsRow, SettingsSection } from "./settings-layout";
import { Switch } from "./switch";

type Toggle = keyof Omit<UserSettings, "dark_mode">;

// duolingo.com's "Lesson experience" switches, in its order.
const LESSON_EXPERIENCE: { key: Toggle; label: string }[] = [
  { key: "sound_effects", label: "Sound effects" },
  { key: "animations", label: "Animations" },
  { key: "motivational_messages", label: "Motivational messages" },
  { key: "listening_exercises", label: "Listening exercises" },
];

const DARK_MODE: { value: DarkModeChoice; label: string }[] = [
  { value: "system", label: "System Default" },
  { value: "on", label: "On" },
  { value: "off", label: "Off" },
];

const GOALS = DAILY_GOALS.map((goal) => ({ value: String(goal.xp), label: `${goal.label} (${goal.xp} XP a day)` }));

/**
 * /settings/preferences, duolingo.com's Preferences page: the lesson switches and dark mode, plus the daily
 * goal chosen in "Get started". Every change is saved at once, as on Duolingo.
 */
export function PreferencesView() {
  const page = useApi(getMe);
  const { settings, update } = usePreferences();

  if (page.status === "error") return <PageError message={page.error.message} onRetry={page.retry} />;
  if (page.status === "loading" || !settings) return <SettingsSkeleton />;

  return (
    <SettingsLayout title="Preferences" isGuest={page.data.is_guest}>
      <SettingsSection title="Lesson experience">
        {LESSON_EXPERIENCE.map(({ key, label }) => (
          <SettingsRow key={key} id={`setting-${key}`} label={label}>
            <Switch
              checked={settings[key]}
              onChange={(checked) => void update({ [key]: checked })}
              labelledBy={`setting-${key}`}
            />
          </SettingsRow>
        ))}
      </SettingsSection>

      <SettingsSection title="Daily goal">
        <DailyGoalField me={page.data} />
      </SettingsSection>

      <SettingsSection title="Appearance">
        <Field id="setting-dark-mode" label="Dark mode">
          <SelectField
            id="setting-dark-mode"
            value={settings.dark_mode}
            options={DARK_MODE}
            onChange={(dark_mode) => void update({ dark_mode })}
          />
        </Field>
      </SettingsSection>
    </SettingsLayout>
  );
}

function DailyGoalField({ me }: { me: Me }) {
  const [goal, setGoal] = useState(me.daily_goal_xp);
  const change = async (value: string) => {
    const before = goal;
    setGoal(Number(value) as DailyGoalXp);
    try {
      await updateMe({ daily_goal_xp: Number(value) as DailyGoalXp });
    } catch (error) {
      setGoal(before);
      toast(error instanceof Error ? error.message : "Couldn't save your goal. Please try again.");
    }
  };
  return (
    <Field id="setting-daily-goal" label="XP to earn each day">
      <SelectField id="setting-daily-goal" value={String(goal)} options={GOALS} onChange={(value) => void change(value)} />
    </Field>
  );
}

/** A labelled control stacked under its label, like Dark mode on duolingo.com. */
function Field({ id, label, children }: { id: string; label: string; children: ReactNode }) {
  return (
    <div className="py-4 lg:pt-3 lg:pb-2">
      <label htmlFor={id} className="mb-3 block lg:mb-2 text-[17px] leading-6 font-bold text-ink lg:text-[19px]">
        {label}
      </label>
      {children}
    </div>
  );
}

export function SettingsSkeleton() {
  return (
    <div aria-busy className="mx-auto flex max-w-[1056px] gap-12 px-4 pt-6 md:px-6">
      <div className="mx-auto w-full max-w-[560px] lg:mx-0">
        <div className="h-10 w-48 animate-pulse rounded-lg bg-snow" />
        <div className="mt-12 flex flex-col gap-3">
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 animate-pulse rounded-xl bg-snow" />
          ))}
        </div>
      </div>
      <div className="hidden w-[368px] shrink-0 flex-col gap-4 lg:flex">
        <div className="h-48 animate-pulse rounded-2xl bg-snow" />
        <div className="h-32 animate-pulse rounded-2xl bg-snow" />
      </div>
    </div>
  );
}
