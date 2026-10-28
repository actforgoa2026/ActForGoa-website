/** Reorder an already-filtered result set; stars never create a match. */
export function prioritizeStarred<T>(matches: readonly T[], starredIds: ReadonlySet<string>, id: (item: T) => string): T[] {
  if (!starredIds.size) return [...matches];
  return [...matches.filter(item => starredIds.has(id(item))), ...matches.filter(item => !starredIds.has(id(item)))];
}

export function parseStarredIds(data: unknown): Set<string> {
  if (!data || typeof data !== 'object' || !('starredIds' in data) || !Array.isArray(data.starredIds)) return new Set();
  return new Set(data.starredIds.filter((id): id is string => typeof id === 'string' && /^[a-zA-Z0-9_-]{1,160}$/.test(id)).slice(0,10000));
}
