"use client";

import Image from "next/image";

import { Button } from "@/components/ui/button";
import { comingSoon } from "@/lib/coming-soon";

import { AnimatedIllustration } from "./animated-illustration";

/** Dark "Power up with Super Duolingo" promo. Subscriptions are a placeholder in this clone. */
export function SuperSection() {
  return (
    <section className="bg-super-night">
      <div className="mx-auto flex max-w-[1020px] flex-col items-center gap-8 px-4 py-16 lg:h-[900px] lg:flex-row lg:gap-10 lg:py-0">
        <AnimatedIllustration
          posters={["/landing/super.svg"]}
          layers={[{ src: "/landing/lottie/super.json", loopFrom: 35.5 }]}
          width={530}
          height={530}
          className="w-full max-w-[360px] lg:size-[530px] lg:max-w-none"
        />
        <div className="flex flex-1 flex-col items-center gap-8 lg:gap-[53px]">
          <Image src="/landing/super-logo.svg" width={339} height={55} alt="Super Duolingo" className="md:hidden" />
          <Image
            src="/landing/super-logo-wide.svg"
            width={605}
            height={91}
            alt="Super Duolingo"
            className="hidden w-[418px] md:block"
          />
          <Button variant="white" size="lg" className="w-full max-w-[330px] md:w-auto" onClick={() => comingSoon("Super Duolingo")}>
            Try 1 week free
          </Button>
        </div>
      </div>
    </section>
  );
}
