export type SearchCitation = {
  id: string;
  title: string;
  label: string;
  reader_url: string;
};
export type SearchAnswer = {
  status: 'answered' | 'insufficient_evidence';
  paragraphs: { text: string; citations: string[] }[];
  citations: SearchCitation[];
  notice?: string;
  providerLabel?: string;
};

const cache = new Map<string, { expires: number; answer: SearchAnswer }>();
const ttl = 10 * 60 * 1000;

export function cachedSearchAnswer(question: string): SearchAnswer | undefined {
  const entry = cache.get(question.trim());
  if (!entry) return;
  if (entry.expires <= Date.now()) { cache.delete(question.trim()); return; }
  return entry.answer;
}

// A broken API response must never render an uncited answer or an arbitrary link.
export function checkedSearchAnswer(value: unknown): SearchAnswer {
  const answer = value as SearchAnswer | null;
  if (!answer || !Array.isArray(answer.paragraphs) || !Array.isArray(answer.citations)) throw Error('The answer could not be checked. The results below are still available.');
  if (answer.notice !== undefined && typeof answer.notice !== 'string') throw Error('The answer’s source limitations could not be checked. The results below are still available.');
  if (answer.status === 'insufficient_evidence' && !answer.paragraphs.length && !answer.citations.length) return answer;
  if (answer.status !== 'answered' || !answer.paragraphs.length || !answer.citations.length) throw Error('The answer has no supporting sources. The results below are still available.');
  const sources = new Set<string>();
  for (const source of answer.citations) {
    if (!source || typeof source.id !== 'string' || !source.id || typeof source.title !== 'string' || typeof source.label !== 'string' || typeof source.reader_url !== 'string'
      || !/^\/documents\/[a-f0-9]{24}-[a-f0-9]{12}\?[^\s\\]*$/.test(source.reader_url)) throw Error('A source link could not be checked. The results below are still available.');
    sources.add(source.id);
  }
  for (const paragraph of answer.paragraphs) {
    if (!paragraph || typeof paragraph.text !== 'string' || !paragraph.text.trim() || !Array.isArray(paragraph.citations) || !paragraph.citations.length
      || paragraph.citations.some(id => !sources.has(id))) throw Error('The answer has an unsupported citation. The results below are still available.');
  }
  return answer;
}

export async function fetchSearchAnswer(question: string, signal: AbortSignal, onProvider?: (label: string) => void): Promise<SearchAnswer> {
  const clean = question.trim();
  if (clean.length < 2 || clean.length > 2000) throw Error('Use a question between 2 and 2,000 characters for an AI answer. You can still browse the results below.');
  const cached = cachedSearchAnswer(clean);
  if (cached) { onProvider?.(cached.providerLabel || 'the configured AI provider'); return cached; }
  const controller = new AbortController();
  const cancel = () => controller.abort();
  signal.addEventListener('abort', cancel, { once: true });
  if (signal.aborted) cancel();
  const timer = setTimeout(cancel, 75000);
  try {
    const statusResponse = await fetch('/api/status', { signal: controller.signal });
    const status = await statusResponse.json().catch(() => null);
    const providerLabel = typeof status?.provider_label === 'string' && status.provider_label.trim() ? status.provider_label.trim() : 'the configured AI provider';
    onProvider?.(providerLabel);
    if (!statusResponse.ok || !status?.search_ready || !status?.chat_ready) throw Error('AI answers are temporarily unavailable. You can still use the guides and other results below.');
    // Only the submitted question goes to our own backend. It retrieves evidence
    // from the saved corpus before calling the model; there is no web-search path.
    const response = await fetch('/api/chat', {
      method: 'POST', signal: controller.signal, headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: clean, answer_style: 'brief' }),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) throw Error(typeof data?.detail === 'string' ? data.detail : 'The answer could not load. You can still use the results below.');
    const answer = { ...checkedSearchAnswer(data), providerLabel };
    if (signal.aborted) throw new DOMException('Search changed', 'AbortError');
    if (cache.size >= 32) cache.delete(cache.keys().next().value!);
    cache.set(clean, { answer, expires: Date.now() + ttl });
    return answer;
  } catch (cause) {
    if (controller.signal.aborted && !signal.aborted) throw Error('The answer is taking too long. Try again or use the results below.');
    if (cause instanceof TypeError) throw Error('The answer service could not be reached. You can still use the results below.');
    throw cause;
  } finally {
    clearTimeout(timer);
    signal.removeEventListener('abort', cancel);
  }
}
