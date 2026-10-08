import { AnimatedIllustration } from "@/components/ui/animated-illustration";
import { Button } from "@/components/ui/button";
import { SpeechBubble } from "@/components/ui/speech-bubble";

import { OnboardingFooter } from "./onboarding-footer";

const WAVE = [{ src: "/onboarding/duo-wave.json", loopFrom: null }];

/** Step 2: Duo waves hello. */
export function IntroStep({ onContinue }: { onContinue: () => void }) {
  return (
    <div className="grid min-h-svh grid-rows-[1fr_auto]">
      <main className="flex flex-col items-center justify-center px-4 sm:pt-[72px]">
        <SpeechBubble tail="bottom">Hi there! I&rsquo;m Duo!</SpeechBubble>
        {/* The animation's canvas is mostly empty sky; this box shows only its lower part, where Duo stands. */}
        <AnimatedIllustration
          posters={["/onboarding/duo-wave.svg"]}
          layers={WAVE}
          width={916}
          height={939}
          fit="cover-bottom"
          priority
          className="mt-[15px] h-[170px] w-[390px] max-w-full"
        />
      </main>
      <OnboardingFooter>
        <Button size="xl" onClick={onContinue} autoFocus>
          Continue
        </Button>
      </OnboardingFooter>
    </div>
  );
}
