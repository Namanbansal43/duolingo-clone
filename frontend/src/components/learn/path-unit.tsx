import Image from "next/image";
import type { Ref } from "react";

import { AnimatedIllustration } from "@/components/ui/animated-illustration";
import type { PathNode as PathNodeData, PathUnit as PathUnitData } from "@/lib/api/types";
import { cn } from "@/lib/cn";

import { nodeOffset } from "./path-layout";
import { PathNode } from "./path-node";

const DUO = [{ src: "/app/path/duo.json" }];
// Greyed-out characters stand beside units that are still locked.
const LOCKED_CHARACTERS = ["/app/path/character-2-locked.svg", "/app/path/character-3-locked.svg"];

type PathUnitProps = {
  unit: PathUnitData;
  index: number;
  openNodeId: number | null;
  onSelect: (node: PathNodeData) => void;
  onStart: (node: PathNodeData) => void;
  ref?: Ref<HTMLElement>;
};

export function PathUnit({ unit, index, openNodeId, onSelect, onStart, ref }: PathUnitProps) {
  const unlocked = unit.nodes.some((node) => node.state !== "locked");
  return (
    <section ref={ref} aria-label={`Unit ${unit.position}: ${unit.title}`} className="relative pb-6">
      {index > 0 && (
        <header className="mt-2 flex h-[82px] items-center gap-4">
          <hr className="flex-1 border-t-2 border-line" />
          <h2 className="max-w-[60%] text-center text-[19px] leading-[26.6px] font-bold text-ink-faint">{unit.title}</h2>
          <hr className="flex-1 border-t-2 border-line" />
        </header>
      )}
      <PathCharacter index={index} unlocked={unlocked} />
      {/* The first unit leaves room under the header for the START bubble. */}
      <div className={cn("relative flex flex-col gap-6", index === 0 ? "pt-[81px]" : "pt-8")}>
        {unit.nodes.map((node, nodeIndex) => (
          <PathNode
            key={node.id}
            node={node}
            offset={nodeOffset(index, nodeIndex, node)}
            roomForBubble={node.state === "active" && node.kind !== "chest" && nodeIndex > 0}
            open={openNodeId === node.id}
            onSelect={onSelect}
            onStart={onStart}
          />
        ))}
      </div>
    </section>
  );
}

/**
 * The character beside each unit, on the side the path bends away from (positions from duolingo.com).
 * Duo is animated once a unit is reached; later units show a greyed-out character until then.
 */
function PathCharacter({ index, unlocked }: { index: number; unlocked: boolean }) {
  const onRight = index % 2 === 0;
  return (
    <div
      aria-hidden
      className={cn(
        "pointer-events-none absolute h-[261px] -translate-y-1/2",
        index === 0 ? "top-[290px]" : "top-[360px]",
        onRight ? "left-[calc(50%-19px)] w-[calc(50%+3px)]" : "right-[calc(50%-14px)] w-[calc(50%-2px)]",
      )}
    >
      {unlocked || index === 0 ? (
        <AnimatedIllustration
          posters={["/app/path/duo.svg"]}
          layers={DUO}
          width={1080}
          height={1080}
          className="mx-auto aspect-square h-full"
        />
      ) : (
        <Image
          src={LOCKED_CHARACTERS[(index - 1) % LOCKED_CHARACTERS.length]}
          width={278}
          height={261}
          alt=""
          className="mx-auto h-full w-auto dark:opacity-40"
        />
      )}
    </div>
  );
}
