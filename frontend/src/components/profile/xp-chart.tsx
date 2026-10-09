import type { DailyXp } from "@/lib/api/types";

const WEEKDAYS = ["Su", "M", "Tu", "W", "Th", "F", "Sa"];

// duolingo.com's chart: a 456 x 205 plot inside a 516-wide drawing, axis labels in a warm grey.
const WIDTH = 516;
const PLOT_LEFT = 45;
const PLOT_TOP = 15;
const PLOT_WIDTH = 456;
const PLOT_HEIGHT = 205;
const HEIGHT = PLOT_TOP + PLOT_HEIGHT + 30;
const GRID_LINES = 4;
const LABEL = "#cccac9";
const BLUE = "#1cb0f6";

/** "XP this week": the learner's XP on each of the last 7 days, as a line over a grid. */
export function XpChart({ name, days }: { name: string; days: DailyXp[] }) {
  const step = gridStep(Math.max(0, ...days.map((d) => d.xp)));
  const top = step * GRID_LINES;
  const x = (i: number) => (days.length > 1 ? (i * PLOT_WIDTH) / (days.length - 1) : 0);
  const y = (xp: number) => PLOT_HEIGHT - (xp / top) * PLOT_HEIGHT;
  const line = days.map((d, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(d.xp)}`).join("");
  const total = days.reduce((sum, d) => sum + d.xp, 0);

  return (
    <div className="rounded-2xl border-2 border-line px-5 pt-7 pb-4">
      <div className="flex items-center justify-between px-4 text-[19px] leading-5 font-bold text-duo-blue">
        <span className="flex items-center gap-2">
          <span aria-hidden className="size-2.5 rounded-full bg-duo-blue" />
          {name}
        </span>
        <span>{total} XP</span>
      </div>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="mt-4 w-full" role="img" aria-label={`XP earned on each of the last ${days.length} days`}>
        <g transform={`translate(${PLOT_LEFT}, ${PLOT_TOP})`} fontSize={16} fill={LABEL}>
          {Array.from({ length: GRID_LINES + 1 }, (_, i) => (
            <g key={i} transform={`translate(0, ${y(i * step)})`}>
              <line x2={PLOT_WIDTH} stroke="#dedede" strokeOpacity={0.5} strokeWidth={2} />
              <text x={-16} dy="0.32em" textAnchor="end">
                {i * step}
              </text>
            </g>
          ))}
          {days.map((d, i) => (
            <text key={d.day} x={x(i)} y={PLOT_HEIGHT + 16} dy="0.71em" textAnchor="middle">
              {weekday(d.day)}
            </text>
          ))}
          <path d={line} fill="none" stroke={BLUE} strokeOpacity={0.3} strokeWidth={2} />
          {days.map((d, i) => (
            <circle key={d.day} cx={x(i)} cy={y(d.xp)} r={3.75} fill={BLUE} stroke={BLUE} strokeWidth={2}>
              <title>{`${d.xp} XP`}</title>
            </circle>
          ))}
        </g>
      </svg>
    </div>
  );
}

/** A round gap between grid lines (1, 2 or 5 times a power of ten) so 4 of them cover the busiest day. */
function gridStep(max: number): number {
  const rough = Math.max(max, 1) / GRID_LINES;
  const power = 10 ** Math.floor(Math.log10(rough));
  const step = [1, 2, 5, 10].map((m) => m * power).find((s) => s >= rough) ?? rough;
  return Math.max(step, 5);
}

/** "Sa", "Su", ... for a YYYY-MM-DD date. */
function weekday(day: string): string {
  const [year, month, date] = day.split("-").map(Number);
  return WEEKDAYS[new Date(year, month - 1, date).getDay()];
}
