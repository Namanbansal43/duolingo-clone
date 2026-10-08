import Image from "next/image";
import type { CSSProperties } from "react";

import type { PathNode as PathNodeData } from "@/lib/api/types";
import { cn } from "@/lib/cn";

import { LOCKED_COLOR, UNIT_COLOR } from "./path-layout";

type PathNodeProps = {
  node: PathNodeData;
  offset: number;
  /** Extra room above, so the START bubble doesn't cover the node before it. */
  roomForBubble: boolean;
  open: boolean;
  onSelect: (node: PathNodeData) => void;
  onStart: (node: PathNodeData) => void;
};

/** One stop on the path, with its popover. The row spans the column so the popover stays centred on it. */
export function PathNode({ node, offset, roomForBubble, open, onSelect, onStart }: PathNodeProps) {
  return (
    <div data-path-node data-node-id={node.id} className={cn("relative h-[65px] w-full", roomForBubble && "mt-7", open && "z-20")}>
      <div className="absolute top-0 left-1/2" style={{ transform: `translateX(calc(-50% + ${offset}px))` }}>
        {node.kind === "chest" ? (
          <ChestButton node={node} onSelect={onSelect} />
        ) : (
          <>
            {node.state === "active" && <ProgressRing done={node.lessons_completed} total={node.lessons_total} />}
            <NodeButton node={node} onSelect={onSelect} />
            {node.state === "active" && <StartBubble />}
          </>
        )}
      </div>
      {open && <NodePopover node={node} offset={offset} onStart={onStart} />}
    </div>
  );
}

function nodeIcon(node: PathNodeData) {
  if (node.kind === "review") return node.state === "locked" ? "/app/path/trophy-locked.svg" : "/app/path/trophy.svg";
  if (node.state === "completed") return "/app/path/check.svg";
  return node.state === "active" ? "/app/path/star.svg" : "/app/path/star-locked.svg";
}

function nodeLabel(node: PathNodeData) {
  if (node.state === "locked") return `${node.title}, locked`;
  if (node.state === "completed") return `${node.title}, completed`;
  return `${node.title}, lesson ${node.lessons_completed + 1} of ${node.lessons_total}`;
}

/**
 * A 70x57 oval face over an 8px ledge of a darker shade, built like Duolingo's: the ledge is the face's
 * shadow, and pressing slides the face down onto it.
 */
function NodeButton({ node, onSelect }: { node: PathNodeData; onSelect: (node: PathNodeData) => void }) {
  const colors = node.state === "locked" ? LOCKED_COLOR : UNIT_COLOR;
  return (
    <button
      type="button"
      onClick={() => onSelect(node)}
      aria-label={nodeLabel(node)}
      className="group relative block h-[65px] w-[70px] rounded-[50%] outline-none focus-visible:ring-4 focus-visible:ring-duo-blue-border"
      style={{ "--face": colors.face, "--ledge": colors.ledge } as CSSProperties}
    >
      {/* Fills the sides between the face and its shadow, so the button reads as a solid disc. */}
      <span className="absolute inset-x-0 top-[28.5px] h-2 bg-(--ledge)" />
      <span className="absolute inset-x-0 top-0 h-[57px] rounded-[50%] bg-(--face) shadow-[0_8px_0_var(--ledge)] transition-transform duration-100 group-active:translate-y-2 group-active:shadow-none" />
      <Image
        src={nodeIcon(node)}
        width={42}
        height={34}
        alt=""
        className="absolute top-[11.5px] left-[14px] h-[34px] w-[42px] object-contain transition-transform duration-100 group-active:translate-y-2"
      />
    </button>
  );
}

function ChestButton({ node, onSelect }: { node: PathNodeData; onSelect: (node: PathNodeData) => void }) {
  const locked = node.state === "locked";
  return (
    <button
      type="button"
      onClick={() => onSelect(node)}
      aria-label={locked ? "Treasure chest, locked" : node.state === "active" ? "Open treasure chest" : "Opened treasure chest"}
      className={cn(
        "relative -top-[12.5px] block rounded-xl outline-none focus-visible:ring-4 focus-visible:ring-duo-blue-border",
        node.state === "active" && "animate-hover-bounce",
      )}
    >
      {locked ? (
        <Image src="/app/path/chest-locked.svg" width={80} height={90} alt="" />
      ) : (
        <Image
          src="/app/cards/quest-chest.svg"
          width={80}
          height={80}
          alt=""
          className={cn("my-[5px]", node.state === "completed" && "opacity-50 grayscale-[30%]")}
        />
      )}
    </button>
  );
}

/** Grey track around the current node, filled in the unit colour as its lessons are finished. */
function ProgressRing({ done, total }: { done: number; total: number }) {
  const circumference = 2 * Math.PI * 46;
  const filled = total > 0 ? (done / total) * circumference : 0;
  return (
    <svg
      aria-hidden
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      className="pointer-events-none absolute -top-[14px] -left-[14px] h-[93px] w-[98px] -rotate-90"
    >
      <circle cx="50" cy="50" r="46" fill="none" stroke="var(--color-line)" strokeWidth="8" />
      <circle
        cx="50"
        cy="50"
        r="46"
        fill="none"
        stroke={UNIT_COLOR.face}
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={`${filled} ${circumference}`}
      />
    </svg>
  );
}

function StartBubble() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute bottom-[calc(100%+2px)] left-1/2 -translate-x-1/2 animate-hover-bounce"
    >
      <div className="relative rounded-[10px] border-2 border-line bg-white p-3 text-[17px] leading-[17px] font-bold tracking-[0.03em] text-duo-green uppercase">
        Start
        <span className="absolute -bottom-2 left-1/2 size-5 -translate-x-1/2 rotate-45 rounded-[2px] border-r-2 border-b-2 border-line bg-white" />
      </div>
    </div>
  );
}

function NodePopover({ node, offset, onStart }: { node: PathNodeData; offset: number; onStart: (node: PathNodeData) => void }) {
  const locked = node.state === "locked";
  const subtitle = locked
    ? "Complete all levels above to unlock this!"
    : node.state === "completed"
      ? "Level complete! Practice to keep it fresh."
      : `Lesson ${node.lessons_completed + 1} of ${node.lessons_total}`;

  return (
    <div
      role="dialog"
      aria-label={node.title}
      className={cn(
        "absolute top-[calc(100%+26px)] left-1/2 w-[min(295px,calc(100vw-32px))] -translate-x-1/2 rounded-[15px] p-4",
        locked ? "border-2 border-line bg-snow text-ink-faint" : "bg-duo-green text-white",
      )}
    >
      {/* The pointer stays under the node even though the card is centred on the path. */}
      <span
        aria-hidden
        className={cn(
          "absolute -top-2 size-4 -translate-x-1/2 rotate-45 rounded-[2px]",
          locked ? "-top-[9px] border-t-2 border-l-2 border-line bg-snow" : "bg-duo-green",
        )}
        style={{ left: `calc(50% + ${offset}px)` }}
      />
      <h3 className="text-[19px] leading-6 font-bold">{node.title}</h3>
      <p className="mt-2 text-[17px] leading-6">{subtitle}</p>
      <button
        type="button"
        disabled={locked}
        onClick={() => onStart(node)}
        className={cn(
          "mt-4 flex h-[46px] w-full items-center justify-center rounded-2xl text-[15px] font-bold tracking-[0.8px] uppercase outline-none",
          locked
            ? "bg-line text-ink-faint"
            : "bg-white text-duo-green shadow-[0_4px_0_rgba(0,0,0,0.15)] hover:bg-snow focus-visible:ring-4 focus-visible:ring-white/60 active:translate-y-1 active:shadow-none",
        )}
      >
        {locked ? "Locked" : node.state === "completed" ? "Practice +5 XP" : "Start +10 XP"}
      </button>
    </div>
  );
}
