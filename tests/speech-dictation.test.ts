import test from 'node:test';
import assert from 'node:assert/strict';
import {createDictationSession, type SpeechSession} from '../src/speech-dictation';

class FakeSpeech implements SpeechSession {
 static last: FakeSpeech;
 lang = ''; continuous = false; interimResults = false;
 starts = 0; stops = 0; aborts = 0;
 onresult: SpeechSession['onresult'] = null;
 onerror: SpeechSession['onerror'] = null;
 onend: SpeechSession['onend'] = null;
 constructor() {FakeSpeech.last = this;}
 start() {this.starts++;}
 stop() {this.stops++;}
 abort() {this.aborts++;}
}
function setup() {
 const finals: string[] = [], interim: string[] = [], states: [boolean, string][] = [];
 const session = createDictationSession(FakeSpeech, 'en-IN', {onFinal: text => finals.push(text), onInterim: text => interim.push(text), onState: (active, message) => states.push([active, message])});
 return {session, speech: FakeSpeech.last, finals, interim, states};
}

test('dictation starts only when requested and appends each final result once', () => {
 const {session, speech, finals, interim, states} = setup();
 assert.equal(speech.starts, 0);
 session.start(); session.start();
 assert.equal(speech.starts, 1);
 assert.equal(states[0][0], true);
 assert.equal(speech.lang, 'en-IN');
 speech.onresult!({resultIndex: 0, results: [{isFinal: false, 0: {transcript: 'I saw'}}]});
 assert.deepEqual(finals, []);
 assert.equal(interim.at(-1), 'I saw');
 const result = {resultIndex: 0, results: [{isFinal: true, 0: {transcript: 'I saw burning'}}]};
 speech.onresult!(result); speech.onresult!(result);
 assert.deepEqual(finals, ['I saw burning']);
 speech.onresult!({resultIndex: 1, results: [...result.results, {isFinal: true, 0: {transcript: 'beside the road'}}]});
 assert.deepEqual(finals, ['I saw burning', 'beside the road']);
 session.dispose();
});

test('stop ends recording without submitting or restarting', () => {
 const {session, speech, states} = setup();
 session.start(); session.stop();
 assert.equal(speech.stops, 1);
 speech.onend!();
 assert.equal(states.at(-1)![0], false);
 assert.equal(speech.starts, 1);
 session.dispose();
});

test('permission failures stay visible when the recognition session ends', () => {
 const {session, speech, states} = setup();
 session.start();
 speech.onerror!({error: 'not-allowed'});
 speech.onend!();
 assert.equal(states.at(-1)![0], false);
 assert.match(states.at(-1)![1], /Microphone access was not allowed/);
 assert.equal(speech.starts, 1);
 session.dispose();
});

test('unmount aborts and prevents late speech events updating the form', () => {
 const {session, speech, finals, states} = setup();
 session.start();
 const lateResult = speech.onresult!, lateEnd = speech.onend!;
 const count = states.length;
 session.dispose();
 assert.equal(speech.aborts, 1);
 assert.equal(speech.onresult, null);
 lateResult({resultIndex: 0, results: [{isFinal: true, 0: {transcript: 'late words'}}]});
 lateEnd();
 assert.deepEqual(finals, []);
 assert.equal(states.length, count);
});

test('a start failure returns an actionable error', () => {
 class FailingSpeech extends FakeSpeech {start() {throw new Error('unavailable');}}
 const states: [boolean, string][] = [];
 const session = createDictationSession(FailingSpeech, 'en-IN', {onFinal: () => {}, onInterim: () => {}, onState: (active, message) => states.push([active, message])});
 session.start();
 assert.equal(states.at(-1)![0], false);
 assert.match(states.at(-1)![1], /could not start/);
 session.dispose();
});
