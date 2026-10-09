import { Settings } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

/**
 * No profile picture yet: Duolingo's empty avatar on a light blue banner. On phones, which have no MORE
 * menu, the banner also carries the way to settings.
 */
export function AvatarBanner() {
  return (
    <div className="relative h-[180px] overflow-hidden rounded-[15px] bg-duo-blue-tint sm:h-[224px]">
      <Image
        src="/app/profile/avatar.svg"
        width={144}
        height={266}
        alt=""
        priority
        className="absolute top-[30px] left-1/2 w-[116px] -translate-x-1/2 sm:top-[39px] sm:w-[144px]"
      />
      <Link
        href="/settings/preferences"
        aria-label="Settings"
        className="absolute top-3 right-3 rounded-xl p-1.5 text-duo-blue outline-none hover:bg-page/40 focus-visible:ring-4 focus-visible:ring-duo-blue-border md:hidden"
      >
        <Settings className="size-7" strokeWidth={2.5} />
      </Link>
    </div>
  );
}
