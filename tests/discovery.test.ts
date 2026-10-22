import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { buildDiscoveryFeed } from "../src/discovery";
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
  assert.ok(page.some((record) => record.id === "resource-590480849c"));
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
