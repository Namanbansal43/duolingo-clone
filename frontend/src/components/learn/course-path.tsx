"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { OutOfHearts } from "@/components/app/out-of-hearts";
import { ApiError } from "@/lib/api/client";
import { openChest, startSession } from "@/lib/api/endpoints";
import type { CoursePath as CoursePathData, Hearts, PathNode } from "@/lib/api/types";

import { PathUnit } from "./path-unit";
import { UnitHeader } from "./unit-header";

// Where the sticky unit header ends; a unit counts as "current" once its top scrolls past this.
const HEADER_BOTTOM = 150;

type CoursePathProps = {
  path: CoursePathData;
  hearts: Hearts;
  /** Called after something changes the learner's state (a chest, a refill), to reload path and stats. */
  onChange: () => Promise<void>;
};

export function CoursePath({ path, hearts, onChange }: CoursePathProps) {
  const router = useRouter();
  const [openNodeId, setOpenNodeId] = useState<number | null>(null);
  const [starting, setStarting] = useState(false);
  const [outOfHearts, setOutOfHearts] = useState(false);
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

  // START (or PRACTICE) creates the session on the server, then the lesson page plays it.
  const start = async (node: PathNode) => {
    if (starting) return;
    setStarting(true);
    try {
      await startSession(node.id);
      router.push("/lesson");
    } catch (error) {
      if (error instanceof ApiError && error.code === "out_of_hearts") setOutOfHearts(true);
      else toast(error instanceof Error ? error.message : "Couldn't start the lesson. Please try again.");
    } finally {
      // Next.js keeps this page's state while the lesson plays, so leave it ready for coming back.
      setStarting(false);
      setOpenNodeId(null);
    }
  };

  // Practicing the latest finished node earns a heart back.
  const practiceNode = path.units
    .flatMap((unit) => unit.nodes)
    .filter((node) => node.state === "completed" && node.kind !== "chest")
    .at(-1);

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
          onStart={(node) => void start(node)}
        />
      ))}
      {outOfHearts && (
        <OutOfHearts
          hearts={hearts}
          onRefilled={() => {
            setOutOfHearts(false);
            void onChange();
          }}
          onPractice={practiceNode ? () => start(practiceNode) : undefined}
          onNoThanks={() => setOutOfHearts(false)}
        />
      )}
    </>
  );
}
