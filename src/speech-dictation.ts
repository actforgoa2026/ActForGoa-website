export type SpeechResult = {isFinal: boolean; 0: {transcript: string}};
export type SpeechSession = {
 lang: string; continuous: boolean; interimResults: boolean;
 onresult: ((event: {resultIndex: number; results: ArrayLike<SpeechResult>}) => void) | null;
 onerror: ((event: {error: string}) => void) | null;
 onend: (() => void) | null;
 start: () => void; stop: () => void; abort: () => void;
};
export type SpeechConstructor = new () => SpeechSession;
type Callbacks = {onFinal: (text: string) => void; onInterim: (text: string) => void; onState: (listening: boolean, message: string) => void};
const errorMessage = (error: string) => error === 'not-allowed' || error === 'service-not-allowed' ? 'Microphone access was not allowed. Enable it in your browser settings or keep typing.' : error === 'no-speech' ? 'No speech was detected. Try dictating again or keep typing.' : error === 'audio-capture' ? 'No microphone was found. Connect one or keep typing.' : 'Dictation stopped. Check your connection and try again, or keep typing.';

/** A single, explicitly started recognition session. There is no automatic restart. */
export function createDictationSession(Speech: SpeechConstructor, language: string, callbacks: Callbacks) {
 const recognition = new Speech();
 const finalized = new Set<number>();
 let disposed = false, failed = false, listening = false;
 let timer: ReturnType<typeof setTimeout> | undefined;
 recognition.lang = language;
 recognition.continuous = true;
 recognition.interimResults = true;
 recognition.onresult = event => {
  if (disposed || !listening) return;
  const pending: string[] = [];
  for (let i = 0; i < event.results.length; i++) {
   const result = event.results[i];
   if (result.isFinal) {
    if (!finalized.has(i)) {finalized.add(i); callbacks.onFinal(result[0].transcript);}
   } else pending.push(result[0].transcript);
  }
  callbacks.onInterim(pending.join(' '));
 };
 recognition.onerror = event => {
  if (disposed) return;
  failed = true; listening = false;
  clearTimeout(timer);
  callbacks.onInterim('');
  callbacks.onState(false, errorMessage(event.error));
 };
 recognition.onend = () => {
  if (disposed) return;
  listening = false;
  clearTimeout(timer);
  callbacks.onInterim('');
  if (!failed) callbacks.onState(false, 'Dictation stopped. Review the text before continuing.');
 };
 return {
  start() {
   if (disposed || listening) return;
   listening = true;
   callbacks.onState(true, 'Listening. Speak clearly, then choose Stop dictating.');
   try {recognition.start(); if (listening) timer = setTimeout(() => recognition.stop(), 60000);}
   catch {failed = true; listening = false; callbacks.onState(false, 'Dictation could not start. Try again or keep typing.');}
  },
  stop() {if (!disposed && listening) {callbacks.onState(true, 'Finishing dictation…'); recognition.stop();}},
  dispose() {
   disposed = true; listening = false; clearTimeout(timer);
   recognition.onresult = null; recognition.onerror = null; recognition.onend = null;
   recognition.abort();
  },
 };
}
