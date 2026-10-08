import { apiFetch } from "./client";
import type { CatalogCourse, ChestReward, CoursePath, Me, MeUpdate } from "./types";

export const getMe = () => apiFetch<Me>("/me");

export const updateMe = (changes: MeUpdate) =>
  apiFetch<Me>("/me", { method: "PATCH", body: JSON.stringify(changes) });

export const getCourses = () => apiFetch<CatalogCourse[]>("/courses");

export const getPath = (courseId: number) => apiFetch<CoursePath>(`/courses/${courseId}/path`);

export const openChest = (nodeId: number) => apiFetch<ChestReward>(`/skills/${nodeId}/open-chest`, { method: "POST" });
