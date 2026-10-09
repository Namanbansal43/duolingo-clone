import { Button } from "@/components/ui/button";

/** Shown in place of a page whose data couldn't be loaded. */
export function PageError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex min-h-[60svh] flex-col items-center justify-center gap-6 px-4 text-center">
      <p className="text-[17px] text-ink-soft">{message}</p>
      <Button variant="secondary" onClick={onRetry}>
        Try again
      </Button>
    </div>
  );
}
