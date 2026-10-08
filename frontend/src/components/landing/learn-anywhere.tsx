import { AppStoreIcon, GooglePlayIcon } from "@/components/icons/store-icons";
import { buttonClasses } from "@/components/ui/button";
import { cn } from "@/lib/cn";

import { AnimatedIllustration } from "./animated-illustration";
import { ComingSoonLink } from "./coming-soon-link";

const STORES = [
  { caption: "Download on the", name: "App Store", Icon: AppStoreIcon },
  { caption: "Get it on", name: "Google Play", Icon: GooglePlayIcon },
];

/** "learn anytime, anywhere" with store badges over a scene of floating phones. */
export function LearnAnywhere() {
  return (
    <section className="relative lg:h-[1385px]">
      <div className="relative z-10 mx-auto flex max-w-[620px] flex-col items-center px-4 pt-16 text-center lg:pt-[236px]">
        <h2 className="font-display text-[40px] font-semibold leading-[1.15] tracking-[-0.02em] text-duo-navy lg:text-[66px] lg:leading-[80px] lg:tracking-normal">
          learn anytime, anywhere
        </h2>
        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:gap-[25px] lg:mt-12">
          {STORES.map(({ caption, name, Icon }) => (
            <ComingSoonLink
              key={name}
              feature="Mobile apps"
              className={buttonClasses({
                variant: "outline",
                className: "h-[63px] gap-2 px-3.5 normal-case tracking-normal text-ink",
              })}
            >
              <Icon className="size-[34px]" />
              <span className="flex flex-col text-left leading-tight">
                <span className="text-[13px]">{caption}</span>
                <span className="text-[17px]">{name}</span>
              </span>
            </ComingSoonLink>
          ))}
        </div>
      </div>

      {/* Two layers, as on duolingo.com: floating shapes behind, phones in front. */}
      <AnimatedIllustration
        posters={["/landing/learn-anywhere-shapes.svg", "/landing/learn-anywhere-phones.svg"]}
        layers={[{ src: "/landing/lottie/learn-anywhere-shapes.json" }, { src: "/landing/lottie/learn-anywhere-phones.json" }]}
        width={4100}
        height={2300}
        className={cn(
          "left-1/2 -mt-6 w-[200%] -translate-x-1/2",
          "lg:absolute lg:top-[167px] lg:mt-0 lg:w-[2000px] lg:translate-x-[calc(-50%+140px)]",
        )}
      />
    </section>
  );
}
