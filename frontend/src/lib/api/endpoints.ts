import { apiFetch } from "./client";
import type { CatalogCourse, Me, MeUpdate } from "./types";

export const getMe = () => apiFetch<Me>("/me");

export const updateMe = (changes: MeUpdate) =>
  apiFetch<Me>("/me", { method: "PATCH", body: JSON.stringify(changes) });

export const getCourses = () => apiFetch<CatalogCourse[]>("/courses");
