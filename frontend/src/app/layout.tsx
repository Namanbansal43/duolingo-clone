import type { Metadata, Viewport } from "next";
import { Fredoka, Signika } from "next/font/google";

import { Toaster } from "@/components/ui/toaster";
import { siteConfig } from "@/config/site";
import { PreferencesProvider } from "@/lib/preferences";
import { THEME_SCRIPT } from "@/lib/theme";

import "./globals.css";

// Closest free matches to Duolingo's proprietary fonts:
// Signika stands in for "duolingo-sans" (UI text), Fredoka for "feather" (display headings).
const signika = Signika({
  subsets: ["latin"],
  variable: "--font-signika",
});

const fredoka = Fredoka({
  subsets: ["latin"],
  weight: ["600"],
  variable: "--font-fredoka",
});

export const metadata: Metadata = {
  title: {
    default: siteConfig.title,
    template: `%s | ${siteConfig.brand}`,
  },
  description: siteConfig.description,
};

export const viewport: Viewport = {
  themeColor: "#58cc02",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // The theme script sets data-theme on <html> before React hydrates, so React shouldn't flag it.
    <html lang="en" className={`${signika.variable} ${fredoka.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className="min-h-svh">
        <PreferencesProvider>{children}</PreferencesProvider>
        <Toaster />
      </body>
    </html>
  );
}
