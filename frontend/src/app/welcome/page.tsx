import type { Metadata } from "next";

import { WelcomeFlow } from "@/components/onboarding/welcome-flow";

export const metadata: Metadata = {
  title: "Get started",
};

export default function WelcomePage() {
  return <WelcomeFlow />;
}
