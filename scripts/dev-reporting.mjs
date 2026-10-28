import { spawn } from 'node:child_process';

// One command owns the web, reporting and internal-tool processes.
const processes = [];
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of processes) if (child.exitCode === null) child.kill('SIGTERM');
  process.exitCode = code;
}
for (const args of [['--import', 'tsx', 'server/reporting.ts'], ['--import', 'tsx', 'server/admin.ts'], ['node_modules/vite/bin/vite.js', '--host', '127.0.0.1']]) {
  const child = spawn(process.execPath, args, { stdio: 'inherit', env: process.env });
  processes.push(child);
  child.on('error', error => { console.error(error.message); stop(1); });
  child.on('exit', code => stop(code ?? 0));
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
