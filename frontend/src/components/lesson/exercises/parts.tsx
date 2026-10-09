"use client";

import Image from "next/image";
import { Volume2 } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import { SpeechBubble } from "@/components/ui/speech-bubble";
import { cn } from "@/lib/cn";
import { canSpeak, speak } from "@/lib/speech";

/** How a tile or choice looks: idle, selected, or judged right or wrong. */
export type Tone = "idle" | "selected" | "right" | "wrong" | "done";

const TONES: Record<Tone, string> = {
  idle: "border-line bg-page text-ink hover:bg-snow",
  selected: "border-duo-blue-border bg-duo-blue-tint text-duo-blue-shade",
  right: "border-duo-green-soft bg-duo-green-tint text-duo-green-shade",
  wrong: "border-duo-red-border bg-duo-red-tint text-duo-red-shade",
  done: "pointer-events-none border-line bg-page text-line",
};

const KEY_TONES: Record<Tone, string> = {
  idle: "border-line text-ink-faint",
  selected: "border-duo-blue-border text-duo-blue-shade",
  right: "border-duo-green-soft text-duo-green-shade",
  wrong: "border-duo-red-border text-duo-red-shade",
  done: "border-line text-line",
};

type CardProps = ButtonHTMLAttributes<HTMLButtonElement> & { tone?: Tone };

/** The bordered card every choice, tile and pair is drawn on: 2px border with a 4px ledge underneath. */
export function Card({ tone = "idle", className, type = "button", ...props }: CardProps) {
  return (
    <button
      type={type}
      className={cn(
        "rounded-xl border-2 border-b-4 text-[19px] leading-[1.4] font-medium transition-colors",
        "outline-none select-none focus-visible:ring-4 focus-visible:ring-duo-blue-border",
        "active:translate-y-[2px] active:border-b-2 disabled:active:translate-y-0 disabled:active:border-b-4",
        TONES[tone],
        className,
      )}
      {...props}
    />
  );
}

/** The small boxed number on choices and pairs; pressing that number key picks it. */
export function KeyHint({ label, tone = "idle" }: { label: string; tone?: Tone }) {
  return (
    <span
      aria-hidden
      className={cn(
        "hidden size-[30px] shrink-0 items-center justify-center rounded-lg border-2 text-[15px] font-bold sm:flex",
        KEY_TONES[tone],
      )}
    >
      {label}
    </span>
  );
}

/** Blue speaker that reads Spanish aloud with the browser's voice. Hidden where the browser can't speak. */
export function SpeakButton({ text, language, className }: { text: string; language: string; className?: string }) {
  if (!canSpeak()) return null;
  return (
    <button
      type="button"
      aria-label="Listen"
      onClick={() => speak(text, language)}
      className={cn("rounded-md text-duo-blue outline-none hover:brightness-110 focus-visible:ring-4", className)}
    >
      <Volume2 className="size-7" strokeWidth={2.5} fill="currentColor" />
    </button>
  );
}

/** Duo beside a speech bubble holding the prompt, as in Duolingo's translation exercises. */
export function PromptBubble({ children, speakText, language }: { children: ReactNode; speakText?: string; language?: string | null }) {
  return (
    <div className="flex items-center">
      <Image
        src="/app/path/duo.svg"
        width={1080}
        height={1080}
        alt=""
        className="-my-[46px] -mr-[40px] -ml-[52px] size-[200px] shrink-0 sm:-my-[60px] sm:-mr-[52px] sm:-ml-[68px] sm:size-[260px]"
      />
      <SpeechBubble tail="left" className="flex items-center gap-2 leading-8">
        {speakText && language === "es" && <SpeakButton text={speakText} language="es" />}
        <span>{children}</span>
      </SpeechBubble>
    </div>
  );
}
