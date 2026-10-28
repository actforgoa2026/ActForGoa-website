import assert from 'node:assert/strict';
import test from 'node:test';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import { once } from 'node:events';
import type { AddressInfo } from 'node:net';
import { request as httpRequest } from 'node:http';
import { AdminError, AdminStore } from '../server/admin-store.ts';
import { createAdminServer, loadAdminRecordIds } from '../server/admin.ts';
import { prioritizeStarred, type BlogInput } from '../shared/admin.ts';

const draft: BlogInput = { title: 'A river worth protecting', slug: 'protecting-our-river', excerpt: 'A community update from Goa.', body: '## Our work\n\nWe met local volunteers and reviewed the source records.', tags: ['Water', 'Community'] };
const password = 'a-test-only-long-password';
const status = (expected: number) => (error: unknown) => error instanceof AdminError && error.status === expected;

test('curation is durable, canonical-ID validated, auditable and public data excludes team identities', async () => {
  const directory = mkdtempSync(resolve(tmpdir(), 'afg-admin-'));
  const path = resolve(directory, 'admin.sqlite');
  let store = new AdminStore(path, new Set(['organization-one', 'guide-water']));
  try {
    const first = await store.provision('first@example.test', 'First curator', password);
    const second = await store.provision('second@example.test', 'Second curator', password);
    store.star(first, 'organization-one', true);
    store.star(second, 'organization-one', true);
    assert.equal(store.stars()[0].updatedBy.name, 'Second curator');
    assert.deepEqual(store.publicStars(), ['organization-one']);
    assert.throws(() => store.star(first, 'invented-record', true), status(404));
    const audit = store.db.prepare('SELECT action FROM admin_audit WHERE target=?').all('organization-one');
    assert.equal(audit.length, 2);
    store.close();
    store = new AdminStore(path, new Set(['guide-water']));
    assert.equal(store.stars()[0].recordId, 'organization-one', 'orphan remains visible to team');
    assert.deepEqual(store.publicStars(), [], 'orphan does not affect public ranking');
    assert.deepEqual(store.star(second, 'organization-one', false), [], 'team can remove an orphan');
  } finally { store.close(); rmSync(directory, { recursive: true, force: true }); }
});

test('session rotation, account reset, revocation and expiry invalidate access', async () => {
  let now = Date.now();
  const store = new AdminStore(':memory:', new Set(), () => now);
  try {
    const user = await store.provision('Editor@Example.test', 'Editor', password);
    const first = await store.login('editor@example.test', password, 'client-one');
    assert.deepEqual(store.session(first.token).user, user);
    assert.equal(store.db.prepare('SELECT token_hash FROM admin_sessions').get()?.token_hash === first.token, false);
    assert.equal(JSON.stringify(store.session(first.token)).includes('password'), false);
    await store.provision('editor@example.test', 'Editor', 'a-new-test-only-password');
    assert.throws(() => store.session(first.token), status(401));
    await assert.rejects(store.login('editor@example.test', password, 'client-one'), status(401));
    const second = await store.login('editor@example.test', 'a-new-test-only-password', 'client-one');
    store.revoke('editor@example.test');
    assert.throws(() => store.session(second.token), status(401));
    await assert.rejects(store.login('editor@example.test', 'a-new-test-only-password', 'client-one'), status(401));
    await store.provision('editor@example.test', 'Editor', password);
    const third = await store.login('editor@example.test', password, 'client-one');
    now += 12 * 60 * 60 * 1000;
    assert.throws(() => store.session(third.token), status(401));
  } finally { store.close(); }
});

test('drafts, concurrent edits and published snapshots preserve explicit editorial publication', async () => {
  const store = new AdminStore(':memory:', new Set());
  try {
    const user = await store.provision('writer@example.test', 'Community team', password);
    let post = store.createPost(user, draft);
    assert.equal(post.version, 1);
    assert.deepEqual(store.publicPosts(), { posts: [], nextCursor: null, total: 0 });
    assert.throws(() => store.publicPost(draft.slug), status(404));
    assert.throws(() => store.updatePost(user, post.id, 0, draft), status(409));
    post = store.publishPost(user, post.id, post.version, true);
    assert.equal(post.status, 'published');
    assert.equal(post.version, 2);
    assert.equal(store.publicPost(draft.slug).title, draft.title);
    assert.equal(store.publicPosts().posts[0].title, draft.title, 'nonempty public lists use a valid SQLite JSON ordering path');
    assert.equal('body' in store.publicPosts().posts[0], false);
    assert.throws(() => store.createPost(user, draft), status(409));
    post = store.updatePost(user, post.id, post.version, { ...draft, title: 'A revised headline', slug: 'river-update', body: 'Unreviewed draft revision' });
    assert.equal(post.hasUnpublishedChanges, true);
    assert.equal(post.publishedSlug, draft.slug, 'admin live link keeps using the published URL');
    assert.equal(store.publicPost(draft.slug).body, draft.body, 'save does not silently publish');
    assert.throws(() => store.publicPost('river-update'), status(404));
    assert.throws(() => store.createPost(user, draft), status(409), 'previous live URL remains reserved');
    assert.throws(() => store.publishPost(user, post.id, 2, true), status(409));
    assert.throws(() => store.deletePost(user, post.id, post.version), status(409));
    post = store.publishPost(user, post.id, post.version, true);
    assert.equal(post.hasUnpublishedChanges, false);
    assert.throws(() => store.publicPost(draft.slug), status(404));
    const publicPost = store.publicPost('river-update');
    assert.equal(publicPost.body, 'Unreviewed draft revision');
    assert.equal('version' in publicPost, false);
    assert.equal('email' in publicPost, false);
    post = store.publishPost(user, post.id, post.version, false);
    assert.deepEqual(store.publicPosts(), { posts: [], nextCursor: null, total: 0 });
    store.deletePost(user, post.id, post.version);
    assert.throws(() => store.getPost(post.id), status(404));
  } finally { store.close(); }
});

test('post validation permits unfinished drafts but refuses unsafe slugs and incomplete publication', async () => {
  const store = new AdminStore(':memory:', new Set());
  try {
    const user = await store.provision('writer@example.test', 'Writer', password);
    assert.throws(() => store.createPost(user, { ...draft, slug: '../bad' }), status(400));
    assert.throws(() => store.createPost(user, { ...draft, tags: ['x'.repeat(41)] }), status(400));
    assert.throws(() => store.createPost(user, { ...draft, body: 'x'.repeat(100001) }), status(400));
    const post = store.createPost(user, { ...draft, title: '', body: '', excerpt: '' });
    assert.throws(() => store.publishPost(user, post.id, post.version, true), status(400));
    assert.equal(store.getPost(post.id).version, 1, 'failed publication rolls back entirely');
  } finally { store.close(); }
});

test('the archive route is reserved on create, edit and publication of older drafts', async () => {
  const store = new AdminStore(':memory:', new Set());
  try {
    const user = await store.provision('writer@example.test', 'Writer', password);
    const reserved = { ...draft, slug: 'archive' };
    const reservedError = (error: unknown) => error instanceof AdminError && error.status === 400 && /reserved for the blog archive/.test(error.message);
    assert.throws(() => store.createPost(user, reserved), reservedError);
    const post = store.createPost(user, draft);
    assert.throws(() => store.updatePost(user, post.id, post.version, reserved), reservedError);
    assert.equal(store.getPost(post.id).slug, draft.slug, 'rejected edit leaves the saved draft unchanged');
    // Represent a draft saved before reserved route validation was introduced.
    store.db.prepare('UPDATE admin_posts SET slug=?, data=? WHERE id=?').run('archive', JSON.stringify(reserved), post.id);
    assert.throws(() => store.publishPost(user, post.id, post.version, true), reservedError);
    assert.equal(store.getPost(post.id).version, post.version, 'failed publication leaves the draft revision unchanged');
    assert.equal(store.publicPosts().total, 0);
    const corrected = store.updatePost(user, post.id, post.version, { ...draft, slug: 'archive-news' });
    store.publishPost(user, corrected.id, corrected.version, true);
    assert.equal(store.publicPost('archive-news').id, post.id, 'related but non-reserved slugs remain usable');
  } finally { store.close(); }
});

test('login throttling persists independently of valid account identity', async () => {
  const store = new AdminStore(':memory:', new Set());
  try {
    for (let i = 0; i < 12; i++) await assert.rejects(store.login('unknown@example.test', password, 'same-client'), status(401));
    await assert.rejects(store.login('different@example.test', password, 'same-client'), status(429));
    await assert.rejects(store.login('unknown@example.test', password, 'different-client'), status(429));
  } finally { store.close(); }
});

test('ranking only prioritizes already relevant records and preserves order within groups', () => {
  const matched = [{ id: 'water-two' }, { id: 'water-one' }, { id: 'water-three' }];
  assert.deepEqual(prioritizeStarred(matched, item => item.id, new Set(['unrelated-housing', 'water-one'])).map(item => item.id), ['water-one', 'water-two', 'water-three']);
  assert.deepEqual(matched.map(item => item.id), ['water-two', 'water-one', 'water-three']);
  const ids = loadAdminRecordIds(resolve('.'));
  assert.ok(ids.has('guide-farming'));
  assert.ok(ids.size > 3000);
});

test('HTTP authentication, CSRF, origin protection, logout and public boundaries', async () => {
  const { server, store } = createAdminServer({ databasePath: ':memory:', knownRecordIds: new Set(['guide-water']), publicOrigin: 'http://127.0.0.1:4173', local: true });
  await store.provision('editor@example.test', 'Test editor', password);
  server.listen(0, '127.0.0.1'); await once(server, 'listening');
  const base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
  const request = (path: string, options?: RequestInit) => fetch(base + path, options);
  try {
    assert.equal((await request('/api/admin/session')).status, 401);
    assert.equal((await request('/api/admin/posts')).status, 401);
    const badOrigin = await request('/api/admin/login', { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: 'https://elsewhere.test' }, body: JSON.stringify({ email: 'editor@example.test', password }) });
    assert.equal(badOrigin.status, 403);
    const login = await request('/api/admin/login', { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: 'http://127.0.0.1:4173' }, body: JSON.stringify({ email: 'editor@example.test', password }) });
    assert.equal(login.status, 200);
    const cookie = login.headers.get('set-cookie')!;
    assert.match(cookie, /HttpOnly; SameSite=Strict; Path=\/api\/admin/);
    const session = await login.json() as { csrfToken: string };
    const headers = { Cookie: cookie.split(';')[0], 'Content-Type': 'application/json', 'X-CSRF-Token': session.csrfToken };
    assert.equal((await request('/api/admin/stars', { method: 'PUT', headers: { Cookie: headers.Cookie, 'Content-Type': 'application/json' }, body: JSON.stringify({ recordId: 'guide-water', starred: true }) })).status, 403);
    assert.equal((await request('/api/admin/stars', { method: 'PUT', headers: { ...headers, 'X-CSRF-Token': 'é'.repeat(64) }, body: JSON.stringify({ recordId: 'guide-water', starred: true }) })).status, 403);
    assert.equal((await request('/api/admin/stars', { method: 'PUT', headers, body: JSON.stringify({ recordId: 'guide-water', starred: true }) })).status, 200);
    const publicCuration = await (await request('/api/curation')).json();
    assert.deepEqual(publicCuration, { starredIds: ['guide-water'] });
    const post = await (await request('/api/admin/posts', { method: 'POST', headers, body: JSON.stringify(draft) })).json() as { post: { id: string; version: number } };
    assert.deepEqual(await (await request('/api/blog')).json(), { posts: [], nextCursor: null, total: 0 });
    const publish = await request(`/api/admin/posts/${post.post.id}/publish`, { method: 'POST', headers, body: JSON.stringify({ version: post.post.version }) });
    assert.equal(publish.status, 200);
    assert.equal((await request(`/api/blog/${draft.slug}`)).status, 200);
    const publicList = await request('/api/blog');
    assert.equal(publicList.status, 200);
    const publicPage = await publicList.json() as { posts: Record<string, unknown>[]; total: number };
    assert.equal(publicPage.total, 1);
    assert.equal('body' in publicPage.posts[0], false);
    assert.equal((await request('/api/blog?limit=101')).status, 400);
    assert.equal((await request('/api/blog?cursor=not-a-cursor')).status, 400);
    assert.equal((await request('/api/admin/logout', { method: 'POST', headers })).status, 200);
    assert.equal((await request('/api/admin/session', { headers })).status, 401);
  } finally { await new Promise<void>(resolveClosed => server.close(() => resolveClosed())); }
});

test('article summaries paginate without duplicates and search all records, with global admin counts', async () => {
  let now = Date.now();
  const store = new AdminStore(':memory:', new Set(), () => now);
  try {
    const user = await store.provision('writer@example.test', 'Writer', password);
    for (let index = 0; index < 4; index++) {
      now += 1000;
      const post = store.createPost(user, { ...draft, slug: `article-${index}`, title: `Article ${index}`, body: index === 0 ? 'Find this unique riverword in an older article.' : draft.body });
      if (index !== 2) store.publishPost(user, post.id, post.version, true);
    }
    const first = store.posts({ limit: 2 });
    assert.equal(first.posts.length, 2); assert.equal(first.total, 4);
    assert.deepEqual(first.counts, { draft: 1, published: 3 });
    assert.ok(first.nextCursor); assert.equal('body' in first.posts[0], false);
    const second = store.posts({ limit: 2, cursor: JSON.parse(Buffer.from(first.nextCursor, 'base64url').toString()) });
    assert.equal(second.posts.length, 2); assert.equal(second.nextCursor, null);
    assert.equal(new Set([...first.posts, ...second.posts].map(post => post.id)).size, 4);
    const search = store.posts({ q: 'riverword', status: 'published' });
    assert.equal(search.total, 1); assert.equal(search.posts[0].slug, 'article-0');
    assert.deepEqual(search.counts, { draft: 1, published: 3 });
    assert.equal(store.posts({ status: 'draft' }).posts[0].slug, 'article-2');
    const publicFirst = store.publicPosts({ limit: 2 });
    assert.equal(publicFirst.total, 3); assert.ok(publicFirst.nextCursor);
    const publicSecond = store.publicPosts({ limit: 2, cursor: JSON.parse(Buffer.from(publicFirst.nextCursor, 'base64url').toString()) });
    assert.equal(publicSecond.posts.length, 1); assert.equal(publicSecond.nextCursor, null);
    assert.equal(store.publicPosts({ q: 'riverword' }).total, 1);
  } finally { store.close(); }
});

test('frontend-proxy mode does not mistake shared relay egress for one visitor', async () => {
  const store = new AdminStore(':memory:', new Set());
  try {
    await store.provision('editor@example.test', 'Editor', password);
    for (let index = 0; index < 12; index++) await assert.rejects(store.login('wrong@example.test', password, null), status(401));
    const session = await store.login('editor@example.test', password, null);
    assert.equal(session.user.email, 'editor@example.test');
    await assert.rejects(store.login('wrong@example.test', password, null), status(429), 'account limit still applies');
  } finally { store.close(); }
});

test('revoking an account while an update body is arriving prevents the pending write', async () => {
  const { server, store } = createAdminServer({ databasePath: ':memory:', knownRecordIds: new Set(['guide-water']), publicOrigin: 'http://127.0.0.1:4173', local: true });
  await store.provision('editor@example.test', 'Editor', password);
  const login = await store.login('editor@example.test', password, 'test-client');
  server.listen(0, '127.0.0.1'); await once(server, 'listening');
  try {
    let initialAuth: () => void = () => {};
    const authorized = new Promise<void>(resolveAuth => { initialAuth = resolveAuth; });
    const originalSession = store.session.bind(store);
    store.session = token => { const session = originalSession(token); initialAuth(); return session; };
    const request = httpRequest({ host: '127.0.0.1', port: (server.address() as AddressInfo).port, path: '/api/admin/stars', method: 'PUT', headers: { 'Content-Type': 'application/json', Cookie: `afg_admin_session=${login.token}`, 'X-CSRF-Token': login.csrfToken } });
    const result = new Promise<number | undefined>((resolveResult, reject) => { request.on('response', response => { response.resume(); response.on('end', () => resolveResult(response.statusCode)); }); request.on('error', reject); });
    request.write('{"recordId":');
    await authorized;
    store.revoke('editor@example.test');
    request.end('"guide-water","starred":true}');
    assert.equal(await result, 401);
    assert.deepEqual(store.publicStars(), []);
  } finally { await new Promise<void>(resolveClosed => server.close(() => resolveClosed())); }
});

test('production requires HTTPS and sets a secure session cookie', async () => {
  assert.throws(() => createAdminServer({ databasePath: ':memory:', knownRecordIds: new Set(), publicOrigin: 'http://example.test' }), /HTTPS/);
  const { server, store } = createAdminServer({ databasePath: ':memory:', knownRecordIds: new Set(), publicOrigin: 'https://actforgoa-field-guide.vercel.app' });
  await store.provision('editor@example.test', 'Editor', password);
  server.listen(0, '127.0.0.1'); await once(server, 'listening');
  try {
    const response = await fetch(`http://127.0.0.1:${(server.address() as AddressInfo).port}/api/admin/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: 'editor@example.test', password }) });
    assert.equal(response.status, 200); assert.match(response.headers.get('set-cookie')!, /; Secure/);
  } finally { await new Promise<void>(resolveClosed => server.close(() => resolveClosed())); }
});
