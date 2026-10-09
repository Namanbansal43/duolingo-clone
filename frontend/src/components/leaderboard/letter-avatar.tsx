import { cn } from "@/lib/cn";

// Learners without a profile picture get their initial on a colour, picked by their id so it never changes.
const COLORS = ["#1cb0f6", "#58cc02", "#ff9600", "#ce82ff", "#ff4b4b", "#2b70c9", "#ffc800", "#00cd9c"];

/** A 48px round avatar showing the learner's initial. `dashed` is the outline used before joining a league. */
export function LetterAvatar({ id, name, dashed = false }: { id: number; name: string; dashed?: boolean }) {
  return (
    <span
      aria-hidden
      className={cn(
        "flex size-12 shrink-0 items-center justify-center rounded-full text-[22px] font-bold uppercase",
        dashed ? "border-2 border-dashed border-ink-faint text-ink-faint" : "text-white",
      )}
      style={dashed ? undefined : { backgroundColor: COLORS[id % COLORS.length] }}
    >
      {name.charAt(0)}
    </span>
  );
}
