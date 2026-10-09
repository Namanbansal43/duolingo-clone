import type { Metadata } from "next";

import { DemoToolsView } from "@/components/settings/demo-tools-view";

export const metadata: Metadata = {
  title: "Demo tools",
};

export default function DemoToolsPage() {
  return <DemoToolsView />;
}
