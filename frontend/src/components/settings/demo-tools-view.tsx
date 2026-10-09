"use client";

import { useState } from "react";
import { toast } from "sonner";

import { PageError } from "@/components/app/page-error";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { advanceDemoDay, emptyHearts, getDemoClock, getMe, resetDemo } from "@/lib/api/endpoints";
import type { DemoClock, Me } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";

import { SettingsSkeleton } from "./preferences-view";
import { SettingsLayout, SettingsRow, SettingsSection } from "./settings-layout";

async function loadDemo() {
  const [me, clock] = await Promise.all([getMe(), getDemoClock()]);
  return { me, clock };
}

type Action = "advance" | "empty" | "reset";

/**
 * /settings/demo: this clone's own section, not one of duolingo.com's. With one built-in learner and real
 * days taking a real day, these let a reviewer try what depends on time (streaks, heart regeneration, the
 * league week ending) and start over.
 */
export function DemoToolsView() {
  const page = useApi(loadDemo);
  const [busy, setBusy] = useState<Action | null>(null);
  const [confirmingReset, setConfirmingReset] = useState(false);

  if (page.status === "loading") return <SettingsSkeleton />;
  if (page.status === "error") return <PageError message={page.error.message} onRetry={page.retry} />;
  const { me, clock } = page.data;

  const run = async <T,>(action: Action, call: () => Promise<T>, done: (result: T) => string) => {
    setBusy(action);
    try {
      const result = await call();
      await page.refresh();
      toast(done(result));
    } catch (error) {
      toast(error instanceof Error ? error.message : "That didn't work. Please try again.");
    } finally {
      setBusy(null);
    }
  };

  return (
    <SettingsLayout
      title="Demo tools"
      isGuest={me.is_guest}
      intro="This clone has one built-in learner, and a day takes a real day to pass. These tools let you try what depends on time, or start again."
    >
      <SettingsSection title="Time">
        <SettingsRow id="demo-advance" label="Advance a day" description={<ClockStatus me={me} clock={clock} />}>
          <Button
            variant="secondary"
            size="sm"
            disabled={busy !== null}
            onClick={() =>
              void run("advance", advanceDemoDay, (moved) => `It's now ${dayName(new Date(moved.now), me)} in the app.`)
            }
          >
            Advance
          </Button>
        </SettingsRow>
      </SettingsSection>

      <SettingsSection title="Hearts">
        <SettingsRow
          id="demo-hearts"
          label="Empty hearts"
          description={`Lose every heart to see the out-of-hearts screen. One comes back every ${me.hearts.regen_minutes} minutes. You have ${me.hearts.current} now.`}
        >
          <Button
            variant="secondary"
            size="sm"
            disabled={busy !== null || me.hearts.current === 0}
            onClick={() => void run("empty", emptyHearts, () => "Your hearts are empty.")}
          >
            Empty
          </Button>
        </SettingsRow>
      </SettingsSection>

      <SettingsSection title="Start over">
        <SettingsRow
          id="demo-reset"
          label="Reset the demo"
          description="Back to the seeded learner: a 3 day streak, 30 XP, this week's Bronze League, and real time. Your preferences stay."
        >
          <Button variant="danger" size="sm" disabled={busy !== null} onClick={() => setConfirmingReset(true)}>
            Reset
          </Button>
        </SettingsRow>
      </SettingsSection>

      {confirmingReset && (
        <Modal label="Reset the demo?" onClose={() => setConfirmingReset(false)}>
          <h2 className="text-[24px] leading-8 font-bold text-ink-strong">Reset the demo?</h2>
          <p className="mt-3 text-[17px] leading-6 text-ink-soft">
            Your progress, and the other learners&rsquo;, goes back to how the demo began.
          </p>
          <Button
            variant="danger"
            size="lg"
            fullWidth
            autoFocus
            disabled={busy !== null}
            className="mt-6"
            onClick={() =>
              void run("reset", resetDemo, () => "The demo was reset.").then(() => setConfirmingReset(false))
            }
          >
            Reset
          </Button>
          <Button variant="ghost" size="lg" fullWidth className="mt-2" onClick={() => setConfirmingReset(false)}>
            Cancel
          </Button>
        </Modal>
      )}
    </SettingsLayout>
  );
}

function ClockStatus({ me, clock }: { me: Me; clock: DemoClock }) {
  const today = dayName(new Date(clock.now), me);
  const days = `${clock.days_ahead} ${clock.days_ahead === 1 ? "day" : "days"}`;
  return (
    <>
      Streaks, hearts and the league week follow the app&rsquo;s clock.{" "}
      {clock.days_ahead === 0 ? (
        <>It&rsquo;s on real time: {today}.</>
      ) : (
        <>
          It&rsquo;s {days} ahead: {today}.
        </>
      )}
    </>
  );
}

/** "Friday, October 9" in the learner's time zone. */
function dayName(date: Date, me: Me): string {
  return new Intl.DateTimeFormat("en-US", { weekday: "long", month: "long", day: "numeric", timeZone: me.timezone }).format(
    date,
  );
}
