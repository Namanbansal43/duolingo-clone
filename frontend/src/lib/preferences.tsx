"use client";

import { usePathname } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { toast } from "sonner";

import { getSettings, updateSettings } from "@/lib/api/endpoints";
import type { UserSettings } from "@/lib/api/types";
import { isAppPath, readStoredDarkMode, storeDarkMode } from "@/lib/theme";

/** Duolingo's defaults, used until the learner's own settings arrive (or if they can't be loaded). */
export const DEFAULT_SETTINGS: UserSettings = {
  sound_effects: true,
  animations: true,
  motivational_messages: true,
  listening_exercises: true,
  dark_mode: "system",
};

type Preferences = {
  /** Null while the learner's settings load. */
  settings: UserSettings | null;
  /** Saves some preferences; the page follows at once, and goes back if saving fails. */
  update: (changes: Partial<UserSettings>) => Promise<void>;
};

const PreferencesContext = createContext<Preferences | null>(null);

/**
 * The learner's preferences, loaded once when they first open an app page. The ones that change the
 * whole page are applied to <html>: dark mode as data-theme and animations as data-animations.
 */
export function PreferencesProvider({ children }: { children: ReactNode }) {
  const themed = isAppPath(usePathname());
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const requested = useRef(false);

  useEffect(() => {
    if (!themed || requested.current) return;
    requested.current = true;
    getSettings().then(setSettings, () => setSettings(DEFAULT_SETTINGS));
  }, [themed]);

  useEffect(() => {
    if (settings) storeDarkMode(settings.dark_mode);
  }, [settings]);

  // Layout effects, so a page never paints in the wrong theme while moving in or out of the app.
  const darkMode = settings?.dark_mode ?? null;
  useLayoutEffect(() => {
    if (!themed) return;
    const choice = darkMode ?? readStoredDarkMode();
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      const dark = choice === "on" || (choice === "system" && media.matches);
      document.documentElement.dataset.theme = dark ? "dark" : "light";
    };
    apply();
    media.addEventListener("change", apply);
    return () => {
      media.removeEventListener("change", apply);
      delete document.documentElement.dataset.theme;
    };
  }, [themed, darkMode]);

  const animationsOff = themed && settings?.animations === false;
  useLayoutEffect(() => {
    if (!animationsOff) return;
    document.documentElement.dataset.animations = "off";
    return () => {
      delete document.documentElement.dataset.animations;
    };
  }, [animationsOff]);

  const update = useCallback(
    async (changes: Partial<UserSettings>) => {
      const before = settings;
      setSettings({ ...(settings ?? DEFAULT_SETTINGS), ...changes });
      try {
        setSettings(await updateSettings(changes));
      } catch (error) {
        setSettings(before);
        toast(error instanceof Error ? error.message : "Couldn't save that change. Please try again.");
      }
    },
    [settings],
  );

  const value = useMemo(() => ({ settings, update }), [settings, update]);
  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}

export function usePreferences(): Preferences {
  const preferences = useContext(PreferencesContext);
  if (!preferences) throw new Error("usePreferences must be used inside PreferencesProvider");
  return preferences;
}
