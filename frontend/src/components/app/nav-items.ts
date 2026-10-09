export type NavItem = {
  label: string;
  /** Null until the page is built; the item then shows a "coming soon" message. */
  href: string | null;
  icon: string;
  /** Shown in the phone tab bar too (it has room for five). */
  inTabBar: boolean;
  /** Opens the MORE menu (with Settings) instead of a page. */
  menu?: boolean;
};

export const NAV_ITEMS: NavItem[] = [
  { label: "Learn", href: "/learn", icon: "/app/nav/learn.svg", inTabBar: true },
  { label: "Leaderboards", href: "/leaderboard", icon: "/app/nav/leaderboards.svg", inTabBar: true },
  { label: "Quests", href: "/quests", icon: "/app/nav/quests.svg", inTabBar: true },
  { label: "Shop", href: "/shop", icon: "/app/nav/shop.svg", inTabBar: true },
  { label: "Profile", href: "/profile", icon: "/app/nav/profile.svg", inTabBar: true },
  { label: "More", href: null, icon: "/app/nav/more.svg", inTabBar: false, menu: true },
];
