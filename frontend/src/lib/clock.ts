/**
 * The app's time as the browser sees it. The server's clock can run ahead of real time (the demo tools'
 * "Advance a day"), so countdowns such as the next heart or the end of the league week measure from the
 * server's time: every response with the learner carries it as `now`, and the gap to this device's clock
 * is kept here. It also absorbs a device clock that is simply wrong.
 */
let offsetMs = 0;

export function syncClock<T extends { now: string }>(data: T): T {
  offsetMs = new Date(data.now).getTime() - Date.now();
  return data;
}

/** Milliseconds since the epoch on the app's clock. */
export function appNow(): number {
  return Date.now() + offsetMs;
}
