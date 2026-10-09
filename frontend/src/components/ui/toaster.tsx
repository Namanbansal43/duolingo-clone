"use client";

import { Toaster as Sonner } from "sonner";

/** App-wide toast host, styled like the app's bordered cards. */
export function Toaster() {
  return (
    <Sonner
      position="top-center"
      toastOptions={{
        unstyled: true,
        classNames: {
          toast:
            "flex w-[356px] items-center gap-3 rounded-2xl border-2 border-line bg-page px-4 py-3 font-extrabold text-ink shadow-[0_4px_0_var(--color-line)]",
        },
      }}
    />
  );
}
