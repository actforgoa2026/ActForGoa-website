/** Only change notifications cross tabs. Sessions and CSRF tokens stay in memory. */
export type TeamChange = 'curation' | 'session';
const key = 'actforgoa:team-change';

export function notifyTeamChange(kind: TeamChange) {
  window.dispatchEvent(new Event(`actforgoa:${kind}-changed`));
  try { localStorage.setItem(key, JSON.stringify({kind, nonce: crypto.randomUUID()})); }
  catch { /* Focus refresh still works when browser storage is unavailable. */ }
}

export function listenForTeamChange(kind: TeamChange, refresh: () => void) {
  const eventName = `actforgoa:${kind}-changed`;
  const storage = (event: StorageEvent) => {
    if (event.key !== key || !event.newValue) return;
    try { if (JSON.parse(event.newValue).kind === kind) refresh(); } catch { /* Ignore unrelated/malformed notifications. */ }
  };
  window.addEventListener(eventName, refresh);
  window.addEventListener('storage', storage);
  return () => { window.removeEventListener(eventName, refresh); window.removeEventListener('storage', storage); };
}
