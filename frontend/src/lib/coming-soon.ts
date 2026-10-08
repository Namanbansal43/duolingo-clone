import { toast } from "sonner";

/** Standard feedback for features the brief allows to stay as placeholders. */
export function comingSoon(feature: string) {
  toast(`${feature} is coming soon!`, { id: `coming-soon:${feature}` });
}
