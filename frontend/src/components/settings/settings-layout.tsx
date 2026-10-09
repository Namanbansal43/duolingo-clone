"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { comingSoon } from "@/lib/coming-soon";

type NavLink = { label: string; href?: string };
type NavGroup = { title: string; links: NavLink[] };

/**
 * The settings sections, grouped as on duolingo.com. Only Preferences (and this clone's demo tools) are
 * built; the rest are the "settings placeholders" the brief allows. A guest sees the shorter guest menu.
 */
function navGroups(isGuest: boolean): NavGroup[] {
  const account: NavLink[] = isGuest
    ? [{ label: "Preferences", href: "/settings/preferences" }, { label: "Privacy settings" }]
    : [
        { label: "Preferences", href: "/settings/preferences" },
        { label: "Profile" },
        { label: "Notifications" },
        { label: "Courses" },
        { label: "Privacy settings" },
      ];
  return [
    { title: "Account", links: account },
    ...(isGuest ? [] : [{ title: "Subscription", links: [{ label: "Choose a plan" }] }]),
    { title: "Demo", links: [{ label: "Demo tools", href: "/settings/demo" }] },
    { title: "Support", links: isGuest ? [{ label: "Help Center" }] : [{ label: "Help Center" }, { label: "Feedback" }] },
  ];
}

/**
 * A settings page. Wide screens: the section on the left and the settings menu as cards on the right,
 * measured from duolingo.com (a 560px column, a 48px gap, a 368px rail). Narrower ones: a top bar with
 * a back arrow and the section's title, the section, then the menu.
 */
type SettingsLayoutProps = {
  title: string;
  isGuest: boolean;
  /** A short explanation under the title. */
  intro?: ReactNode;
  children: ReactNode;
};

export function SettingsLayout({ title, isGuest, intro, children }: SettingsLayoutProps) {
  const groups = navGroups(isGuest);
  return (
    <>
      <header className="sticky top-0 z-20 flex h-14 items-center border-b-2 border-line bg-page px-4 lg:hidden">
        <Link
          href="/profile"
          aria-label="Back to profile"
          className="rounded-lg p-1 text-ink-faint outline-none hover:text-ink-soft focus-visible:ring-4 focus-visible:ring-duo-blue-border"
        >
          <ArrowLeft className="size-6" strokeWidth={2.5} />
        </Link>
        <h1 className="mr-8 flex-1 text-center text-[19px] font-bold text-ink-faint">{title}</h1>
      </header>
      <div className="mx-auto flex max-w-[1056px] gap-12 md:px-6">
        <main className="mx-auto w-full max-w-[560px] min-w-0 px-4 pb-12 max-lg:[&>section:first-of-type]:mt-6 md:px-0 lg:mx-0 lg:flex-1 lg:pt-6">
          <div className="lg:mb-[51px]">
            <h1 className="hidden text-[32px] leading-8 font-bold text-ink lg:block">{title}</h1>
            {intro && <p className="mt-6 text-[17px] leading-[26px] text-ink-soft lg:mt-4">{intro}</p>}
          </div>
          {children}
          <div className="mt-10 flex flex-col gap-4 lg:hidden">
            <SettingsMenu groups={groups} />
          </div>
        </main>
        <aside className="hidden w-[368px] shrink-0 lg:block">
          <div className="sticky top-0 flex flex-col gap-4 py-6">
            <SettingsMenu groups={groups} />
          </div>
        </aside>
      </div>
    </>
  );
}

function SettingsMenu({ groups }: { groups: NavGroup[] }) {
  const pathname = usePathname();
  return groups.map((group) => (
    <nav key={group.title} aria-label={group.title} className="rounded-2xl border-2 border-line px-6 py-6 lg:px-[46px]">
      <h2 className="text-[23px] leading-[30px] font-bold text-ink-soft">{group.title}</h2>
      <ul className="mt-[14px]">
        {group.links.map((link) => (
          <li key={link.label}>
            {link.href ? (
              <Link
                href={link.href}
                aria-current={pathname === link.href ? "page" : undefined}
                className="block py-[9px] text-[19px] leading-[26px] font-bold text-ink outline-none hover:text-duo-blue focus-visible:text-duo-blue"
              >
                {link.label}
              </Link>
            ) : (
              <button
                type="button"
                onClick={() => comingSoon(link.label)}
                className="block w-full py-[9px] text-left text-[19px] leading-[26px] font-bold text-ink outline-none hover:text-duo-blue focus-visible:text-duo-blue"
              >
                {link.label}
              </button>
            )}
          </li>
        ))}
      </ul>
    </nav>
  ));
}

/** A section of a settings page: a grey heading over its rows, ruled on wide screens and boxed on phones. */
export function SettingsSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="mt-10 lg:mt-9">
      <h2 className="text-[17px] leading-6 font-bold text-ink-soft lg:border-b-2 lg:border-line lg:pb-3 lg:text-[24px] lg:leading-[30px]">
        {title}
      </h2>
      <div className="mt-3 divide-y-2 divide-line rounded-2xl border-2 border-line px-4 lg:mt-2 lg:divide-y-0 lg:rounded-none lg:border-0 lg:px-0">
        {children}
      </div>
    </section>
  );
}

/** One setting: its label (and an optional explanation) on the left, the control on the right. */
export function SettingsRow({
  id,
  label,
  description,
  children,
}: {
  id: string;
  label: string;
  description?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="flex min-h-[66px] items-center justify-between gap-6 py-3 lg:min-h-14 lg:py-2">
      <div className="min-w-0">
        <p id={id} className="text-[17px] leading-6 font-bold text-ink lg:text-[19px]">
          {label}
        </p>
        {description && <p className="mt-1 text-[15px] leading-[22px] text-ink-soft">{description}</p>}
      </div>
      {children}
    </div>
  );
}
