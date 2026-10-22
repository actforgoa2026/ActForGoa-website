import type { RecordItem, Kind } from "./types";

// A deterministic, diverse sequence keeps reading and practical contacts together.
// Each record appears once; missing categories never leave holes in the feed.
const cadence: Kind[] = [
  "story",
  "resource",
  "resource",
  "organisation",
  "organisation",
  "contact",
  "resource",
  "story",
  "resource",
  "organisation",
  "story",
  "resource",
];
const featured = [
  "resource-590480849c",
  "resource-5731eea370",
  "resource-34bc1772ee",
];
export function buildDiscoveryFeed(records: RecordItem[]): RecordItem[] {
  const kinds = ["story", "resource", "organisation", "contact"] as const;
  const queues = new Map<Kind, RecordItem[]>(
    kinds.map((kind) => [
      kind,
      records
        .filter((record) => record.kind === kind)
        .sort((a, b) => {
          const priority = (record: RecordItem) =>
            record.id === "wp-9352"
              ? 100
              : featured.includes(record.id)
                ? 90 - featured.indexOf(record.id)
                : record.image
                  ? 50
                  : record.kind === "organisation" && record.text.trim().length > 80
                    ? 30
                    : 0;
          return (
            priority(b) - priority(a) ||
            (b.publishedAt || "").localeCompare(a.publishedAt || "") ||
            a.title.localeCompare(b.title) || a.id.localeCompare(b.id)
          );
        }),
    ]),
  );
  const feed: RecordItem[] = [];
  while (kinds.some((kind) => queues.get(kind)!.length)) {
    for (const kind of cadence) {
      const record = queues.get(kind)?.shift();
      if (record) feed.push(record);
    }
  }
  return feed;
}
