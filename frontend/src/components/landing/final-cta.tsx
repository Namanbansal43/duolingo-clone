import Link from "next/link";

import { AnimatedIllustration } from "@/components/ui/animated-illustration";
import { buttonClasses } from "@/components/ui/button";
import { siteConfig } from "@/config/site";

/**
 * Closing call-to-action. The illustration is a background whose green wave
 * runs into the footer, so it is anchored to the bottom and cropped at the sides.
 */
export function FinalCta() {
  return (
    <section className="relative h-[640px] overflow-hidden md:h-[843px]">
      {/* Extends 2px past the bottom so the wave's anti-aliased edge never shows above the footer. */}
      <AnimatedIllustration
        posters={["/landing/final-cta.svg"]}
        // Scene (looping) behind; the owl peeking out of the phone plays once and stays.
        layers={[
          { src: "/landing/lottie/final-cta-b.json" },
          { src: "/landing/lottie/final-cta-a.json", loopFrom: null },
        ]}
        width={1920}
        height={1060}
        fit="cover-bottom"
        className="absolute inset-x-0 top-0 -bottom-[2px]"
      />
      <div className="relative mx-auto flex max-w-[620px] flex-col items-center gap-8 px-4 pt-14 text-center md:gap-12 md:pt-[92px]">
        <h2 className="font-display text-[40px] font-semibold leading-[1.15] tracking-[-0.02em] text-duo-green md:text-[66px] md:leading-[80px] md:tracking-normal">
          learn a language with {siteConfig.name}
        </h2>
        <Link href="/welcome" className={buttonClasses({ size: "lg", className: "w-full max-w-[330px]" })}>
          Get started
        </Link>
      </div>
    </section>
  );
}
