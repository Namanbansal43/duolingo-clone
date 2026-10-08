import Link from "next/link";

import { buttonClasses } from "@/components/ui/button";
import { siteConfig } from "@/config/site";
import { cn } from "@/lib/cn";

import { AnimatedIllustration } from "./animated-illustration";

/*
 * One grid, two arrangements (named grid areas):
 *  - Mobile: illustration and tagline centred in the first screen, buttons pinned to its bottom.
 *  - Desktop: illustration on the left, tagline and buttons in a 480px column on the right.
 * Keeping a single set of buttons lets the sticky header watch one element at every width.
 */
export function Hero({ ctaId }: { ctaId: string }) {
  return (
    <section
      className={cn(
        "mx-auto grid min-h-[calc(100svh-70px)] max-w-[1020px] justify-items-center px-4",
        "grid-rows-[1fr_auto_auto_1fr_auto] [grid-template-areas:'.'_'art'_'title'_'.'_'cta']",
        "md:min-h-[min(calc(100svh-150px),760px)] md:grid-cols-[1fr_480px] md:grid-rows-[1fr_auto_auto_1fr] md:gap-x-[15px]",
        "md:[grid-template-areas:'art_.'_'art_title'_'art_cta'_'art_.']",
      )}
    >
      <AnimatedIllustration
        posters={["/landing/hero.svg"]}
        layers={[{ src: "/landing/lottie/hero.json", loopFrom: 130 }]}
        width={424}
        height={424}
        priority
        className="w-[260px] self-center [grid-area:art] sm:w-[340px] md:w-full md:max-w-[424px] md:justify-self-end"
      />

      <h1 className="mt-8 max-w-[480px] text-center text-[26px] font-bold leading-snug text-ink [grid-area:title] sm:text-[32px] md:mt-0">
        {siteConfig.tagline}
      </h1>

      <div id={ctaId} className="flex w-full max-w-[330px] flex-col gap-3 pb-5 [grid-area:cta] md:mt-10 md:pb-0">
        <Link href="/learn" className={buttonClasses({ size: "lg", fullWidth: true })}>
          Get started
        </Link>
        <Link href="/learn" className={buttonClasses({ variant: "outline", size: "lg", fullWidth: true })}>
          I already have an account
        </Link>
      </div>
    </section>
  );
}
