/**
 * Reads text aloud with the browser's own text-to-speech (the Web Speech API): no audio files, no keys.
 * How it sounds depends on the voices installed with the browser; without a voice for the language,
 * nothing is played.
 */

const LOCALES: Record<string, string> = { es: "es-ES", en: "en-US" };

export function canSpeak(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

export function speak(text: string, language: string, { slow = false } = {}): void {
  if (!canSpeak()) return;
  const synth = window.speechSynthesis;
  synth.cancel(); // a new sentence interrupts the last one, as tapping does on Duolingo
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = LOCALES[language] ?? language;
  const voice = synth.getVoices().find((v) => v.lang.toLowerCase().startsWith(language));
  if (voice) utterance.voice = voice;
  utterance.rate = slow ? 0.6 : 0.95;
  synth.speak(utterance);
}
