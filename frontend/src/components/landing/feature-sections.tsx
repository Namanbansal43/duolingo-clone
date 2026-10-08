import { siteConfig } from "@/config/site";

import { ComingSoonLink } from "./coming-soon-link";
import { FeatureRow, type FeatureRowProps } from "./feature-row";
import { LearnAnywhere } from "./learn-anywhere";

const FEATURES: FeatureRowProps[] = [
  {
    title: "free. fun. effective.",
    body: (
      <>
        Learning with {siteConfig.brand} is fun, and{" "}
        <ComingSoonLink feature="Our research page" className="font-bold text-duo-blue hover:underline">
          research shows that it works
        </ComingSoonLink>
        ! With quick, bite-sized lessons, you&apos;ll earn points and unlock new levels while gaining real-world
        communication skills.
      </>
    ),
    poster: "/landing/free-fun-effective.svg",
    animation: { src: "/landing/lottie/free-fun-effective.json", loopFrom: 291 },
    textLeft: 0,
    imageLeft: 590,
  },
  {
    title: "backed by science",
    body: "We use a combination of research-backed teaching methods and delightful content to create courses that effectively teach reading, writing, listening, and speaking skills!",
    poster: "/landing/backed-by-science.svg",
    animation: { src: "/landing/lottie/backed-by-science.json", loopFrom: 190 },
    textLeft: 515,
    imageLeft: -100,
  },
  {
    title: "stay motivated",
    body: "We make it easy to form a habit of language learning with game-like features, fun challenges, and reminders from our friendly mascot, Duo the owl.",
    poster: "/landing/stay-motivated.svg",
    animation: { src: "/landing/lottie/stay-motivated.json" },
    textLeft: 0,
    imageLeft: 590,
  },
  {
    title: "personalized learning",
    body: "Combining the best of AI and language science, lessons are tailored to help you learn at just the right level and pace.",
    poster: "/landing/personalized-learning.svg",
    animation: { src: "/landing/lottie/personalized-learning.json" },
    textLeft: 485,
    imageLeft: -130,
  },
];

/** The light-blue band: four feature rows followed by "learn anytime, anywhere". */
export function FeatureSections() {
  return (
    <div className="overflow-hidden bg-duo-blue-tint pt-10 lg:pt-24">
      {FEATURES.map((feature) => (
        <FeatureRow key={feature.title} {...feature} />
      ))}
      <LearnAnywhere />
    </div>
  );
}
