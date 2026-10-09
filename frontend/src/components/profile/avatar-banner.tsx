import Image from "next/image";

/** No profile picture yet: Duolingo's empty avatar on a light blue banner. */
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
    </div>
  );
}
