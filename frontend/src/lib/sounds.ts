/**
 * Lesson sound effects, synthesised with the Web Audio API rather than played from files:
 * a rising two-note chime for a right answer, a low buzz for a wrong one, and a short fanfare at the end.
 */

type Note = { frequency: number; start: number; duration: number; type?: OscillatorType };

const SOUNDS: Record<"correct" | "wrong" | "complete", Note[]> = {
  correct: [
    { frequency: 880, start: 0, duration: 0.12 },
    { frequency: 1318.5, start: 0.09, duration: 0.22 },
  ],
  wrong: [
    { frequency: 196, start: 0, duration: 0.14, type: "square" },
    { frequency: 164.8, start: 0.12, duration: 0.24, type: "square" },
  ],
  complete: [
    { frequency: 523.3, start: 0, duration: 0.14 },
    { frequency: 659.3, start: 0.12, duration: 0.14 },
    { frequency: 784, start: 0.24, duration: 0.14 },
    { frequency: 1046.5, start: 0.36, duration: 0.4 },
  ],
};

let context: AudioContext | null = null;

export function playSound(name: keyof typeof SOUNDS): void {
  if (typeof window === "undefined" || !("AudioContext" in window)) return;
  context ??= new AudioContext();
  const now = context.currentTime;
  for (const note of SOUNDS[name]) {
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    oscillator.type = note.type ?? "sine";
    oscillator.frequency.value = note.frequency;
    // A quick attack and an exponential fade, so notes don't click.
    gain.gain.setValueAtTime(0.0001, now + note.start);
    gain.gain.exponentialRampToValueAtTime(note.type === "square" ? 0.05 : 0.18, now + note.start + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + note.start + note.duration);
    oscillator.connect(gain).connect(context.destination);
    oscillator.start(now + note.start);
    oscillator.stop(now + note.start + note.duration + 0.02);
  }
}
