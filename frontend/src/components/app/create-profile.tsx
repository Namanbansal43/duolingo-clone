"use client";

import { Button } from "@/components/ui/button";
import { comingSoon } from "@/lib/coming-soon";

import { RailCard } from "./right-rail";

const buttonShape = "rounded-2xl text-[15px] tracking-[0.8px]";

/**
 * CREATE A PROFILE and SIGN IN, which duolingo.com offers guests. There is one built-in learner and the
 * brief lets accounts stay simple, so both are "coming soon".
 */
export function CreateProfileButtons() {
  return (
    <div className="flex flex-col gap-2.5">
      <Button size="lg" fullWidth className={buttonShape} onClick={() => comingSoon("Creating a profile")}>
        Create a profile
      </Button>
      <Button variant="secondary" size="lg" fullWidth className={buttonShape} onClick={() => comingSoon("Signing in")}>
        Sign in
      </Button>
    </div>
  );
}

/** The right-rail card a guest sees on duolingo.com. */
export function CreateProfileCard() {
  return (
    <RailCard>
      <h2 className="text-[19px] leading-7 font-bold text-ink">Create a profile to save your progress!</h2>
      <div className="mt-6">
        <CreateProfileButtons />
      </div>
    </RailCard>
  );
}
