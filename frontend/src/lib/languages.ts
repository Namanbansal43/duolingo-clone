/*
 * Course and site-language lists for the marketing pages.
 * Each flag code matches a file in /public/landing/flags.
 */

export type FlagCode =
  | "en" | "chess" | "math" | "es" | "fr" | "de" | "it" | "pt" | "nl" | "ja" | "ar" | "cs"
  | "cy" | "da" | "el" | "eo" | "fi" | "ga" | "gd" | "he" | "hi" | "ht" | "hu" | "hv"
  | "haw" | "id" | "ko" | "la" | "nb" | "nv" | "pl" | "ro" | "ru" | "sv" | "sw" | "tlh"
  | "tr" | "uk" | "vi" | "yi" | "zh" | "zu";

export type Course = {
  flag: FlagCode;
  label: string;
  /** Only courses with seeded content can be started; the rest show "coming soon". */
  available: boolean;
};

const course = (flag: FlagCode, label: string, available = false): Course => ({ flag, label, available });

/** Same order as the course strip on duolingo.com. */
export const COURSES: Course[] = [
  course("en", "English"),
  course("chess", "Chess"),
  course("math", "Math"),
  course("es", "Spanish", true),
  course("fr", "French"),
  course("de", "German"),
  course("it", "Italian"),
  course("pt", "Portuguese"),
  course("nl", "Dutch"),
  course("ja", "Japanese"),
  course("ar", "Arabic"),
  course("cs", "Czech"),
  course("cy", "Welsh"),
  course("da", "Danish"),
  course("el", "Greek"),
  course("eo", "Esperanto"),
  course("fi", "Finnish"),
  course("ga", "Irish"),
  course("gd", "Scottish Gaelic"),
  course("he", "Hebrew"),
  course("hi", "Hindi"),
  course("ht", "Haitian Creole"),
  course("hu", "Hungarian"),
  course("hv", "High Valyrian"),
  course("haw", "Hawaiian"),
  course("id", "Indonesian"),
  course("ko", "Korean"),
  course("la", "Latin"),
  course("nb", "Norwegian (Bokmål)"),
  course("nv", "Navajo"),
  course("pl", "Polish"),
  course("ro", "Romanian"),
  course("ru", "Russian"),
  course("sv", "Swedish"),
  course("sw", "Swahili"),
  course("tlh", "Klingon"),
  course("tr", "Turkish"),
  course("uk", "Ukrainian"),
  course("vi", "Vietnamese"),
  course("yi", "Yiddish"),
  course("zh", "Chinese (Simplified)"),
  course("zu", "Zulu"),
];

export type SiteLanguage = {
  id: string;
  nativeName: string;
  flag: FlagCode;
};

/** UI languages, in duolingo.com's order. Only English is implemented. */
export const SITE_LANGUAGES: SiteLanguage[] = [
  { id: "ar", nativeName: "العربية", flag: "ar" },
  { id: "bn", nativeName: "বাংলা", flag: "hi" },
  { id: "cs", nativeName: "Čeština", flag: "cs" },
  { id: "de", nativeName: "Deutsch", flag: "de" },
  { id: "el", nativeName: "Ελληνικά", flag: "el" },
  { id: "en", nativeName: "English", flag: "en" },
  { id: "es", nativeName: "Español", flag: "es" },
  { id: "fr", nativeName: "Français", flag: "fr" },
  { id: "hi", nativeName: "हिंदी", flag: "hi" },
  { id: "hu", nativeName: "Magyar", flag: "hu" },
  { id: "id", nativeName: "Bahasa Indonesia", flag: "id" },
  { id: "it", nativeName: "Italiano", flag: "it" },
  { id: "ja", nativeName: "日本語", flag: "ja" },
  { id: "kn", nativeName: "ಕನ್ನಡ", flag: "hi" },
  { id: "ko", nativeName: "한국어", flag: "ko" },
  { id: "mr", nativeName: "मराठी", flag: "hi" },
  { id: "nl", nativeName: "Nederlands", flag: "nl" },
  { id: "pa", nativeName: "ਪੰਜਾਬੀ", flag: "hi" },
  { id: "pl", nativeName: "Polski", flag: "pl" },
  { id: "pt", nativeName: "Português", flag: "pt" },
  { id: "ro", nativeName: "Română", flag: "ro" },
  { id: "ru", nativeName: "Русский", flag: "ru" },
  { id: "sv", nativeName: "svenska", flag: "sv" },
  { id: "ta", nativeName: "தமிழ்", flag: "hi" },
  { id: "te", nativeName: "తెలుగు", flag: "hi" },
  { id: "tr", nativeName: "Türkçe", flag: "tr" },
  { id: "uk", nativeName: "Українською", flag: "uk" },
  { id: "vi", nativeName: "Tiếng Việt", flag: "vi" },
  { id: "zh", nativeName: "中文", flag: "zh" },
];

export const CURRENT_SITE_LANGUAGE = "en";
