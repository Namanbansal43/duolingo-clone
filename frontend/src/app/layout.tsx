import type { Metadata, Viewport } from "next";
import { Fredoka, Signika } from "next/font/google";

import { Toaster } from "@/components/ui/toaster";
import { siteConfig } from "@/config/site";

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
    <html lang="en" className={`${signika.variable} ${fredoka.variable}`}>
      <body className="min-h-svh">
        {children}
        <Toaster />
      </body>
    </html>
  );
}
