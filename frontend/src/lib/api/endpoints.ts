import { apiFetch } from "./client";
import type { CatalogCourse, ChestReward, CoursePath, Me, MeUpdate, Onboarding } from "./types";

export const getMe = () => apiFetch<Me>("/me");

export const updateMe = (changes: MeUpdate) =>
  apiFetch<Me>("/me", { method: "PATCH", body: JSON.stringify(changes) });

export const completeOnboarding = (choices: Onboarding) =>
  apiFetch<Me>("/me/onboarding", { method: "POST", body: JSON.stringify(choices) });

export const getCourses = () => apiFetch<CatalogCourse[]>("/courses");

export const getPath = (courseId: number) => apiFetch<CoursePath>(`/courses/${courseId}/path`);

export const openChest = (nodeId: number) => apiFetch<ChestReward>(`/skills/${nodeId}/open-chest`, { method: "POST" });
