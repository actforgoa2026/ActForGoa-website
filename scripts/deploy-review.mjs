import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { smokeMcp } from './smoke-mcp.mjs';
import { resolve } from 'node:path';

const run = (command, args) => execFileSync(command, args, { encoding: 'utf8' }).trim();
const git = (...args) => run('git', args);
const checkOnly = process.argv.includes('--check');
const evidenceArg = process.argv.indexOf('--evidence');
if (evidenceArg === -1 || !process.argv[evidenceArg + 1]) {
  throw new Error('Supply --evidence <JSON file> from desktop and phone verification; see docs/RELEASING.md.');
}
const evidence = JSON.parse(readFileSync(resolve(process.argv[evidenceArg + 1]), 'utf8'));
if (git('status', '--porcelain', '--untracked-files=all')) {
  throw new Error('Release source must be committed and clean. Use an isolated checkout.');
}
git('fetch', 'origin', 'main');
const commit = git('rev-parse', 'HEAD');
const tree = git('rev-parse', 'HEAD^{tree}');
if (commit !== git('rev-parse', 'origin/main')) {
  throw new Error('Release HEAD must equal freshly fetched origin/main. Integrate and merge first.');
}
const requiredRoutes = ['/', '/explore', '/topics/waste', '/directory', '/directory/archive', '/emergency', '/report', '/read/guide-farming', '/templates/18-service-enquiry', '/ask', '/ask/legal', '/ask/ecology', '/admin', '/blog', '/blog/archive'];
if (evidence.treeSha !== tree || evidence.desktop !== true || evidence.mobile !== true
    || !requiredRoutes.every(route => evidence.routes?.includes(route))
    || !evidence.routes?.some(route => route.startsWith('/documents/'))) {
  throw new Error('Browser evidence must cover this exact source tree on desktop and phone, including all required routes.');
}
const lock = resolve(git('rev-parse', '--git-common-dir'), 'actforgoa-release.lock');
mkdirSync(lock); // One release at a time across all worktrees.
try {
  writeFileSync(resolve(lock, 'owner.json'), JSON.stringify({ commit, pid: process.pid, startedAt: new Date().toISOString() }));
  const inspect = JSON.parse(run('vercel', ['inspect', 'https://actforgoa-field-guide.vercel.app', '--json']));
  if (inspect.id !== evidence.previousDeploymentId) {
    throw new Error('The live deployment changed after verification. Reconcile it before publishing.');
  }
  if (checkOnly) {
    console.log(`Release preflight passed for ${commit}. No deployment performed.`);
  } else {
    execFileSync('npm', ['test'], { stdio: 'inherit' });
    execFileSync('npm', ['run', 'build'], {
      stdio: 'inherit',
      env: { ...process.env, VITE_REPORT_API_ORIGIN: 'https://reports-production-42c8.up.railway.app' },
    });
    // Refuse concurrent commits or edits made while the checks ran.
    git('fetch', 'origin', 'main');
    if (git('rev-parse', 'HEAD') !== commit || git('rev-parse', 'origin/main') !== commit
        || git('status', '--porcelain', '--untracked-files=all')) {
      throw new Error('Source changed during release checks. Revalidate before deployment.');
    }
    const current = JSON.parse(run('vercel', ['inspect', 'https://actforgoa-field-guide.vercel.app', '--json']));
    if (current.id !== inspect.id) throw new Error('Another deployment landed during checks. Reconcile first.');
    const deploymentResult = JSON.parse(execFileSync('vercel', ['deploy', '--json', '--yes', '--prod', '--skip-domain', '--project', 'actforgoa-field-guide',
      '--build-env', 'VITE_REPORT_API_ORIGIN=https://reports-production-42c8.up.railway.app',
      '--meta', `releaseCommit=${commit}`, '--meta', `releaseTree=${tree}`], {
      encoding: 'utf8', stdio: ['inherit', 'pipe', 'inherit'],
    }));
    // Agent mode wraps the same deployment object in a status envelope.
    const deployment = deploymentResult.deployment ?? deploymentResult;
    const deploymentUrl = deployment.url;
    if (typeof deploymentUrl !== 'string' || !/^https:\/\/actforgoa-field-guide-[a-z0-9-]+\.vercel\.app$/.test(deploymentUrl)) {
      throw new Error('Deployment did not return the expected project URL. Nothing promoted.');
    }
    const staged = JSON.parse(run('vercel', ['inspect', deploymentUrl, '--json']));
    if (staged.id !== deployment.id) throw new Error('Staged deployment identity does not match the build. Nothing promoted.');
    if (staged.readyState !== 'READY' && staged.status !== 'READY') throw new Error('Deployment is not ready. Nothing promoted.');
    const research = JSON.parse(run('vercel', ['curl', '/api/status', '--deployment', deploymentUrl,
      '--', '--fail', '--silent', '--show-error', '--max-time', '30']));
    if (research.search_ready !== true) throw new Error('Staged research routing or service is unavailable. Nothing promoted.');
    if (research.chat_ready !== true) throw new Error('Staged AI answers are unavailable or exhausted. Nothing promoted.');
    if (!['legal', 'ecology'].every(domain => research.domains?.includes(domain) && research.domain_counts?.[domain] > 0)) {
      throw new Error('Staged legal/ecology collections are not ready. Restore and verify the complete corpus before promotion.');
    }
    if (existsSync('api/admin/[...path].ts')) {
      const admin = JSON.parse(run('vercel', ['curl', '/api/admin/config', '--deployment', deploymentUrl,
        '--', '--fail', '--silent', '--show-error', '--max-time', '30']));
      if (admin.available !== true) throw new Error('Staged team tools service is unavailable. Nothing promoted.');
      const blog = JSON.parse(run('vercel', ['curl', '/api/blog', '--deployment', deploymentUrl,
        '--', '--fail', '--silent', '--show-error', '--max-time', '30']));
      if (!Array.isArray(blog.posts)) throw new Error('Staged public journal is unavailable. Nothing promoted.');
    }
    if (existsSync('api/mcp.ts')) smokeMcp(deploymentUrl);
    // Remote builds take time too. Check the release boundary again before promotion.
    git('fetch', 'origin', 'main');
    if (git('rev-parse', 'HEAD') !== commit || git('rev-parse', 'origin/main') !== commit
        || git('status', '--porcelain', '--untracked-files=all')) {
      throw new Error('Source changed during the remote build. Nothing promoted.');
    }
    const beforePromotion = JSON.parse(run('vercel', ['inspect', 'https://actforgoa-field-guide.vercel.app', '--json']));
    if (beforePromotion.id !== inspect.id) throw new Error('Live site changed during the remote build. Nothing promoted.');
    execFileSync('vercel', ['promote', deploymentUrl, '--yes'], { stdio: 'inherit' });
    const published = JSON.parse(run('vercel', ['inspect', 'https://actforgoa-field-guide.vercel.app', '--json']));
    if (published.id !== staged.id) throw new Error('Public alias does not match the verified deployment. Inspect the release before continuing.');
    console.log(`Promoted ${staged.id} from ${commit}. Verify the public site in the browser before declaring it live.`);
  }
} finally {
  rmSync(lock, { recursive: true });
}
