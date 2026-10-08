import Image from "next/image";

import type { PathUnit } from "@/lib/api/types";
import { comingSoon } from "@/lib/coming-soon";

import { SECTION_LABEL } from "./path-layout";

/** The green banner pinned above the path; it shows whichever unit is being scrolled through. */
export function UnitHeader({ unit }: { unit: PathUnit }) {
  return (
    <div className="sticky top-[58px] z-10 bg-white px-4 pb-1 md:px-0 lg:top-0 lg:pt-6 lg:pb-0">
      <div className="flex min-h-[90px] items-center justify-between gap-4 rounded-[13px] bg-duo-green py-4 pr-4 pl-4 text-white max-md:min-h-[82px] max-md:items-stretch max-md:py-0 max-md:pr-0">
        <div className="min-w-0 max-md:self-center max-md:py-3">
          <button
            type="button"
            onClick={() => comingSoon("Sections")}
            className="flex items-center gap-2 rounded-md text-[16px] leading-6 font-bold uppercase opacity-70 outline-none hover:opacity-100 focus-visible:ring-2 focus-visible:ring-white"
          >
            <Image src="/app/path/unit-back.svg" width={16} height={16} alt="" className="max-md:hidden" />
            {SECTION_LABEL}, Unit {unit.position}
          </button>
          <h2 className="mt-1.5 line-clamp-2 text-[18px] leading-6 font-bold md:truncate md:text-[22px] md:leading-7">{unit.title}</h2>
        </div>
        <button
          type="button"
          onClick={() => comingSoon("The guidebook")}
          aria-label="Guidebook"
          className="flex h-[52px] shrink-0 items-center gap-3 rounded-2xl border-2 border-black/20 px-3 text-[15px] font-bold tracking-[0.8px] uppercase shadow-[0_2px_0_rgba(0,0,0,0.2)] outline-none hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-white active:translate-y-[2px] active:shadow-none max-md:h-auto max-md:self-stretch max-md:rounded-none max-md:border-0 max-md:border-l-2 max-md:px-5 max-md:shadow-none wide:pr-[14px]"
        >
          <Image src="/app/path/guidebook.svg" width={24} height={24} alt="" />
          <span className="hidden wide:inline">Guidebook</span>
        </button>
      </div>
    </div>
  );
}
