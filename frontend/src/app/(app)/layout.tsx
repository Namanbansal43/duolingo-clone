import type { ReactNode } from "react";

import { Sidebar } from "@/components/app/sidebar";
import { TabBar } from "@/components/app/tab-bar";

/** Shell of the signed-in app: sidebar on tablets and desktops, tab bar on phones. */
export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <Sidebar />
      <div className="pb-[82px] md:pb-0 md:pl-[88px] wide:pl-[256px]">{children}</div>
      <TabBar />
    </>
  );
}
