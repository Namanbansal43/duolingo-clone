import Image from "next/image";

import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";

/** "Wait, don't go!": shown when quitting a lesson that has progress to lose. */
export function QuitDialog({ onStay, onQuit }: { onStay: () => void; onQuit: () => void }) {
  return (
    <Modal label="Quit lesson?" onClose={onStay}>
      <Image src="/app/lesson/quit-duo.svg" width={120} height={120} alt="" className="mx-auto size-[120px]" />
      <h2 className="mt-4 text-[24px] leading-8 font-bold text-ink">
        Wait, don&rsquo;t go! You&rsquo;ll lose your progress if you quit now
      </h2>
      <Button variant="secondary" size="lg" fullWidth onClick={onStay} autoFocus className="mt-8">
        Keep learning
      </Button>
      <button
        type="button"
        onClick={onQuit}
        className="mt-4 w-full rounded-xl py-1.5 text-[15px] font-bold tracking-[0.7px] text-duo-red uppercase hover:bg-snow"
      >
        End session
      </button>
    </Modal>
  );
}
