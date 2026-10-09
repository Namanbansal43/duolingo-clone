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
  Leaderboard,
  LessonSession,
  Me,
  MeUpdate,
  Onboarding,
} from "./types";

const post = (body?: unknown): RequestInit => ({
  method: "POST",
  body: body === undefined ? undefined : JSON.stringify(body),
});

export const getMe = () => apiFetch<Me>("/me");

export const updateMe = (changes: MeUpdate) =>
  apiFetch<Me>("/me", { method: "PATCH", body: JSON.stringify(changes) });

export const completeOnboarding = (choices: Onboarding) => apiFetch<Me>("/me/onboarding", post(choices));

export const refillHearts = () => apiFetch<Me>("/me/hearts/refill", post());

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
