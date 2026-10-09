import { CreateProfileButtons } from "@/components/app/create-profile";

import { AvatarBanner } from "./avatar-banner";

/**
 * What a guest (a learner who came through "Get started") sees instead of a profile: like duolingo.com,
 * there is no profile until they create one.
 */
export function GuestProfile() {
  return (
    <div className="px-4 pt-4 pb-12 md:px-0 lg:pt-0">
      <AvatarBanner />
      <div className="mx-auto mt-8 max-w-[360px] text-center">
        <h1 className="text-[24px] leading-[30px] font-bold text-ink-strong">Create a profile to save your progress!</h1>
        <p className="mt-2 text-[17px] leading-6 text-ink-soft">Your streak, XP and achievements will show here.</p>
        <div className="mt-6">
          <CreateProfileButtons />
        </div>
      </div>
    </div>
  );
}
