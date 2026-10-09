"use client";

import { useState } from "react";

import { cn } from "@/lib/cn";

const TABS = [
  { id: "following", label: "Following", empty: "Not following anyone yet" },
  { id: "followers", label: "Followers", empty: "No followers yet" },
] as const;

/** The profile's Following / Followers card. Friends are a placeholder (the brief allows it), so both are empty. */
export function FriendsCard() {
  const [active, setActive] = useState<(typeof TABS)[number]["id"]>("following");
  const tab = TABS.find((t) => t.id === active) ?? TABS[0];
  return (
    <section className="overflow-hidden rounded-2xl border-2 border-line">
      <div role="tablist" aria-label="Friends" className="flex border-b-2 border-line">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={t.id === active}
            onClick={() => setActive(t.id)}
            className={cn(
              "-mb-0.5 h-[50px] flex-1 border-b-2 text-[15px] font-bold tracking-[0.8px] uppercase outline-none focus-visible:bg-snow",
              t.id === active ? "border-duo-blue text-duo-blue" : "border-transparent text-ink-soft hover:text-ink",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>
      <p role="tabpanel" className="px-6 py-[38px] text-center text-[19px] leading-5 text-ink">
        {tab.empty}
      </p>
    </section>
  );
}
