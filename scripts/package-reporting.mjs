import { cp, mkdir, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

// Explicit allowlist: no private database, tokens, photos or research archives.
const destination = resolve('.reports/deployment');
await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });
for (const name of ['package.json', 'package-lock.json', 'Dockerfile', 'railway.json']) {
  await cp(resolve('deploy/reporting', name), resolve(destination, name));
}
for (const name of ['server', 'shared']) await cp(resolve(name), resolve(destination, name), { recursive: true });
console.log('Reporting deployment package prepared at .reports/deployment.');
