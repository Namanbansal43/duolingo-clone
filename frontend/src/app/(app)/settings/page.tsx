import { redirect } from "next/navigation";

/** /settings opens on Preferences, the first section. */
export default function SettingsPage() {
  redirect("/settings/preferences");
}
