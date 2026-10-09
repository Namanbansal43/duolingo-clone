"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";

import { getMe } from "@/lib/api/endpoints";
import { cn } from "@/lib/cn";
import { comingSoon } from "@/lib/coming-soon";

const PRODUCTS = [
  { label: "Duolingo English Test", icon: "/app/nav/english-test.svg" },
  { label: "Podcast", icon: "/app/nav/podcast.svg" },
];

const ITEM = "flex w-full items-center px-5 text-left text-[15px] font-bold tracking-[0.8px] text-ink-soft uppercase outline-none hover:bg-snow focus-visible:bg-snow";

/**
 * The sidebar's MORE item and its pop-up menu, opened by hovering or clicking as on duolingo.com: other
 * Duolingo products, then Settings and Help. A guest also sees Create a profile and Sign in.
 */
export function MoreMenu({ trigger }: { trigger: (props: { open: boolean; toggle: () => void }) => ReactNode }) {
  const [open, setOpen] = useState(false);
  const [guest, setGuest] = useState<boolean | null>(null);
  const root = useRef<HTMLDivElement>(null);

  // Whether to offer "Create a profile" depends on the learner; asked once, the first time it opens.
  useEffect(() => {
    if (!open || guest !== null) return;
    getMe().then(
      (me) => setGuest(me.is_guest),
      () => setGuest(false),
    );
  }, [open, guest]);

  useEffect(() => {
    if (!open) return;
    const closeOnEscape = (event: KeyboardEvent) => event.key === "Escape" && setOpen(false);
    const closeOutside = (event: PointerEvent) => {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("keydown", closeOnEscape);
    document.addEventListener("pointerdown", closeOutside);
    return () => {
      document.removeEventListener("keydown", closeOnEscape);
      document.removeEventListener("pointerdown", closeOutside);
    };
  }, [open]);

  const soon = (feature: string) => {
    setOpen(false);
    comingSoon(feature);
  };

  return (
    <div ref={root} className="relative" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      {trigger({ open, toggle: () => setOpen((value) => !value) })}
      {open && (
        // The left padding bridges the gap to the item, so the pointer can cross it without closing the menu.
        <div className="absolute -top-2.5 left-full z-40 pl-[9px]">
          <div role="menu" aria-label="More" className="w-[290px] rounded-2xl border-2 border-line bg-page py-2">
            {PRODUCTS.map((product) => (
              <button key={product.label} type="button" role="menuitem" className={cn(ITEM, "h-[52px] gap-4")} onClick={() => soon(product.label)}>
                <Image src={product.icon} width={32} height={32} alt="" className="size-8" />
                {product.label}
              </button>
            ))}
            <div className="my-2 border-t-2 border-line" />
            {guest && (
              <button type="button" role="menuitem" className={cn(ITEM, "h-10")} onClick={() => soon("Creating a profile")}>
                Create a profile
              </button>
            )}
            <Link href="/settings/preferences" role="menuitem" className={cn(ITEM, "h-10")} onClick={() => setOpen(false)}>
              Settings
            </Link>
            <button type="button" role="menuitem" className={cn(ITEM, "h-10")} onClick={() => soon("Help")}>
              Help
            </button>
            {guest && (
              <Link href="/log-in" role="menuitem" className={cn(ITEM, "h-10")} onClick={() => setOpen(false)}>
                Sign in
              </Link>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
