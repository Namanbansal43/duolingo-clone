import type { Metadata } from "next";

import { LogInView } from "@/components/auth/log-in-view";

export const metadata: Metadata = {
  title: "Log in",
};

export default function LogInPage() {
  return <LogInView />;
}
