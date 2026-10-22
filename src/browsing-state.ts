// Tab-local, bounded caches. No query or browsing history is sent to a server.
export class RecentCache<T> {
  private entries = new Map<string, T>();
  constructor(private capacity = 60) {}
  get(key: string) {
    return this.entries.get(key);
  }
  has(key: string) {
    return this.entries.has(key);
  }
  set(key: string, value: T) {
    this.entries.delete(key);
    this.entries.set(key, value);
    if (this.entries.size > this.capacity)
      this.entries.delete(this.entries.keys().next().value!);
  }
}
export const browsingState = new RecentCache<{
  view: "grid" | "list";
  limit: number;
}>();
export const semanticCache = new RecentCache<Map<string, number>>(20);

export const homeFeedState = new RecentCache<{
  limit: number;
  kind: string;
  automatic: boolean;
}>();
