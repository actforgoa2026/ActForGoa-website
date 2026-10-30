import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const position = process.argv.indexOf('--output');
if (position < 0 || !process.argv[position + 1]) throw new Error('Use --output <new staging directory>.');
const output = resolve(process.argv[position + 1]);
if (existsSync(output)) throw new Error('Use a new output directory; existing packages are never overwritten.');
const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
if (git('status', '--porcelain', '--untracked-files=all')) throw new Error('Commit and verify the source before packaging the editorial service.');
const mappings = [
  ['deploy/admin/package.json','package.json'], ['deploy/admin/package-lock.json','package-lock.json'],
  ['deploy/admin/Dockerfile','Dockerfile'], ['deploy/admin/railway.json','railway.json'],
  ...['server/admin.ts','server/admin-store.ts','server/admin-accounts.ts','server/satellite-proxy.ts','server/satellite-public.ts','shared/admin.ts',
    'public/data/catalog.json','public/data/crm.json','src/content/guide-records.json'].map(path => [path,path]),
];
for (const [source] of mappings) if (!existsSync(resolve(root, source))) throw new Error(`Missing required source: ${source}`);
const files = mappings.map(([source, destination]) => {
  const bytes = readFileSync(resolve(root, source));
  const target = resolve(output, 'service', destination);
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(resolve(root, source), target);
  return { path: destination, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') };
});
const report = { commit: git('rev-parse','HEAD'), tree: git('rev-parse','HEAD^{tree}'),
  service: resolve(output,'service'), files, scope:'Source and public catalogue allowlist only. No accounts, credentials, drafts, databases or private reports.' };
writeFileSync(resolve(output,'manifest.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
