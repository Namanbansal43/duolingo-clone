"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/cn";
import { comingSoon } from "@/lib/coming-soon";

import { NAV_ITEMS } from "./nav-items";

/** The bottom navigation on phones, in place of the sidebar. */
export function TabBar() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-30 flex h-[82px] items-center justify-around border-t-2 border-line bg-white px-2 md:hidden"
    >
      {NAV_ITEMS.filter((item) => item.inTabBar).map((item) => {
        const active = item.href !== null && pathname.startsWith(item.href);
        const classes = cn(
          "flex size-12 items-center justify-center rounded-xl border-2 outline-none focus-visible:ring-4 focus-visible:ring-duo-blue-border",
          active ? "border-duo-blue-border bg-duo-blue-tint" : "border-transparent",
        );
        const icon = <Image src={item.icon} width={32} height={32} alt="" />;
        return item.href ? (
          <Link key={item.label} href={item.href} aria-label={item.label} aria-current={active ? "page" : undefined} className={classes}>
            {icon}
          </Link>
        ) : (
          <button key={item.label} type="button" aria-label={item.label} className={classes} onClick={() => comingSoon(item.label)}>
            {icon}
          </button>
        );
      })}
    </nav>
  );
}
