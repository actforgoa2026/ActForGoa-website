/** Public wire contracts. Credentials and private audit records are never public. */
export type AdminUser = { id: string; email: string; name: string; role: 'admin' | 'editor' };
export type AdminSession = { user: AdminUser; csrfToken: string };
export type CuratedStar = { recordId: string; updatedAt: string; updatedBy: { id: string; name: string } };
export type BlogInput = { title: string; slug: string; excerpt: string; body: string; tags: string[] };
export type BlogPost = BlogInput & {
  id: string; status: 'draft' | 'published'; version: number;
  createdAt: string; updatedAt: string; publishedAt: string | null; publishedSlug: string | null;
  authorName: string; hasUnpublishedChanges: boolean;
};
export type PublicBlogPost = BlogInput & { id: string; authorName: string; publishedAt: string; updatedAt: string };
export const blogLimits = { title: 180, slug: 100, excerpt: 500, body: 100000, tags: 12, tag: 40 } as const;

/** Apply ONLY after query matching and selected filters; this never adds a result. */
export function prioritizeStarred<T>(relevantResults: readonly T[], getId: (record: T) => string, starredIds: ReadonlySet<string>): T[] {
  return relevantResults.map((record, index) => ({ record, index }))
    .sort((a, b) => Number(starredIds.has(getId(b.record))) - Number(starredIds.has(getId(a.record))) || a.index - b.index)
    .map(({ record }) => record);
}
