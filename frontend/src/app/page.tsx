import { CourseStrip } from "@/components/landing/course-strip";
import { Hero } from "@/components/landing/hero";
import { SiteHeader } from "@/components/landing/site-header";
import { StickyHeader } from "@/components/landing/sticky-header";

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
      </main>
    </div>
  );
}
