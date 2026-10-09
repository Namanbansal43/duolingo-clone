import type { Metadata } from "next";

import { LessonPlayer } from "@/components/lesson/lesson-player";

export const metadata: Metadata = { title: "Lesson" };

/** The full-screen lesson, outside the app shell: no sidebar, just the lesson. */
export default function LessonPage() {
  return <LessonPlayer />;
}
