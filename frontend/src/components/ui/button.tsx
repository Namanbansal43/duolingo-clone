import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

/*
 * Duolingo's "3D" button: a solid face sitting on a darker ledge.
 * The ledge is a hard box-shadow. Pressing moves the face down onto
 * the ledge, which is what gives the button its tactile feel.
 */

const variants = {
  primary:
    "bg-duo-green text-white shadow-[0_4px_0_var(--color-duo-green-shade)] hover:bg-duo-green-hover",
  secondary:
    "bg-duo-blue text-white shadow-[0_4px_0_var(--color-duo-blue-shade)] hover:bg-duo-blue-hover",
  danger:
    "bg-duo-red text-white shadow-[0_4px_0_var(--color-duo-red-shade)] hover:brightness-105",
  super:
    "bg-duo-purple text-white shadow-[0_4px_0_var(--color-duo-purple-shade)] hover:brightness-105",
  // White button with a grey outline: 2px border plus a 2px ledge.
  outline:
    "border-2 border-line bg-white text-duo-blue shadow-[0_2px_0_var(--color-line)] hover:bg-snow active:translate-y-[2px]",
  // White button for dark backgrounds (Super section).
  white: "bg-white text-super-ink shadow-[0_4px_0_var(--color-super-ledge)] hover:brightness-95",
  ghost: "bg-transparent text-ink-faint hover:bg-snow active:translate-y-0",
} as const;

const sizes = {
  sm: "h-10 rounded-xl px-4 text-[13px]",
  md: "h-11 rounded-xl px-5 text-[14px]",
  lg: "h-[50px] rounded-xl px-4 text-[14px]",
} as const;

export type ButtonVariant = keyof typeof variants;
export type ButtonSize = keyof typeof sizes;

type ButtonStyleOptions = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  className?: string;
};

/** Class list for anything that should look like a button (e.g. a Next.js Link). */
export function buttonClasses({
  variant = "primary",
  size = "md",
  fullWidth = false,
  className,
}: ButtonStyleOptions = {}) {
  return cn(
    "inline-flex select-none items-center justify-center gap-2 whitespace-nowrap",
    "font-bold uppercase tracking-[0.7px] transition-[background-color,filter,transform] duration-100",
    "outline-none focus-visible:ring-4 focus-visible:ring-duo-blue-border",
    "active:translate-y-[4px] active:shadow-none",
    "disabled:pointer-events-none disabled:bg-line disabled:text-ink-faint disabled:shadow-none",
    variants[variant],
    sizes[size],
    fullWidth && "w-full",
    className,
  );
}

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & Omit<ButtonStyleOptions, "className">;

export function Button({ variant, size, fullWidth, className, type = "button", ...props }: ButtonProps) {
  return (
    <button
      type={type}
      className={buttonClasses({ variant, size, fullWidth, className })}
      {...props}
    />
  );
}
