import Image from "next/image";

import type { FlagCode } from "@/lib/languages";
import { cn } from "@/lib/cn";

type FlagProps = {
  code: FlagCode;
  /** Rendered width in px; height follows the 36:28 flag ratio. */
  width?: number;
  className?: string;
};

/** Rounded flag tile, as used in the course strip and language pickers. */
export function Flag({ code, width = 36, className }: FlagProps) {
  return (
    <Image
      src={`/landing/flags/${code}.svg`}
      width={width}
      height={Math.round((width * 28) / 36)}
      alt=""
      aria-hidden
      className={cn("shrink-0", className)}
    />
  );
}
