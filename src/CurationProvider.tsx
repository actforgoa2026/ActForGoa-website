import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { parseStarredIds } from './curation';
import {listenForTeamChange} from './team-events';

const empty = new Set<string>();
const CurationContext = createContext<ReadonlySet<string>>(empty);
export const useStarredIds = () => useContext(CurationContext);
const CurationUpdates = createContext<(ids: string[]) => void>(() => {});
export const useUpdateStarredIds = () => useContext(CurationUpdates);

/** Public metadata only. An unavailable service preserves the original ordering. */
export function CurationProvider({ children }: { children: ReactNode }) {
  const [stars, setStars] = useState<ReadonlySet<string>>(empty);
  const update = useCallback((ids: string[]) => setStars(parseStarredIds({starredIds: ids})), []);
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
        if (active && !request.signal.aborted) setStars(parseStarredIds(data));
      } catch { /* Optional curation must never block public content. */ }
      finally { clearTimeout(timer); }
    }
    void refresh();
    const changed = () => { lastAttempt = 0; void refresh(); };
    window.addEventListener('focus', refresh);
    const stop = listenForTeamChange('curation', changed);
    return () => { active = false; controller?.abort(); window.removeEventListener('focus', refresh); stop(); };
  }, []);
  return <CurationUpdates.Provider value={update}><CurationContext.Provider value={stars}>{children}</CurationContext.Provider></CurationUpdates.Provider>;
}
