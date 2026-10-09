import type { DarkModeChoice } from "@/lib/api/types";

/** The app's own pages, which follow the dark mode setting. The landing page and "Get started" stay
 * light, as on duolingo.com. */
const APP_PATH = /^\/(learn|leaderboard|quests|shop|profile|settings|lesson)(\/|$)/;

export const isAppPath = (pathname: string) => APP_PATH.test(pathname);

// The last dark mode choice, kept in the browser so the next page load paints in the right theme before
// the learner's settings arrive. The setting itself is saved on the server.
const STORAGE_KEY = "dark-mode";

/** Runs in <head> before an app page first paints, so a dark theme doesn't flash light on page load. */
export const THEME_SCRIPT = `try {
  if (${APP_PATH}.test(location.pathname)) {
    var choice = localStorage.getItem("${STORAGE_KEY}") || "system";
    var dark = choice === "on" || (choice === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }
} catch (e) {}`;

export function readStoredDarkMode(): DarkModeChoice {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored === "on" || stored === "off" ? stored : "system";
  } catch {
    return "system";
  }
}

export function storeDarkMode(choice: DarkModeChoice): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, choice);
  } catch {
    // storage unavailable: the next page load paints light until the settings arrive
  }
}
