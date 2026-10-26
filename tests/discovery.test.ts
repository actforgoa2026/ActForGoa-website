import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { buildDiscoveryFeed, buildDiscoverySections } from "../src/discovery";
import { practicalGuideRecords } from "../src/guide-records";
import type { RecordItem } from "../src/types";
const records: RecordItem[] = JSON.parse(
  readFileSync(new URL("../public/data/catalog.json", import.meta.url), "utf8"),
);
test("home discovery includes every resource, person and story exactly once", () => {
  const feed = buildDiscoveryFeed(records);
  const eligible = records.filter((record) => record.kind !== "page");
  assert.equal(feed.length, eligible.length);
  assert.equal(new Set(feed.map((record) => record.id)).size, eligible.length);
  assert.deepEqual(
    new Set(feed.map((record) => record.id)),
    new Set(eligible.map((record) => record.id)),
  );
});
test("first page offers reading, community stories, organisations and direct contacts", () => {
  const page = buildDiscoveryFeed(records).slice(0, 12);
  assert.deepEqual(
    new Set(page.map((record) => record.kind)),
    new Set(["resource", "organisation", "contact", "story"]),
  );
  assert.ok(page.some((record) => record.image));
  assert.ok(page.some((record) => record.id === "resource-5731eea370"));
});
test("pagination remains stable for history restoration and handles sparse categories", () => {
  assert.deepEqual(
    buildDiscoveryFeed(records).map((r) => r.id),
    buildDiscoveryFeed([...records].reverse()).map((r) => r.id),
  );
  const resources = records.filter((r) => r.kind === "resource").slice(0, 7);
  assert.equal(buildDiscoveryFeed(resources).length, 7);
  assert.deepEqual(buildDiscoveryFeed([]), []);
});

test("sectioned discovery leads with practical help and preserves the whole catalogue exactly once", () => {
  const catalogue = [...practicalGuideRecords, ...records];
  const sections = buildDiscoverySections(catalogue);
  const entries = sections.flatMap(section => section.records);
  assert.equal(entries.length, catalogue.filter(record => record.kind !== "page").length);
  assert.equal(new Set(entries.map(record => record.id)).size, entries.length);
  assert.ok(sections[0].records.every(record => record.editorialStatus === "authored-practical-guide"));
  assert.deepEqual(new Set(entries.slice(0, 12).map(record => record.kind)), new Set(["resource", "organisation", "contact", "story"]));
  let position = 0;
  for (const section of sections) {
    assert.equal(section.start, position);
    assert.ok(section.records.length > 0 && section.records.length <= 3);
    if (section.type === "documents") assert.ok(section.records.every(record => record.kind === "resource" && record.documents.length > 0));
    if (section.type === "people") assert.ok(section.records.every(record => ["organisation", "contact"].includes(record.kind)));
    if (section.type === "stories") assert.ok(section.records.every(record => record.kind === "story"));
    position += section.records.length;
  }
  assert.deepEqual(buildDiscoverySections([...catalogue].reverse()), sections);
});

test("section filters retain every matching record with contiguous focus positions", () => {
  for (const kind of ["resource", "organisation", "story"]) {
    const sections = buildDiscoverySections(records, kind);
    const entries = sections.flatMap(section => section.records);
    const expected = records.filter(record => record.kind === kind || (kind === "organisation" && record.kind === "contact"));
    assert.deepEqual(new Set(entries.map(record => record.id)), new Set(expected.map(record => record.id)));
    assert.equal(entries.length, expected.length);
    let start = 0;
    for (const section of sections) {
      assert.equal(section.start, start);
      start += section.records.length;
    }
  }
});

test("sparse discovery sections do not leave holes or empty headings", () => {
  const sparse = records.filter(record => record.kind === "contact").slice(0, 4);
  const sections = buildDiscoverySections(sparse);
  assert.deepEqual(sections.map(section => section.records.length), [3, 1]);
  assert.deepEqual(sections.map(section => section.start), [0, 3]);
  assert.deepEqual(buildDiscoverySections(sparse, "resource"), []);
  assert.deepEqual(buildDiscoverySections([]), []);
});
