import {createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode} from 'react';
import {Link} from 'react-router-dom';
import {Star, ArrowRight} from 'lucide-react';
import {adminApi, AdminApiError, type AdminSession, type CuratedStar} from './admin-api';
import {useStarredIds, useUpdateStarredIds} from './CurationProvider';
import {listenForTeamChange, notifyTeamChange} from './team-events';
import './team-access.css';

type TeamAccess = {session: AdminSession | null; pending: boolean; setStar: (id: string, starred: boolean) => Promise<void>};
const TeamContext = createContext<TeamAccess>({session: null, pending: false, setStar: async () => { throw Error('Sign in to curate.'); }});

/** Optional staff controls never gate normal browsing. The server authorizes every write. */
export function TeamAccessProvider({children}: {children: ReactNode}) {
  const [session, setSession] = useState<AdminSession | null>(null);
  const [pending, setPending] = useState(false);
  const updateStars = useUpdateStarredIds();
  const saving = useRef(false);
  const currentSession = useRef<AdminSession | null>(null);
  useEffect(() => {
    let active = true; let controller: AbortController | undefined;
    const refresh = () => {
      controller?.abort(); controller = new AbortController(); const request = controller;
      void adminApi<AdminSession>('/api/admin/session', {signal: request.signal}).then(value => {
        if (active && !request.signal.aborted) { currentSession.current = value; setSession(value); }
      }).catch(() => {
        if (active && !request.signal.aborted) { currentSession.current = null; setSession(null); }
      });
    };
    refresh();
    const stop = listenForTeamChange('session', refresh);
    window.addEventListener('focus', refresh);
    return () => { active = false; controller?.abort(); stop(); window.removeEventListener('focus', refresh); };
  }, []);
  const setStar = useCallback(async (recordId: string, starred: boolean) => {
    if (saving.current) return;
    const current = currentSession.current;
    if (!current) throw new AdminApiError('Sign in again to save your team pick.', 401);
    saving.current = true; setPending(true);
    try {
      const data = await adminApi<{stars: CuratedStar[]}>('/api/admin/stars', {method: 'PUT', csrfToken: current.csrfToken, body: {recordId, starred}});
      updateStars(data.stars.map(star => star.recordId));
      notifyTeamChange('curation');
    } catch (error) {
      if (error instanceof AdminApiError && (error.status === 401 || error.status === 403)) {
        currentSession.current = null; setSession(null); notifyTeamChange('session');
      }
      // A timed-out write may have reached the server. Read its saved state before retrying.
      notifyTeamChange('curation');
      throw error;
    } finally { saving.current = false; setPending(false); }
  }, [updateStars]);
  return <TeamContext.Provider value={{session, pending, setStar}}>{children}</TeamContext.Provider>;
}

export function TeamBrowsingBar() {
  const {session} = useContext(TeamContext);
  if (!session) return null;
  return <aside className="team-browsing-bar" aria-label="Team curation"><div className="shell"><span><Star size={17} aria-hidden="true"/><strong>Curating as {session.user.name}</strong><span>Star useful people and resources as you browse.</span></span><Link to="/admin?tool=community&view=picks">Manage team picks <ArrowRight size={16} aria-hidden="true"/></Link></div></aside>;
}

export function CurationStar({recordId, title}: {recordId: string; title: string}) {
  const {session, pending, setStar} = useContext(TeamContext);
  const stars = useStarredIds(); const starred = stars.has(recordId);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  async function toggle() {
    setError(''); setNotice('');
    try { await setStar(recordId, !starred); setNotice(starred ? 'Removed from team picks.' : 'Added to team picks.'); }
    catch (error) { setError(error instanceof Error ? error.message : 'Could not save this team pick.'); }
  }
  if (!session && !error) return null;
  return <div className="curation-control">
    {session && <button type="button" className="curation-star" aria-label={`${starred ? 'Unstar' : 'Star'} ${title}`} aria-pressed={starred} title={starred ? 'Remove from team picks' : 'Add to team picks'} disabled={pending} onClick={() => void toggle()}><Star size={20} fill={starred ? 'currentColor' : 'none'} aria-hidden="true"/></button>}
    {error && <span className="curation-error" role="alert">{error} {!session && <Link to="/admin">Sign in</Link>}</span>}
    <span className="sr-only" role="status">{notice}</span>
  </div>;
}
