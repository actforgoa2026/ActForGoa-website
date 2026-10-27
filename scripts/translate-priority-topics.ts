/** Generate review-only translations for topic action labels, questions, steps and link labels.
 * Dry run: node --import tsx scripts/translate-priority-topics.ts
 * Execute: node --import tsx scripts/translate-priority-topics.ts --translate
 * Outputs /tmp/actforgoa-priority-topics.json; does not modify the site or any provider ledger.
 */
import { readFile, writeFile } from 'node:fs/promises';
import { topicFlows, topicDescriptions, type TopicAction } from '../src/topic-flows';

const output = '/tmp/actforgoa-priority-topics.json';
const keyFile = '.env.translation.local';
const texts = new Set<string>();
const add = (value?: string) => { if (value?.trim()) texts.add(value.trim()); };
function collect(actions: TopicAction[]) {
  for (const action of actions) {
    add(action.label); add(action.question);
    for (const step of action.steps ?? []) add(step);
    for (const link of action.links ?? []) add(link.label);
    if (action.choices) collect(action.choices);
  }
}
for (const flow of topicFlows) { add(flow.label); add(topicDescriptions[flow.slug]); collect(flow.actions); }
const inputs = [...texts];
const charsPerLanguage = inputs.reduce((n, value) => n + [...value].length, 0);
const MAX_ITEMS = 500, MAX_CHARS_PER_LANGUAGE = 40000;
if (inputs.length > MAX_ITEMS || charsPerLanguage > MAX_CHARS_PER_LANGUAGE) throw new Error('Scope exceeds the hard limit; review the source before increasing it.');
console.log(JSON.stringify({ strings: inputs.length, charactersPerLanguage: charsPerLanguage, languages: ['hi', 'gom'], maximumCharacters: charsPerLanguage * 2, output, mode: process.argv.includes('--translate') ? 'translate' : 'dry-run' }));
if (!process.argv.includes('--translate')) process.exit(0);
const env = await readFile(keyFile, 'utf8');
const key = env.match(/^GOOGLE_TRANSLATE_API_KEY=(.+)$/m)?.[1]?.trim();
if (!key) throw new Error('GOOGLE_TRANSLATE_API_KEY is missing from the local key file');
const results: Record<string, Record<string,string>> = {};
for (const target of ['hi', 'gom']) {
  const translations: Record<string,string> = {};
  for (let i = 0; i < inputs.length; i += 25) {
    const batch = inputs.slice(i, i + 25);
    const response = await fetch('https://translation.googleapis.com/language/translate/v2', {
      method: 'POST', headers: { 'content-type': 'application/json', 'x-goog-api-key': key },
      body: JSON.stringify({ q: batch, source: 'en', target, format: 'text' }), signal: AbortSignal.timeout(30000),
    });
    if (!response.ok) throw new Error(`Translation request failed: HTTP ${response.status}; no output file written`);
    const data = await response.json() as { data?: { translations?: { translatedText: string }[] } };
    const values = data.data?.translations;
    if (!values || values.length !== batch.length || values.some(x => typeof x.translatedText !== 'string')) throw new Error('Unexpected translation response; no output file written');
    batch.forEach((text, index) => { translations[text] = values[index].translatedText; });
  }
  results[target] = translations;
}
await writeFile(output, JSON.stringify({ reviewStatus: 'machine-generated-unreviewed', scope: 'topic actions only', sourceLanguage: 'en', translations: results }, null, 2) + '\n', { mode: 0o600 });
console.log(`Wrote ${output}`);
