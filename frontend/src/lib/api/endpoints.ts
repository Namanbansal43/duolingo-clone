import { syncClock } from "@/lib/clock";

import { apiFetch } from "./client";
import type {
  Achievement,
  AnswerBody,
  AnswerResult,
  CatalogCourse,
  ChestReward,
  Completion,
  CoursePath,
  DailyXp,
  DemoClock,
  Leaderboard,
  LessonSession,
  Me,
  MeUpdate,
  Onboarding,
  UserSettings,
} from "./types";

const post = (body?: unknown): RequestInit => ({
  method: "POST",
  body: body === undefined ? undefined : JSON.stringify(body),
});

const patch = (body: unknown): RequestInit => ({ method: "PATCH", body: JSON.stringify(body) });

/** Every response with the learner carries the app's time; countdowns on the page measure from it. */
const learner = (path: string, init?: RequestInit) => apiFetch<Me>(path, init).then(syncClock);

export const getMe = () => learner("/me");

export const updateMe = (changes: MeUpdate) => learner("/me", patch(changes));

export const completeOnboarding = (choices: Onboarding) => learner("/me/onboarding", post(choices));

export const refillHearts = () => learner("/me/hearts/refill", post());

export const getSettings = () => apiFetch<UserSettings>("/me/settings");

export const updateSettings = (changes: Partial<UserSettings>) =>
  apiFetch<UserSettings>("/me/settings", patch(changes));

export const getAchievements = () => apiFetch<Achievement[]>("/me/achievements");

/** XP per day for the last `days` days, ending today; oldest first. */
export const getXpHistory = (days = 7) => apiFetch<DailyXp[]>(`/me/xp-history?days=${days}`);

/** This week's league. Reading it brings the rivals' XP up to now and ranks any week that has ended. */
export const getLeaderboard = () => apiFetch<Leaderboard>("/leaderboard");

export const getCourses = () => apiFetch<CatalogCourse[]>("/courses");

export const getPath = (courseId: number) => apiFetch<CoursePath>(`/courses/${courseId}/path`);

export const openChest = (nodeId: number) => apiFetch<ChestReward>(`/skills/${nodeId}/open-chest`, post());

/** Starts the node's next lesson (or practice, for a completed node); the lesson page then plays it. */
export const startSession = (nodeId: number) => apiFetch<LessonSession>("/sessions", post({ skill_id: nodeId }));

export const getCurrentSession = () => apiFetch<LessonSession>("/sessions/current");

export const answerExercise = (sessionId: number, exerciseId: number, answer: AnswerBody) =>
  apiFetch<AnswerResult>(`/sessions/${sessionId}/answers`, post({ exercise_id: exerciseId, ...answer }));

export const completeSession = (sessionId: number) => apiFetch<Completion>(`/sessions/${sessionId}/complete`, post());

export const quitSession = (sessionId: number) => apiFetch<null>(`/sessions/${sessionId}/quit`, post());

// Demo tools on the settings page

export const getDemoClock = () => apiFetch<DemoClock>("/demo/clock");

/** Moves the app's clock forward a day: streaks, hearts and the league week all follow it. */
export const advanceDemoDay = () => apiFetch<DemoClock>("/demo/clock/advance", post());

export const emptyHearts = () => learner("/demo/hearts/empty", post());

/** Back to the seeded learner and real time; preferences are kept. */
export const resetDemo = () => learner("/demo/reset", post());
