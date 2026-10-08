import Link from "next/link";

import { Logo } from "@/components/brand/logo";

import { SiteLanguagePicker } from "./site-language-picker";

/** Top bar of the landing page. It scrolls away with the hero; see StickyHeader for the fixed bar. */
export function SiteHeader() {
  return (
    <header className="relative z-30 h-[70px]">
      <div className="mx-auto flex h-full max-w-[1020px] items-center justify-center px-4 md:justify-between">
        <Link href="/" aria-label="Home" className="rounded-lg outline-none focus-visible:ring-4 focus-visible:ring-duo-blue-border">
          <Logo priority />
        </Link>
        <div className="hidden md:block">
          <SiteLanguagePicker />
        </div>
      </div>
    </header>
  );
}
