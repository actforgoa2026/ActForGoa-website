import type { RecordItem } from './types';
import { publicCatalogue } from './public-record';
import { climatePlanRecord } from './climate-plan';

export function needsCatalogue(pathname: string): boolean {
  const path = pathname.replace(/\/$/, '') || '/';
  return ['/', '/explore', '/search', '/directory/archive', '/library', '/stories', '/blog', '/blog/archive', '/about'].includes(path)
    || path.startsWith('/topics/')
    || (path !== '/read/goa-sapcc' && /^\/read\/(?!guide-)[^/]+$/.test(path));
}

/** Cache successful loads; failed and timed-out requests remain retryable. */
export function createCatalogueLoader(fetcher: typeof fetch = fetch, timeoutMs = 12000) {
  let cached: Promise<{ records: RecordItem[]; error: boolean }> | undefined;
  return async (pathname: string) => {
    if (!needsCatalogue(pathname)) return { records: [], error: false };
    if (!cached) {
      cached = (async () => {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const [response, { practicalGuideRecords }] = await Promise.all([
            fetcher('/data/catalog.json', { signal: controller.signal }),
            import('./guide-records'),
          ]);
          if (!response.ok) throw new Error('Catalogue unavailable');
          const records = await response.json() as RecordItem[];
          if (!Array.isArray(records)) throw new Error('Invalid catalogue');
          return { records: publicCatalogue([climatePlanRecord, ...practicalGuideRecords, ...records]), error: false };
        } catch {
          cached = undefined;
          return { records: [], error: true };
        } finally {
          clearTimeout(timer);
        }
      })();
    }
    return cached;
  };
}
