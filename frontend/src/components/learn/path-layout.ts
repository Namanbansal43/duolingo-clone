import type { PathNode } from "@/lib/api/types";

/** Horizontal offsets (px) that make nodes snake down the path, as measured on duolingo.com. */
const SWAY = [0, 45, 70, 45, 0, -45, -70, -45];

/**
 * Where a node sits relative to the path's centre line. Units alternate which way they swing first,
 * and the unit review trophy always sits on the centre line.
 */
export function nodeOffset(unitIndex: number, nodeIndex: number, node: PathNode): number {
  if (node.kind === "review") return 0;
  const direction = unitIndex % 2 === 0 ? -1 : 1;
  return direction * SWAY[nodeIndex % SWAY.length];
}

/** Units in a section share its colour; this course is a single green section. */
export const UNIT_COLOR = {
  face: "var(--color-duo-green)",
  ledge: "#46a302", // the face colour under a 20% black overlay, like Duolingo's node ledges
};

export const LOCKED_COLOR = {
  face: "var(--color-line)",
  ledge: "#b7b7b7",
};

export const SECTION_LABEL = "Section 1";
