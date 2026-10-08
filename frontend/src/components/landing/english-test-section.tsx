import { buttonClasses } from "@/components/ui/button";

import { ComingSoonLink } from "./coming-soon-link";
import { FeatureRow } from "./feature-row";

/** "duolingo english test" product row (placeholder destination). */
export function EnglishTestSection() {
  return (
    <div className="overflow-hidden pt-6 lg:pb-11 lg:pt-24">
      <FeatureRow
        title="duolingo english test"
        body="Our convenient, fast, and affordable English test integrates the latest assessment science and AI — empowering anyone to accurately test their English where and when they're at their best."
        poster="/landing/english-test.svg"
        animation={{ src: "/landing/lottie/english-test.json" }}
        textLeft={0}
        imageLeft={619}
        action={
          <ComingSoonLink
            feature="The English Test"
            className={buttonClasses({ variant: "outline", size: "lg", className: "w-full max-w-[330px]" })}
          >
            Certify your English
          </ComingSoonLink>
        }
      />
    </div>
  );
}
