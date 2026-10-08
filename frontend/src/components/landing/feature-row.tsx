import type { CSSProperties, ReactNode } from "react";

import { AnimatedIllustration, type AnimationLayer } from "./animated-illustration";

export type FeatureRowProps = {
  title: string;
  body: ReactNode;
  /** Static SVG shown before (or instead of) the animation. */
  poster: string;
  animation: AnimationLayer;
  /** Optional call-to-action under the paragraph. */
  action?: ReactNode;
  /*
   * Desktop layout, in px from the row's left edge, measured from duolingo.com.
   * The 530px illustrations deliberately overhang the 988px content column.
   */
  textLeft: number;
  imageLeft: number;
};

/**
 * Heading + paragraph beside a 530px illustration.
 * Stacked and centred below the lg breakpoint, text first.
 */
export function FeatureRow({ title, body, poster, animation, action, textLeft, imageLeft }: FeatureRowProps) {
  return (
    <section
      className="relative mx-auto max-w-[1020px] px-4 py-10 lg:flex lg:h-[530px] lg:items-center lg:py-0"
      style={{ "--text-left": `${textLeft}px`, "--image-left": `${imageLeft}px` } as CSSProperties}
    >
      <div className="mx-auto max-w-[473px] text-center lg:mr-0 lg:ml-[var(--text-left)] lg:text-left">
        <h2 className="font-display text-[40px] font-semibold leading-[1.15] tracking-[0.02em] text-duo-green lg:w-[505px] lg:text-[50px] lg:leading-[60px] lg:tracking-[0.02em]">
          {title}
        </h2>
        <p className="mt-4 text-[17px] font-medium leading-6 text-ink-soft lg:mt-6">{body}</p>
        {action && <div className="mt-8 flex justify-center lg:justify-start">{action}</div>}
      </div>

      <AnimatedIllustration
        posters={[poster]}
        layers={[animation]}
        width={530}
        height={530}
        className="mx-auto mt-6 w-full max-w-[360px] lg:absolute lg:top-0 lg:left-[var(--image-left)] lg:mt-0 lg:size-[530px] lg:max-w-none"
      />
    </section>
  );
}
