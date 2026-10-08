"use client";

import type { ReactNode } from "react";

import { comingSoon } from "@/lib/coming-soon";

type ComingSoonLinkProps = {
  feature: string;
  className?: string;
  children: ReactNode;
};

/** Looks like a link but announces a placeholder feature instead of navigating. */
export function ComingSoonLink({ feature, className, children }: ComingSoonLinkProps) {
  return (
    <button type="button" onClick={() => comingSoon(feature)} className={className}>
      {children}
    </button>
  );
}
