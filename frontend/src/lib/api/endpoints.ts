import { apiFetch } from "./client";
import type {
  AnswerBody,
  AnswerResult,
  CatalogCourse,
  ChestReward,
  Completion,
  CoursePath,
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
