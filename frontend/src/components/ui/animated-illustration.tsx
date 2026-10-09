"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import type { AnimationItem } from "lottie-web";

import { cn } from "@/lib/cn";

export type AnimationLayer = {
  /** Path to the Lottie JSON. */
  src: string;
  /**
   * After the first play-through: loop the whole animation (undefined),
   * loop from this frame onwards (number), or hold the last frame (null).
   */
  loopFrom?: number | null;
};

type AnimatedIllustrationProps = {
  /** Static SVGs (stacked) shown until the animation is ready, and kept when motion is off. */
  posters: string[];
  layers: AnimationLayer[];
  width: number;
  height: number;
  /** "contain" shows the whole frame; "cover-bottom" fills the box and anchors to its bottom edge. */
  fit?: "contain" | "cover-bottom";
  priority?: boolean;
  className?: string;
};

/**
 * Lottie illustration with a static poster.
 * Uses the "light" Lottie player, which renders SVG only and never evaluates the
 * JavaScript expressions some animation files carry. Animations load when the
 * illustration nears the viewport and pause while it is off-screen.
 */
export function AnimatedIllustration({
  posters,
  layers,
  width,
  height,
  fit = "contain",
  priority,
  className,
}: AnimatedIllustrationProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const layerRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const root = rootRef.current;
    // Reduced-motion users, and learners who switched Animations off in settings, keep the poster.
    const still =
      window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
      document.documentElement.dataset.animations === "off";
    if (!root || still) return;

    let animations: AnimationItem[] = [];
    let started = false;
    let cancelled = false;

    const start = async () => {
      started = true;
      const [{ default: lottie }, ...data] = await Promise.all([
        import("lottie-web/build/player/lottie_light"),
        ...layers.map((layer) => fetch(layer.src).then((response) => response.json())),
      ]);
      if (cancelled) return;

      let drawn = 0;
      animations = layers.map((layer, i) => {
        const animation = lottie.loadAnimation({
          container: layerRefs.current[i]!,
          renderer: "svg",
          loop: layer.loopFrom === undefined,
          autoplay: true,
          animationData: data[i],
          rendererSettings: {
            preserveAspectRatio: fit === "cover-bottom" ? "xMidYMax slice" : "xMidYMid meet",
          },
        });

        const { loopFrom } = layer;
        if (typeof loopFrom === "number") {
          // Play the intro once, then loop the tail of the timeline.
          animation.addEventListener("complete", () => {
            animation.loop = true;
            animation.playSegments([loopFrom, animation.firstFrame + animation.totalFrames], true);
          });
        }

        animation.addEventListener("DOMLoaded", () => {
          drawn += 1;
          if (drawn === layers.length) setReady(true);
        });
        return animation;
      });
    };

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          if (!started) void start();
          animations.forEach((animation) => animation.play());
        } else {
          animations.forEach((animation) => animation.pause());
        }
      },
      { rootMargin: "200px 0px" },
    );
    observer.observe(root);

    return () => {
      cancelled = true;
      observer.disconnect();
      animations.forEach((animation) => animation.destroy());
    };
  }, [layers, fit]);

  const posterClasses = cn("transition-opacity duration-300", ready && "opacity-0");

  return (
    <div ref={rootRef} aria-hidden className={cn("relative", className)}>
      {posters.map((poster, i) =>
        fit === "cover-bottom" ? (
          <Image key={poster} src={poster} alt="" fill sizes="100vw" priority={priority} className={cn("object-cover object-bottom", posterClasses)} />
        ) : (
          <Image
            key={poster}
            src={poster}
            alt=""
            width={width}
            height={height}
            priority={priority}
            // The first poster sets the box size; further posters stack on top of it.
            className={cn("h-auto w-full", i > 0 && "absolute inset-0", posterClasses)}
          />
        ),
      )}
      {layers.map((layer, i) => (
        <div
          key={layer.src}
          ref={(element) => {
            layerRefs.current[i] = element;
          }}
          className="absolute inset-0"
        />
      ))}
    </div>
  );
}
