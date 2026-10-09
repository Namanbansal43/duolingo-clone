"use client";

import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";

import { AchievementBadge } from "@/components/achievements/achievement-badge";
import { PageColumns } from "@/components/app/page-columns";
import { PageError } from "@/components/app/page-error";
import { RightRail } from "@/components/app/right-rail";
import { Flag } from "@/components/icons/flag";
import { ComingSoonLink } from "@/components/landing/coming-soon-link";
import { getAchievements, getMe, getXpHistory } from "@/lib/api/endpoints";
import type { Me } from "@/lib/api/types";
import { useApi } from "@/lib/api/use-api";
import { cn } from "@/lib/cn";
import { isFlagCode } from "@/lib/languages";

import { AvatarBanner } from "./avatar-banner";
import { FriendsCard } from "./friends-card";
import { GuestProfile } from "./guest-profile";
import { XpChart } from "./xp-chart";

async function loadProfile() {
  const [me, achievements, week] = await Promise.all([getMe(), getAchievements(), getXpHistory(7)]);
  return { me, achievements, week };
}

/**
 * /profile: the learner's own profile, laid out like a profile on duolingo.com: avatar, name and join
 * date, then statistics, XP this week and achievements. A guest is asked to create a profile instead.
 */
export function ProfileView() {
  const profile = useApi(loadProfile);

  if (profile.status === "loading") return <ProfileSkeleton />;
  if (profile.status === "error") return <PageError message={profile.error.message} onRetry={profile.retry} />;

  const { me, achievements, week } = profile.data;
  if (me.is_guest) {
    return (
      <PageColumns me={me} rail={<RightRail me={me} />}>
        <GuestProfile />
      </PageColumns>
    );
  }
  return (
    <PageColumns
      me={me}
      rail={
        <RightRail me={me}>
          <FriendsCard />
        </RightRail>
      }
    >
      <div className="px-4 pt-4 pb-12 md:px-0 lg:pt-0">
        <ProfileHeader me={me} />

        <Section title="Statistics">
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              icon={me.streak.length > 0 ? "/app/profile/streak.svg" : "/app/profile/streak-off.svg"}
              value={me.streak.length}
              label="Day streak"
              muted={me.streak.length === 0}
            />
            <StatCard icon="/app/profile/xp.svg" value={me.total_xp} label="Total XP" muted={me.total_xp === 0} />
            {/* Leagues open after 10 lessons; until then there is no league to show. */}
            <StatCard icon="/app/profile/league-none.svg" value="None" label="Current league" muted />
            <StatCard icon="/app/profile/top-three-off.svg" value={0} label="Top 3 finishes" muted />
          </div>
        </Section>

        <Section title="XP this week">
          <XpChart name={me.display_name} days={week} />
        </Section>

        <Section
          title="Achievements"
          action={
            <Link
              href="/profile/achievements"
              className="text-[15px] leading-[18px] font-bold tracking-[0.8px] text-duo-blue uppercase hover:brightness-110"
            >
              View all
            </Link>
          }
        >
          <div className="grid grid-cols-4 gap-2 rounded-2xl border-2 border-line p-4 sm:flex sm:gap-4 sm:p-6 sm:pb-[34px]">
            {achievements.map((achievement) => (
              <AchievementBadge key={achievement.key} achievement={achievement} className="w-full sm:w-[89px]" />
            ))}
          </div>
        </Section>
      </div>
    </PageColumns>
  );
}

function ProfileHeader({ me }: { me: Me }) {
  const joined = new Date(me.joined_at).toLocaleDateString("en-US", { month: "long", year: "numeric" });
  const course = me.active_course;
  return (
    <header className="border-b-2 border-line pb-8">
      <AvatarBanner />
      <div className="mt-7 flex items-end justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-[28px] leading-[34px] font-bold text-ink-strong">{me.display_name}</h1>
          <p className="text-[17px] leading-5 font-medium text-ink-faint">{me.username}</p>
          <p className="mt-1.5 text-[17px] leading-5 font-medium text-ink-soft">Joined {joined}</p>
          <p className="mt-3.5 flex gap-5 text-[16px] leading-[19px] font-bold tracking-[0.8px] text-duo-blue">
            <ComingSoonLink feature="Friends" className="hover:brightness-110">
              0 Following
            </ComingSoonLink>
            <ComingSoonLink feature="Friends" className="hover:brightness-110">
              0 Followers
            </ComingSoonLink>
          </p>
        </div>
        {course && isFlagCode(course.learning_language) && (
          <span title={course.title} className="mb-0.5 shrink-0">
            <Flag code={course.learning_language} width={31} className="rounded-[18%]" />
          </span>
        )}
      </div>
    </header>
  );
}

function Section({ title, action, children }: { title: string; action?: ReactNode; children: ReactNode }) {
  return (
    <section className="mt-8">
      <div className="flex items-center justify-between">
        <h2 className="text-[24px] leading-[26px] font-bold text-ink-strong">{title}</h2>
        {action}
      </div>
      <div className="mt-3">{children}</div>
    </section>
  );
}

type StatCardProps = { icon: string; value: number | string; label: string; muted?: boolean };

function StatCard({ icon, value, label, muted = false }: StatCardProps) {
  return (
    <div className="flex items-start gap-2.5 rounded-2xl border-2 border-line px-3 py-[15px] sm:gap-3 sm:px-6">
      <Image src={icon} width={24} height={29} alt="" className="h-[26px] w-6 shrink-0 object-contain" />
      <div className="min-w-0">
        <p className={cn("text-[20px] leading-5 font-bold", muted ? "text-ink-faint" : "text-ink-strong")}>{value}</p>
        <p className="mt-1 text-[16px] leading-5 font-medium text-ink-faint">{label}</p>
      </div>
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div aria-busy className="mx-auto flex max-w-[1056px] gap-12 px-4 pt-[58px] md:px-6 lg:pt-6">
      <div className="mx-auto w-full max-w-[592px] lg:mx-0">
        <div className="h-[180px] animate-pulse rounded-[15px] bg-snow sm:h-[224px]" />
        <div className="mt-7 h-[34px] w-40 animate-pulse rounded-lg bg-snow" />
        <div className="mt-2 h-5 w-56 animate-pulse rounded-lg bg-snow" />
        <div className="mt-[86px] grid grid-cols-2 gap-3">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-[78px] animate-pulse rounded-2xl bg-snow" />
          ))}
        </div>
      </div>
      <div className="hidden w-[368px] shrink-0 flex-col gap-6 lg:flex">
        <div className="h-11 animate-pulse rounded-xl bg-snow" />
        <div className="h-[152px] animate-pulse rounded-2xl bg-snow" />
      </div>
    </div>
  );
}
