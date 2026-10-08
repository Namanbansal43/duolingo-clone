import Image from "next/image";

import { siteConfig } from "@/config/site";
import { cn } from "@/lib/cn";

type LogoProps = {
  /** "full" is the owl plus wordmark; "icon" is the owl alone (compact headers). */
  variant?: "full" | "icon";
  className?: string;
  priority?: boolean;
};

const LOGOS = {
  full: { src: "/landing/logo.svg", width: 179, height: 42 },
  icon: { src: "/landing/logo-icon.svg", width: 43, height: 42 },
} as const;

export function Logo({ variant = "full", className, priority }: LogoProps) {
  const logo = LOGOS[variant];
  return (
    <Image
      src={logo.src}
      width={logo.width}
      height={logo.height}
      alt={siteConfig.brand}
      priority={priority}
      className={cn("block", className)}
    />
  );
}
