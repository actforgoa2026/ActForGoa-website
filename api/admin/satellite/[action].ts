// Plain Node functions need an explicit entry at this path depth on Vercel.
// The shared proxy retains its route allowlist and session/CSRF transport.
export { default } from '../../../server/admin-proxy.js';
export const config = { maxDuration: 60 };
