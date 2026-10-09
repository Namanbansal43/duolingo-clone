/** Response and request shapes of the backend API. Field meanings are documented in docs/API.md. */

export type DailyGoalXp = 10 | 20 | 30 | 50;

export type Course = {
  id: number;
  learning_language: string;
  from_language: string;
  title: string;
  is_available: boolean;
};

export type CatalogCourse = Course & {
  learners: number;
};

export type Hearts = {
  current: number;
  max: number;
  /** ISO 8601 UTC; null when hearts are full. */
  next_heart_at: string | null;
  regen_minutes: number;
};

export type Streak = {
  length: number;
  extended_today: boolean;
  longest: number;
};

export type Me = {
  id: number;
  username: string;
  display_name: string;
  joined_at: string;
  timezone: string;
  active_course: Course | null;
  daily_goal_xp: DailyGoalXp;
  total_xp: number;
  /** XP earned today in the learner's time zone; compare with daily_goal_xp. */
  xp_today: number;
  lessons_completed: number;
  gems: number;
  hearts: Hearts;
  streak: Streak;
};

export type NodeState = "completed" | "active" | "locked";

export type PathNode = {
  id: number;
  position: number;
  title: string;
  kind: "lesson" | "chest" | "review";
  state: NodeState;
  lessons_total: number;
  lessons_completed: number;
};

export type PathUnit = {
  id: number;
  position: number;
  title: string;
  nodes: PathNode[];
};

export type CoursePath = {
  course: Course;
  units: PathUnit[];
  active_node_id: number | null;
};

export type ChestReward = {
  gems_awarded: number;
  gems: number;
};

/** PATCH /api/v1/me: omitted fields are left unchanged. */
export type MeUpdate = {
  active_course_id?: number;
  daily_goal_xp?: DailyGoalXp;
  timezone?: string;
};

/** The "Get started" choices; sending them starts the learner over. */
export type Onboarding = {
  active_course_id: number;
  daily_goal_xp: DailyGoalXp;
  timezone: string;
};

export type ApiErrorBody = {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
};
