import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { parseStarredIds } from './curation';

const empty = new Set<string>();
const CurationContext = createContext<ReadonlySet<string>>(empty);
export const useStarredIds = () => useContext(CurationContext);

/** Public metadata only. An unavailable service preserves the original ordering. */
export function CurationProvider({ children }: { children: ReactNode }) {
  const [stars, setStars] = useState<ReadonlySet<string>>(empty);
  useEffect(() => {
    let active = true;
    let controller: AbortController | undefined;
    let lastAttempt = 0;
    async function refresh() {
      if (Date.now() - lastAttempt < 60_000) return;
      lastAttempt = Date.now();
      controller?.abort();
      controller = new AbortController();
      const request = controller;
      const timer = setTimeout(() => request.abort(), 4000);
      try {
        const response = await fetch('/api/curation', { signal: request.signal, credentials: 'omit' });
        if (!response.ok) return;
        const data: unknown = await response.json();
        if (active) setStars(parseStarredIds(data));
      } catch { /* Optional curation must never block public content. */ }
      finally { clearTimeout(timer); }
    }
    void refresh();
    const changed = () => { lastAttempt = 0; void refresh(); };
    window.addEventListener('focus', refresh);
    window.addEventListener('actforgoa:curation-changed', changed);
    return () => { active = false; controller?.abort(); window.removeEventListener('focus', refresh); window.removeEventListener('actforgoa:curation-changed', changed); };
  }, []);
  return <CurationContext.Provider value={stars}>{children}</CurationContext.Provider>;
}
