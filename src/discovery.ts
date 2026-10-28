import type { RecordItem, Kind } from "./types";
import { prioritizeStarred } from './curation';

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
  "guide-farming",
  "guide-animal-welfare",
  "guide-environmental-protection",
  "guide-reporting",
  "guide-building",
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

export type DiscoverySectionType = "guides" | "people" | "stories" | "documents";
export interface DiscoverySection {
  id: string;
  type: DiscoverySectionType;
  round: number;
  title: string;
  description: string;
  href: string;
  linkLabel: string;
  start: number;
  records: RecordItem[];
}

const sectionDetails = {
  guides: {
    title: "Practical guides & local knowledge",
    description: "Find a next step for the things you care about.",
    href: "/library", linkLabel: "All guides & resources",
  },
  people: {
    title: "Local people & organisations",
    description: "Discover the work of community groups and volunteers across Goa.",
    href: "/directory", linkLabel: "Explore the directory",
  },
  stories: {
    title: "Stories from Goa",
    description: "Local ideas, community efforts and the people behind them.",
    href: "/stories", linkLabel: "All stories",
  },
  documents: {
    title: "Documents & handbooks",
    description: "Browse source documents, reference material and downloadable reading.",
    href: "/library", linkLabel: "Explore the library",
  },
} satisfies Record<DiscoverySectionType, Omit<DiscoverySection, "id" | "type" | "round" | "start" | "records">>;

// Build the entire stable sequence before revealing it. Loading another section
// never moves new records above a section the visitor has already read.
export function buildDiscoverySections(records: RecordItem[], kind = "all", starredIds: ReadonlySet<string> = new Set()): DiscoverySection[] {
  const queues: Record<DiscoverySectionType, RecordItem[]> = {
    guides: [], people: [], stories: [], documents: [],
  };
  for (const record of buildDiscoveryFeed(records)) {
    if (kind !== "all" && record.kind !== kind && !(kind === "organisation" && record.kind === "contact")) continue;
    const type = record.kind === "story" ? "stories"
      : record.kind === "organisation" || record.kind === "contact" ? "people"
      : record.documents.length && record.editorialStatus !== "authored-practical-guide" ? "documents" : "guides";
    queues[type].push(record);
  }
  const order = ["guides", "people", "stories", "documents"] as const;
  for (const type of order) queues[type] = prioritizeStarred(queues[type], starredIds, record => record.id);
  const sections: DiscoverySection[] = [];
  let start = 0;
  for (let round = 0; order.some(type => queues[type].length); round++) {
    for (const type of order) {
      const items = queues[type].splice(0, 3);
      if (!items.length) continue;
      const details = sectionDetails[type];
      sections.push({
        ...details,
        id: `${type}-${round}`, type, round, start, records: items,
        title: round === 0 ? details.title : `More ${details.title[0].toLowerCase()}${details.title.slice(1)}`,
      });
      start += items.length;
    }
  }
  return sections;
}
