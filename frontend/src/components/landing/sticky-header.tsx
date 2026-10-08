"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Logo } from "@/components/brand/logo";
import { buttonClasses } from "@/components/ui/button";
import { cn } from "@/lib/cn";

type StickyHeaderProps = {
  /** Element id of the hero call-to-action. The bar slides in once it has scrolled off the top. */
  heroCtaId: string;
};

export function StickyHeader({ heroCtaId }: StickyHeaderProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const target = document.getElementById(heroCtaId);
    if (!target) return;

    const observer = new IntersectionObserver(([entry]) => {
      setVisible(!entry.isIntersecting && entry.boundingClientRect.top < 0);
    });
    observer.observe(target);
    return () => observer.disconnect();
  }, [heroCtaId]);

  return (
    <div
      inert={!visible}
      className={cn(
        "fixed inset-x-0 top-0 z-40 border-b-2 border-line bg-white transition-transform duration-300 ease-out",
        visible ? "translate-y-0" : "-translate-y-full",
      )}
    >
      <div className="mx-auto flex h-[70px] max-w-[1020px] items-center justify-between px-4">
        <Link href="/" aria-label="Home">
          <Logo className="hidden md:block" />
          <Logo variant="icon" className="md:hidden" />
        </Link>
        <Link href="/learn" className={buttonClasses({ size: "md" })}>
          Get started
        </Link>
      </div>
    </div>
  );
}
