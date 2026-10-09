import { cn } from "@/lib/cn";

type SwitchProps = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  /** The visible label's id. */
  labelledBy: string;
};

/** duolingo.com's settings toggle: a blue (or grey) track under a square knob with a 3D bottom edge. */
export function Switch({ checked, onChange, labelledBy }: SwitchProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-labelledby={labelledBy}
      onClick={() => onChange(!checked)}
      className="group relative h-[31px] w-14 shrink-0 rounded-[10px] outline-none focus-visible:ring-4 focus-visible:ring-duo-blue-border"
    >
      <span
        className={cn(
          "absolute inset-x-0 top-1/2 h-[23px] -translate-y-1/2 rounded-full transition-colors",
          checked ? "bg-duo-blue" : "bg-line",
        )}
      />
      <span
        className={cn(
          "absolute top-0 size-[31px] rounded-[10px] border-2 border-b-4 bg-page transition-[left,border-color]",
          checked ? "left-[25px] border-duo-blue" : "left-0 border-line",
        )}
      />
    </button>
  );
}
