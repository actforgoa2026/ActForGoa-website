import { cp, mkdir, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

// Explicit allowlist: no private database, tokens, photos or research archives.
const destination = resolve('.reports/deployment');
await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });
for (const name of ['package.json', 'package-lock.json', 'Dockerfile', 'railway.json']) {
  await cp(resolve('deploy/reporting', name), resolve(destination, name));
}
// Keep this service independent of other backends added to the repository.
for (const name of ['server/reporting.ts', 'shared/reporting.ts', 'shared/submission-identity.ts']) {
  await mkdir(resolve(destination, name, '..'), { recursive: true });
  await cp(resolve(name), resolve(destination, name));
}
console.log('Reporting deployment package prepared at .reports/deployment.');
