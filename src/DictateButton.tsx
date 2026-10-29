import {useEffect, useRef, useState} from 'react';
import {Mic, Square} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {appendDictation} from './dictation-text';
import {createDictationSession, type SpeechConstructor} from './speech-dictation';

export default function DictateButton({value, onChange, maxLength}: {value: string; onChange: (value: string) => void; maxLength: number}) {
 const [listening, setListening] = useState(false);
 const [message, setMessage] = useState('');
 const [interim, setInterim] = useState('');
 const current = useRef(value); current.current = value;
 const update = useRef(onChange); update.current = onChange;
 const session = useRef<ReturnType<typeof createDictationSession> | null>(null);
 useEffect(() => () => session.current?.dispose(), []);
 function toggle() {
  if (listening) {session.current?.stop(); return;}
  const browser = window as typeof window & {SpeechRecognition?: SpeechConstructor; webkitSpeechRecognition?: SpeechConstructor};
  const Speech = browser.SpeechRecognition || browser.webkitSpeechRecognition;
  if (!Speech) {setMessage('This browser does not offer dictation. Use your keyboard’s microphone or type your report.'); return;}
  session.current?.dispose();
  session.current = createDictationSession(Speech, navigator.language || 'en-IN', {
   onFinal: text => {
    const next = appendDictation(current.current, text, maxLength);
    current.current = next;
    update.current(next);
    if (next.length === maxLength) {session.current?.stop(); setMessage('The description is full. Review the text before continuing.');}
   },
   onInterim: setInterim,
   onState: (active, status) => {setListening(active); setMessage(status);},
  });
  session.current.start();
 }
 return <div className="report-dictation">
  <Button type="button" variant="secondary" size="sm" onClick={toggle} aria-pressed={listening}>{listening ? <Square size={16}/> : <Mic size={16}/>}<span>{listening ? 'Stop dictating' : 'Dictate'}</span></Button>
  <p className="report-help">Uses your browser’s speech service, which may process audio online. Nothing is submitted until you send the report.</p>
  {(message || interim) && <p className="report-dictation-status" role="status">{interim || message}</p>}
 </div>;
}
