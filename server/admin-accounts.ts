/** Account operator CLI. Passwords come from a hidden terminal prompt or stdin, never argv. */
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { AdminStore } from './admin-store.ts';

async function readPassword(): Promise<string> {
  if (!process.stdin.isTTY) {
    let input = '';
    for await (const chunk of process.stdin) { input += chunk; if (input.length > 300) throw new Error('Password input is too long.'); }
    return input.replace(/\r?\n$/, '');
  }
  process.stderr.write('Password (hidden, at least 12 characters): ');
  return new Promise((resolvePassword, reject) => {
    let value = '';
    process.stdin.setRawMode(true); process.stdin.resume(); process.stdin.setEncoding('utf8');
    const finish = () => { process.stdin.setRawMode(false); process.stdin.pause(); process.stdin.off('data', read); process.stderr.write('\n'); };
    const read = (chunk: string) => {
      for (const char of chunk) {
        if (char === '\u0003' || char === '\u0004') { finish(); reject(new Error('Cancelled.')); return; }
        if (char === '\r' || char === '\n') { finish(); resolvePassword(value); return; }
        if (char === '\u007f' || char === '\b') value = value.slice(0, -1);
        else if (value.length < 256 && char >= ' ') value += char;
      }
    };
    process.stdin.on('data', read);
  });
}

export async function accountCommand(args: string[]) {
  const [action, email, name, role = 'editor'] = args;
  if (!['add', 'revoke'].includes(action) || !email || (action === 'add' && (!name || !['editor', 'admin'].includes(role)))) throw new Error('Usage: admin-accounts.ts add email "Display name" [editor|admin], or revoke email. Password is read securely from terminal/stdin.');
  process.umask(0o077);
  const store = new AdminStore(resolve(process.env.ADMIN_DATA_DIR ?? '.reports/admin', 'admin.sqlite'), new Set());
  try {
    if (action === 'add') {
      await store.provision(email, name, await readPassword(), role as 'editor' | 'admin');
      console.log('Account saved. Existing sessions for this account were revoked.');
    } else { store.revoke(email); console.log('Account and its active sessions revoked.'); }
  } finally { store.close(); }
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  accountCommand(process.argv.slice(2)).catch(error => { console.error(error instanceof Error ? error.message : 'Account operation failed.'); process.exitCode = 1; });
}
