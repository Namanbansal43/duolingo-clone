"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { openChest } from "@/lib/api/endpoints";
import type { CoursePath as CoursePathData, PathNode } from "@/lib/api/types";
import { comingSoon } from "@/lib/coming-soon";

import { PathUnit } from "./path-unit";
import { UnitHeader } from "./unit-header";

// Where the sticky unit header ends; a unit counts as "current" once its top scrolls past this.
const HEADER_BOTTOM = 150;

type CoursePathProps = {
  path: CoursePathData;
  /** Called after something changes the learner's state (opening a chest), to reload path and stats. */
  onChange: () => Promise<void>;
};

export function CoursePath({ path, onChange }: CoursePathProps) {
  const [openNodeId, setOpenNodeId] = useState<number | null>(null);
  const [currentUnit, setCurrentUnit] = useState(0);
  const sections = useRef<(HTMLElement | null)[]>([]);

  // The sticky header names the unit being scrolled through.
  useEffect(() => {
    const onScroll = () => {
      let index = 0;
      sections.current.forEach((section, i) => {
        if (section && section.getBoundingClientRect().top <= HEADER_BOTTOM) index = i;
      });
      setCurrentUnit(index);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Start with the next node to play in view.
  useEffect(() => {
    if (path.active_node_id === null) return;
    document.querySelector(`[data-node-id="${path.active_node_id}"]`)?.scrollIntoView({ block: "center" });
  }, [path.active_node_id]);

  // A popover closes on Escape or a click anywhere outside the path nodes.
  useEffect(() => {
    if (openNodeId === null) return;
    const onPointerDown = (event: PointerEvent) => {
      if (!(event.target as Element).closest("[data-path-node]")) setOpenNodeId(null);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpenNodeId(null);
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [openNodeId]);

  const select = async (node: PathNode) => {
    if (node.kind === "chest" && node.state === "active") {
      setOpenNodeId(null);
      try {
        const reward = await openChest(node.id);
        toast(`You found ${reward.gems_awarded} gems!`);
        await onChange();
      } catch (error) {
        toast(error instanceof Error ? error.message : "Couldn't open the chest. Please try again.");
      }
      return;
    }
    setOpenNodeId((current) => (current === node.id ? null : node.id));
  };

  const start = () => comingSoon("Lessons");

  return (
    <>
      <UnitHeader unit={path.units[currentUnit]} />
      {path.units.map((unit, index) => (
        <PathUnit
          key={unit.id}
          ref={(section) => {
            sections.current[index] = section;
          }}
          unit={unit}
          index={index}
          openNodeId={openNodeId}
          onSelect={select}
          onStart={start}
        />
      ))}
    </>
  );
}
