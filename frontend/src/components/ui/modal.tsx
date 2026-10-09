"use client";

import { useEffect, type ReactNode } from "react";

import { cn } from "@/lib/cn";

type ModalProps = {
  label: string;
  /** Escape and a click on the backdrop call this; leave it out for a modal that must be answered. */
  onClose?: () => void;
  children: ReactNode;
  className?: string;
};

/** A white card over a dimmed page. */
export function Modal({ label, onClose, children, className }: ModalProps) {
  useEffect(() => {
    if (!onClose) return;
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onPointerDown={(event) => event.target === event.currentTarget && onClose?.()}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={label}
        className={cn("w-full max-w-[384px] animate-pop-in rounded-2xl bg-white p-6 text-center", className)}
      >
        {children}
      </div>
    </div>
  );
}
