import { CourseStrip } from "@/components/landing/course-strip";
import { EnglishTestSection } from "@/components/landing/english-test-section";
import { FeatureSections } from "@/components/landing/feature-sections";
import { FinalCta } from "@/components/landing/final-cta";
import { Hero } from "@/components/landing/hero";
import { SiteFooter } from "@/components/landing/site-footer";
import { SiteHeader } from "@/components/landing/site-header";
import { StickyHeader } from "@/components/landing/sticky-header";
import { SuperSection } from "@/components/landing/super-section";

const HERO_CTA_ID = "hero-cta";

/** Marketing landing page, mirroring duolingo.com section by section. */
export default function LandingPage() {
  return (
    <div className="overflow-x-clip">
      <StickyHeader heroCtaId={HERO_CTA_ID} />
      <SiteHeader />
      <main>
        <Hero ctaId={HERO_CTA_ID} />
        <CourseStrip />
        <FeatureSections />
        <SuperSection />
        <EnglishTestSection />
        <FinalCta />
      </main>
      <SiteFooter />
    </div>
  );
}
