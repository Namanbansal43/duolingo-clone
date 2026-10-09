import type { Metadata } from "next";

import { AchievementsView } from "@/components/profile/achievements-view";

export const metadata: Metadata = {
  title: "Achievements",
};

export default function AchievementsPage() {
  return <AchievementsView />;
}
