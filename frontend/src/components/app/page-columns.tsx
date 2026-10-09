import type { ReactNode } from "react";

import type { Me } from "@/lib/api/types";

import { StatsBar } from "./stats-bar";

/**
 * The columns of an app page such as /learn or /profile: the page in the middle and the right rail on wide
 * screens, or a stats bar across the top on narrower ones. Widths are duolingo.com's: a main column up to
 * 592px, a 48px gap and a 368px rail.
 */
export function PageColumns({ me, rail, children }: { me: Me; rail: ReactNode; children: ReactNode }) {
  return (
    <>
      <div className="sticky top-0 z-20 bg-page lg:hidden">
        <StatsBar me={me} className="mx-auto h-[58px] max-w-[592px] px-1" />
      </div>
      <div className="mx-auto flex max-w-[1056px] gap-12 md:px-6">
        <main className="mx-auto min-w-0 max-w-[592px] flex-1 lg:mx-0 lg:pt-6">{children}</main>
        <aside className="hidden w-[368px] shrink-0 lg:block">
          <div className="sticky top-0 pt-6 pb-6">{rail}</div>
        </aside>
      </div>
    </>
  );
}
