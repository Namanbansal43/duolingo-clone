"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";

import { Flag } from "@/components/icons/flag";
import { comingSoon } from "@/lib/coming-soon";
import { CURRENT_SITE_LANGUAGE, SITE_LANGUAGES } from "@/lib/languages";
import { cn } from "@/lib/cn";

/** "SITE LANGUAGE: ENGLISH" menu. Opens on hover like duolingo.com, and on click for touch and keyboard. */
export function SiteLanguagePicker() {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const current = SITE_LANGUAGES.find((language) => language.id === CURRENT_SITE_LANGUAGE);

  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  return (
    <div
      ref={rootRef}
      className="relative"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        // Hover already opens it on desktop; a click must not toggle it closed again.
        onClick={() => setOpen(true)}
        className="flex h-[70px] items-center gap-2 text-[14px] font-bold uppercase tracking-[0.7px] text-ink-faint outline-none focus-visible:underline"
      >
        Site language: {current?.nativeName}
        <ChevronDown className="size-5 stroke-[2]" />
      </button>

      {open && (
        <ul
          role="menu"
          aria-label="Site language"
          className="absolute right-0 top-[58px] z-50 grid w-[412px] grid-cols-2 gap-x-2 rounded-2xl border-2 border-line bg-white px-6 py-4 before:absolute before:-top-[9px] before:right-[18px] before:size-4 before:rotate-45 before:border-l-2 before:border-t-2 before:border-line before:bg-white"
        >
          {SITE_LANGUAGES.map((language) => (
            <li key={language.id} role="none">
              <button
                type="button"
                role="menuitem"
                onClick={() => {
                  setOpen(false);
                  if (language.id !== CURRENT_SITE_LANGUAGE) comingSoon(`${language.nativeName} site language`);
                }}
                className={cn(
                  "flex w-full items-center gap-4 rounded-lg py-[9px] text-left text-[15px] font-normal text-ink-soft hover:text-ink",
                  language.id === CURRENT_SITE_LANGUAGE && "text-ink",
                )}
              >
                <Flag code={language.flag} width={22} />
                <span className="truncate">{language.nativeName}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
