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
  /** Started over through "Get started" without creating a profile: the profile page asks for one. */
  is_guest: boolean;
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

/** An achievement with the learner's level and progress towards the next one. */
export type Achievement = {
  key: string;
  title: string;
  /** 0 until the first level is reached. */
  level: number;
  max_level: number;
  /** The learner's statistic: longest streak, total XP, lessons or perfect lessons. */
  value: number;
  /** What the next level needs; the last level's threshold once every level is reached. */
  goal: number;
  /** The goal in words, e.g. "Reach a 7 day streak". */
  description: string;
  unlocked_at: string | null;
};

/** XP earned on one calendar day (YYYY-MM-DD, the learner's time zone). */
export type DailyXp = {
  day: string;
  xp: number;
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

export type ExerciseType = "multiple_choice" | "word_bank" | "match_pairs" | "fill_blank" | "type_answer" | "listen";

export type ExerciseOption = {
  id: number;
  text: string;
};

/** One challenge of a lesson, without its solution. */
export type Exercise = {
  id: number;
  type: ExerciseType;
  instruction: string;
  /** For fill_blank the sentence contains ___; null for match_pairs. */
  prompt: string | null;
  prompt_language: string | null;
  /** Choices or word tiles, already shuffled. */
  options: ExerciseOption[];
  pairs: { left: string[]; right: string[] } | null;
};

export type LessonSession = {
  id: number;
  mode: "lesson" | "practice";
  status: "in_progress" | "completed" | "failed" | "abandoned";
  started_at: string;
  node: { id: number; title: string };
  lesson_position: number;
  lessons_total: number;
  exercises: Exercise[];
  completed_exercise_ids: number[];
  hearts: Hearts;
};

/** What a learner sends for one exercise; which field depends on its type. */
export type AnswerBody = {
  option_ids?: number[];
  text?: string;
  pair?: [string, string];
  skipped?: boolean;
};

export type Verdict = "correct" | "other_solution" | "typo" | "wrong";

export type AnswerResult = {
  correct: boolean;
  verdict: Verdict;
  solution: string | null;
  exercise_completed: boolean;
  hearts: Hearts;
};

export type Completion = {
  xp_earned: number;
  total_xp: number;
  xp_today: number;
  daily_goal_xp: number;
  accuracy: number;
  duration_seconds: number;
  streak: { length: number; longest: number; extended: boolean };
  hearts: Hearts;
  node: { id: number; lessons_completed: number; lessons_total: number; completed: boolean };
  /** Achievements that went up a level, at their new level. */
  achievements: Achievement[];
};

export type ApiErrorBody = {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
};
