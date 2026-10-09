"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/cn";
import { comingSoon } from "@/lib/coming-soon";

import { MoreMenu } from "./more-menu";
import { NAV_ITEMS, type NavItem } from "./nav-items";

/**
 * The left navigation on tablets and desktops: icons only below 1160px, icons and labels above
 * (measured from duolingo.com: 88px and 256px wide).
 */
export function Sidebar() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Main"
      className="fixed inset-y-0 left-0 z-30 hidden w-[88px] flex-col border-r-2 border-line bg-page px-4 md:flex wide:w-[256px]"
    >
      <Link
        href="/learn"
        aria-label="Learn"
        className="mt-9 mb-6 ml-2.5 self-start rounded-lg outline-none focus-visible:ring-4 focus-visible:ring-duo-blue-border wide:mt-8 wide:mb-[30px] wide:ml-4"
      >
        <Image src="/app/logo-mark.svg" width={40} height={40} alt="" priority className="wide:hidden" />
        <Image src="/app/logo-wordmark.svg" width={128} height={30} alt="" priority className="hidden wide:block" />
      </Link>
      <ul className="flex flex-col gap-2">
        {NAV_ITEMS.map((item) => (
          <li key={item.label}>
            {item.menu ? (
              <MoreMenu trigger={({ open, toggle }) => <SidebarItem item={item} active={false} open={open} onClick={toggle} />} />
            ) : (
              <SidebarItem item={item} active={item.href !== null && pathname.startsWith(item.href)} />
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}

type SidebarItemProps = {
  item: NavItem;
  active: boolean;
  /** The item's menu is showing (MORE). */
  open?: boolean;
  onClick?: () => void;
};

function SidebarItem({ item, active, open, onClick }: SidebarItemProps) {
  const classes = cn(
    "flex h-[52px] w-full items-center justify-center rounded-xl border-2 px-2 py-1 outline-none transition-colors wide:justify-start",
    "focus-visible:ring-4 focus-visible:ring-duo-blue-border",
    active ? "border-duo-blue-border bg-duo-blue-tint" : cn("border-transparent hover:bg-snow", open && "bg-snow"),
  );
  const content = (
    <>
      <span className="flex w-8 shrink-0 justify-center wide:w-[38px] wide:justify-end">
        <Image src={item.icon} width={32} height={32} alt="" />
      </span>
      <span
        className={cn(
          "ml-5 hidden text-[15px] leading-[25px] font-bold tracking-[0.8px] uppercase wide:inline",
          active ? "text-duo-blue" : "text-ink-soft",
        )}
      >
        {item.label}
      </span>
    </>
  );

  return item.href ? (
    <Link href={item.href} aria-current={active ? "page" : undefined} aria-label={item.label} className={classes}>
      {content}
    </Link>
  ) : (
    <button
      type="button"
      aria-label={item.label}
      aria-haspopup={item.menu ? "menu" : undefined}
      aria-expanded={item.menu ? Boolean(open) : undefined}
      className={classes}
      onClick={onClick ?? (() => comingSoon(item.label))}
    >
      {content}
    </button>
  );
}
