import { ChevronDown } from "lucide-react";

type SelectFieldProps<T extends string> = {
  id: string;
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
};

/** duolingo.com's settings dropdown: a bordered, uppercase box with a chevron, over the native select. */
export function SelectField<T extends string>({ id, value, options, onChange }: SelectFieldProps<T>) {
  return (
    <div className="relative">
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value as T)}
        className="h-12 w-full cursor-pointer appearance-none rounded-xl border-2 border-b-4 border-line bg-page pr-12 pl-3 text-[13px] font-bold tracking-[0.8px] text-ink-soft uppercase outline-none hover:bg-snow focus-visible:border-duo-blue-border"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown
        aria-hidden
        strokeWidth={3}
        className="pointer-events-none absolute top-1/2 right-4 size-5 -translate-y-[60%] text-ink-faint"
      />
    </div>
  );
}
