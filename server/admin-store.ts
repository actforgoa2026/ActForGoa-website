import { DatabaseSync } from 'node:sqlite';
import { createHash, randomBytes, randomUUID, scrypt, timingSafeEqual } from 'node:crypto';
import { chmodSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { blogLimits, type AdminUser, type BlogInput, type BlogPost, type CuratedStar, type PublicBlogPost, type AdminPostPage, type PublicPostPage } from '../shared/admin.ts';

export class AdminError extends Error { constructor(public status: number, message: string) { super(message); } }
const fail = (status: number, message: string): never => { throw new AdminError(status, message); };
export const hashToken = (value: string) => createHash('sha256').update(value).digest('hex');
const derive = (password: string, salt: string): Promise<Buffer> => new Promise((resolve, reject) => {
  scrypt(password, salt, 64, { N: 32768, r: 8, p: 1, maxmem: 64 * 1024 * 1024 }, (error, key) => error ? reject(error) : resolve(key));
});
export async function passwordHash(password: string) {
  if (password.length < 12 || password.length > 256) fail(400, 'Use a password between 12 and 256 characters.');
  const salt = randomBytes(16).toString('hex');
  return `scrypt:${salt}:${(await derive(password, salt)).toString('hex')}`;
}
async function passwordMatches(password: string, stored: string) {
  const [, salt, expected] = stored.split(':');
  const actual = await derive(password, salt);
  const value = Buffer.from(expected, 'hex');
  return value.length === actual.length && timingSafeEqual(value, actual);
}
type UserRow = AdminUser & { password_hash: string; active: number };
type PostRow = { id: string; data: string; version: number; created_at: string; updated_at: string; author_name: string; published: string | null };
export type PostPageOptions = { limit?: number; cursor?: { time: string; id: string }; q?: string; status?: 'draft' | 'published' | 'all' };
const pageCursor = (time: string, id: string) => Buffer.from(JSON.stringify({ time, id })).toString('base64url');
const visibleUser = (row: UserRow): AdminUser => ({ id: row.id, email: row.email, name: row.name, role: row.role });
const normalEmail = (email: string) => email.trim().toLowerCase();

function cleanInput(value: unknown): BlogInput {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(400, 'Check the post fields.');
  const input = value as Record<string, unknown>;
  const out: Record<string, string> = {};
  for (const field of ['title', 'slug', 'excerpt', 'body'] as const) {
    if (typeof input[field] !== 'string' || input[field].length > blogLimits[field]) fail(400, `${field} must be text under ${blogLimits[field]} characters.`);
    out[field] = (input[field] as string).trim();
  }
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(out.slug)) fail(400, 'Use a lowercase slug with words separated by hyphens.');
  if (!Array.isArray(input.tags) || input.tags.length > blogLimits.tags || input.tags.some(tag => typeof tag !== 'string' || !tag.trim() || tag.length > blogLimits.tag)) fail(400, 'Use up to 12 tags, each under 40 characters.');
  return { title: out.title, slug: out.slug, excerpt: out.excerpt, body: out.body, tags: [...new Set((input.tags as string[]).map(tag => tag.trim()))] };
}

export class AdminStore {
  readonly db: DatabaseSync;
  private dummyPassword: Promise<string>;
  constructor(databasePath: string, readonly knownRecordIds: ReadonlySet<string>, readonly now: () => number = Date.now) {
    if (databasePath !== ':memory:') mkdirSync(dirname(databasePath), { recursive: true, mode: 0o700 });
    this.db = new DatabaseSync(databasePath);
    if (databasePath !== ':memory:') chmodSync(databasePath, 0o600);
    this.db.exec(`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;
      CREATE TABLE IF NOT EXISTS admin_users (id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','editor')), password_hash TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS admin_sessions (token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES admin_users(id), csrf TEXT NOT NULL, expires_at INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS admin_login_attempts (client TEXT NOT NULL, email TEXT NOT NULL, time INTEGER NOT NULL);
      CREATE INDEX IF NOT EXISTS admin_attempt_time ON admin_login_attempts(time);
      CREATE TABLE IF NOT EXISTS admin_stars (record_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES admin_users(id), updated_at TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS admin_posts (id TEXT PRIMARY KEY, slug TEXT UNIQUE NOT NULL, data TEXT NOT NULL, version INTEGER NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, author_name TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS admin_published_posts (post_id TEXT PRIMARY KEY REFERENCES admin_posts(id), slug TEXT UNIQUE NOT NULL, data TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS admin_audit (id TEXT PRIMARY KEY, actor_id TEXT NOT NULL, action TEXT NOT NULL, target TEXT NOT NULL, time TEXT NOT NULL);
    `);
    this.dummyPassword = passwordHash(randomBytes(32).toString('hex'));
  }
  close() { this.db.close(); }
  private stamp() { return new Date(this.now()).toISOString(); }
  private transaction<T>(fn: () => T): T {
    this.db.exec('BEGIN IMMEDIATE');
    try { const result = fn(); this.db.exec('COMMIT'); return result; }
    catch (error) { this.db.exec('ROLLBACK'); throw error; }
  }
  private audit(actor: string, action: string, target: string) {
    this.db.prepare('INSERT INTO admin_audit VALUES (?, ?, ?, ?, ?)').run(randomUUID(), actor, action, target, this.stamp());
  }
  async provision(email: string, name: string, password: string, role: AdminUser['role'] = 'editor') {
    email = normalEmail(email); name = name.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254 || !name || name.length > 100 || !['editor', 'admin'].includes(role)) fail(400, 'Provide a valid email, name and role.');
    const encrypted = await passwordHash(password);
    return this.transaction(() => {
      const existing = this.db.prepare('SELECT id FROM admin_users WHERE email=?').get(email);
      const id = existing?.id as string || randomUUID();
      this.db.prepare(`INSERT INTO admin_users VALUES (?, ?, ?, ?, ?, 1, ?) ON CONFLICT(email) DO UPDATE SET name=excluded.name, role=excluded.role, password_hash=excluded.password_hash, active=1, updated_at=excluded.updated_at`).run(id, email, name, role, encrypted, this.stamp());
      this.db.prepare('DELETE FROM admin_sessions WHERE user_id=?').run(id);
      this.audit('account-cli', existing ? 'reset-account' : 'create-account', id);
      return { id, email, name, role };
    });
  }
  revoke(email: string) {
    const user = this.db.prepare('SELECT id FROM admin_users WHERE email=?').get(normalEmail(email));
    if (!user) fail(404, 'Account not found.');
    this.transaction(() => {
      this.db.prepare('UPDATE admin_users SET active=0, updated_at=? WHERE id=?').run(this.stamp(), user!.id as string);
      this.db.prepare('DELETE FROM admin_sessions WHERE user_id=?').run(user!.id as string);
      this.audit('account-cli', 'revoke-account', user!.id as string);
    });
  }
  async login(email: string, password: string, client: string | null) {
    email = normalEmail(email);
    if (!email || email.length > 254 || !password || password.length > 256) fail(401, 'Email or password is incorrect.');
    const cutoff = this.now() - 15 * 60 * 1000;
    this.db.prepare('DELETE FROM admin_login_attempts WHERE time < ?').run(cutoff);
    const emailHash = hashToken(email), clientHash = client === null ? '' : hashToken(client);
    // A frontend relay is not an end-user identity. In proxy mode only the
    // account and aggregate controls apply; never trust an arbitrary XFF header.
    const attempts = this.db.prepare("SELECT COUNT(*) AS n FROM admin_login_attempts WHERE (client!='' AND client=?) OR email=?").get(clientHash, emailHash) as { n: number };
    const global = this.db.prepare('SELECT COUNT(*) AS n FROM admin_login_attempts').get() as { n: number };
    if (attempts.n >= 12 || global.n >= 150) fail(429, 'Too many sign-in attempts. Try again in 15 minutes.');
    this.db.prepare('INSERT INTO admin_login_attempts VALUES (?, ?, ?)').run(clientHash, emailHash, this.now());
    const user = this.db.prepare('SELECT * FROM admin_users WHERE email=?').get(email) as UserRow | undefined;
    const valid = await passwordMatches(password, user?.password_hash ?? await this.dummyPassword);
    if (!user || !valid || !user.active) fail(401, 'Email or password is incorrect.');
    // Recheck after asynchronous password hashing: revocation must win a concurrent login.
    const active = this.db.prepare('SELECT * FROM admin_users WHERE id=? AND active=1 AND password_hash=?').get(user!.id, user!.password_hash) as UserRow | undefined;
    if (!active) fail(401, 'Email or password is incorrect.');
    const token = randomBytes(32).toString('hex'), csrfToken = randomBytes(32).toString('hex');
    const expiresAt = this.now() + 12 * 60 * 60 * 1000;
    this.db.prepare('DELETE FROM admin_sessions WHERE expires_at <= ?').run(this.now());
    this.db.prepare('INSERT INTO admin_sessions VALUES (?, ?, ?, ?)').run(hashToken(token), active!.id, csrfToken, expiresAt);
    this.audit(active!.id, 'login', active!.id);
    return { token, csrfToken, user: visibleUser(active!), expiresAt };
  }
  session(token: string) {
    if (!/^[a-f0-9]{64}$/.test(token)) fail(401, 'Sign in to continue.');
    const row = this.db.prepare('SELECT u.*, s.csrf FROM admin_sessions s JOIN admin_users u ON u.id=s.user_id WHERE token_hash=? AND expires_at>? AND u.active=1').get(hashToken(token), this.now()) as (UserRow & { csrf: string }) | undefined;
    if (!row) fail(401, 'Your session has ended. Sign in again.');
    return { user: visibleUser(row!), csrfToken: row!.csrf };
  }
  logout(token: string) { this.db.prepare('DELETE FROM admin_sessions WHERE token_hash=?').run(hashToken(token)); }
  stars(): CuratedStar[] {
    return this.db.prepare('SELECT s.record_id, s.updated_at, u.id, u.name FROM admin_stars s JOIN admin_users u ON u.id=s.user_id ORDER BY s.updated_at DESC, s.record_id').all().map(row => ({ recordId: row.record_id as string, updatedAt: row.updated_at as string, updatedBy: { id: row.id as string, name: row.name as string } }));
  }
  publicStars() { return this.stars().filter(star => this.knownRecordIds.has(star.recordId)).map(star => star.recordId); }
  star(user: AdminUser, recordId: string, starred: boolean) {
    if (!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,199}$/.test(recordId)) fail(400, 'Choose a valid record.');
    if (starred && !this.knownRecordIds.has(recordId)) fail(404, 'This record is no longer in the catalogue. Refresh the list.');
    this.transaction(() => {
      if (starred) this.db.prepare('INSERT INTO admin_stars VALUES (?, ?, ?) ON CONFLICT(record_id) DO UPDATE SET user_id=excluded.user_id, updated_at=excluded.updated_at').run(recordId, user.id, this.stamp());
      else this.db.prepare('DELETE FROM admin_stars WHERE record_id=?').run(recordId);
      this.audit(user.id, starred ? 'star' : 'unstar', recordId);
    });
    return this.stars();
  }
  private row(id: string): PostRow {
    const row = this.db.prepare('SELECT p.*, live.data AS published FROM admin_posts p LEFT JOIN admin_published_posts live ON live.post_id=p.id WHERE p.id=?').get(id) as PostRow | undefined;
    if (!row) fail(404, 'Post not found.');
    return row!;
  }
  private post(row: PostRow): BlogPost {
    const data = JSON.parse(row.data) as BlogInput, published = row.published ? JSON.parse(row.published) as PublicBlogPost : null;
    const publicInput = published ? { title: published.title, slug: published.slug, excerpt: published.excerpt, body: published.body, tags: published.tags } : null;
    return { ...data, id: row.id, status: published ? 'published' : 'draft', version: row.version, createdAt: row.created_at, updatedAt: row.updated_at, publishedAt: published?.publishedAt ?? null, publishedSlug: published?.slug ?? null, authorName: row.author_name, hasUnpublishedChanges: published ? JSON.stringify(data) !== JSON.stringify(publicInput) : false };
  }
  posts(options: PostPageOptions = {}): AdminPostPage {
    const limit = options.limit ?? 50, query = options.q?.trim() ?? '', status = options.status ?? 'all';
    const join = 'FROM admin_posts p LEFT JOIN admin_published_posts live ON live.post_id=p.id';
    const filter = " WHERE (?='all' OR (?='draft' AND live.post_id IS NULL) OR (?='published' AND live.post_id IS NOT NULL)) AND instr(lower(json_extract(p.data,'$.title') || ' ' || json_extract(p.data,'$.excerpt') || ' ' || json_extract(p.data,'$.body')),lower(?))>0";
    const args = [status, status, status, query];
    const total = (this.db.prepare(`SELECT COUNT(*) AS n ${join}${filter}`).get(...args) as { n: number }).n;
    const published = (this.db.prepare('SELECT COUNT(*) AS n FROM admin_published_posts').get() as { n: number }).n;
    const all = (this.db.prepare('SELECT COUNT(*) AS n FROM admin_posts').get() as { n: number }).n;
    const cursorWhere = options.cursor ? ' AND (p.updated_at<? OR (p.updated_at=? AND p.id<?))' : '';
    const cursorArgs = options.cursor ? [options.cursor.time, options.cursor.time, options.cursor.id] : [];
    const rows = this.db.prepare(`SELECT p.*, live.data AS published ${join}${filter}${cursorWhere} ORDER BY p.updated_at DESC, p.id DESC LIMIT ?`).all(...args, ...cursorArgs, limit + 1) as PostRow[];
    const posts = rows.slice(0, limit).map(row => { const { body: _body, ...summary } = this.post(row); return summary; });
    const last = posts.at(-1);
    return { posts, nextCursor: rows.length > limit && last ? pageCursor(last.updatedAt, last.id) : null, total, counts: { draft: all - published, published } };
  }
  getPost(id: string) { return this.post(this.row(id)); }
  private slugAvailable(slug: string, id?: string) {
    // /blog/archive is an existing application route, not a journal article.
    // Check here so previously saved drafts cannot publish to it either.
    if (slug === 'archive') fail(400, 'This URL is reserved for the blog archive. Choose another slug.');
    const conflict = this.db.prepare('SELECT id FROM admin_posts WHERE slug=? AND id!=? UNION SELECT post_id AS id FROM admin_published_posts WHERE slug=? AND post_id!=?').get(slug, id ?? '', slug, id ?? '');
    if (conflict) fail(409, 'That URL is already used by another post. Choose another slug.');
  }
  createPost(user: AdminUser, input: unknown) {
    const data = cleanInput(input), id = randomUUID(), time = this.stamp();
    return this.transaction(() => {
      this.slugAvailable(data.slug);
      this.db.prepare('INSERT INTO admin_posts VALUES (?, ?, ?, 1, ?, ?, ?)').run(id, data.slug, JSON.stringify(data), time, time, user.name);
      this.audit(user.id, 'create-post', id);
      return this.getPost(id);
    });
  }
  private requireVersion(row: PostRow, version: unknown) {
    if (!Number.isSafeInteger(version) || version !== row.version) fail(409, 'This post changed. Reload it before saving your edits.');
  }
  updatePost(user: AdminUser, id: string, version: unknown, input: unknown) {
    const data = cleanInput(input);
    return this.transaction(() => {
      const row = this.row(id); this.requireVersion(row, version); this.slugAvailable(data.slug, id);
      this.db.prepare('UPDATE admin_posts SET slug=?, data=?, version=version+1, updated_at=? WHERE id=?').run(data.slug, JSON.stringify(data), this.stamp(), id);
      this.audit(user.id, 'edit-post', id);
      return this.getPost(id);
    });
  }
  publishPost(user: AdminUser, id: string, version: unknown, publish: boolean) {
    return this.transaction(() => {
      const row = this.row(id); this.requireVersion(row, version);
      if (publish) {
        const data = JSON.parse(row.data) as BlogInput;
        if (!data.title || !data.excerpt || !data.body) fail(400, 'Add a title, summary and article before publishing.');
        this.slugAvailable(data.slug, id);
        const snapshot: PublicBlogPost = { ...data, id, authorName: row.author_name, publishedAt: row.published ? (JSON.parse(row.published) as PublicBlogPost).publishedAt : this.stamp(), updatedAt: this.stamp() };
        this.db.prepare('INSERT INTO admin_published_posts VALUES (?, ?, ?) ON CONFLICT(post_id) DO UPDATE SET slug=excluded.slug, data=excluded.data').run(id, data.slug, JSON.stringify(snapshot));
      } else this.db.prepare('DELETE FROM admin_published_posts WHERE post_id=?').run(id);
      this.db.prepare('UPDATE admin_posts SET version=version+1, updated_at=? WHERE id=?').run(this.stamp(), id);
      this.audit(user.id, publish ? 'publish-post' : 'unpublish-post', id);
      return this.getPost(id);
    });
  }
  deletePost(user: AdminUser, id: string, version: unknown) {
    this.transaction(() => {
      const row = this.row(id); this.requireVersion(row, version);
      if (row.published) fail(409, 'Unpublish this post before deleting it.');
      this.db.prepare('DELETE FROM admin_posts WHERE id=?').run(id); this.audit(user.id, 'delete-post', id);
    });
  }
  publicPosts(options: PostPageOptions = {}): PublicPostPage {
    const limit = options.limit ?? 50, query = options.q?.trim() ?? '';
    const filter = " WHERE instr(lower(json_extract(data,'$.title') || ' ' || json_extract(data,'$.excerpt') || ' ' || json_extract(data,'$.body')),lower(?))>0";
    const total = (this.db.prepare(`SELECT COUNT(*) AS n FROM admin_published_posts${filter}`).get(query) as { n: number }).n;
    const cursorWhere = options.cursor ? " AND (json_extract(data,'$.publishedAt')<? OR (json_extract(data,'$.publishedAt')=? AND post_id<?))" : '';
    const cursorArgs = options.cursor ? [options.cursor.time, options.cursor.time, options.cursor.id] : [];
    const rows = this.db.prepare(`SELECT data FROM admin_published_posts${filter}${cursorWhere} ORDER BY json_extract(data,'$.publishedAt') DESC, post_id DESC LIMIT ?`).all(query, ...cursorArgs, limit + 1);
    const posts = rows.slice(0, limit).map(row => { const { body: _body, ...summary } = JSON.parse(row.data as string) as PublicBlogPost; return summary; });
    const last = posts.at(-1);
    return { posts, nextCursor: rows.length > limit && last ? pageCursor(last.publishedAt, last.id) : null, total };
  }
  publicPost(slug: string): PublicBlogPost {
    const row = this.db.prepare('SELECT data FROM admin_published_posts WHERE slug=?').get(slug);
    if (!row) fail(404, 'Article not found.');
    return JSON.parse(row!.data as string) as PublicBlogPost;
  }
}
