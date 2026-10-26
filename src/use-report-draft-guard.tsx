import { useEffect, useRef, useState } from 'react';
import { useBlocker } from 'react-router-dom';
import { Button } from './components/arc/button/button';

export function useReportDraftGuard(isDirty: () => boolean, saving: boolean) {
  const blocker = useBlocker(({ currentLocation, nextLocation }) => isDirty() &&
    (currentLocation.pathname !== nextLocation.pathname || currentLocation.search !== nextLocation.search));
  const [action, setAction] = useState<(() => void) | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const open = blocker.state === 'blocked' || action !== null;
  useEffect(() => { if (open) dialog.current?.showModal(); else dialog.current?.close(); }, [open]);
  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (isDirty()) { event.preventDefault(); event.returnValue = ''; }
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [isDirty]);
  const cancel = () => { setAction(null); if (blocker.state === 'blocked') blocker.reset(); };
  return {
    confirm: (next: () => void) => { if (isDirty()) setAction(() => next); else next(); },
    dialog: <dialog ref={dialog} className="report-leave-dialog" aria-labelledby="report-leave-title" onCancel={cancel}>
      <h2 id="report-leave-title">{saving ? 'Your report is saving' : 'Leave unsaved changes?'}</h2>
      <p>{saving ? 'Wait for confirmation before leaving this page.' : 'Your unfinished changes are only in this tab. Leaving or refreshing the inbox will discard them.'}</p>
      <div className="report-actions"><Button type="button" autoFocus onClick={cancel}>Keep editing</Button>
        {!saving && <Button type="button" variant="secondary" onClick={() => {
          const next = action; setAction(null);
          if (blocker.state === 'blocked') blocker.proceed(); else next?.();
        }}>Discard changes</Button>}
      </div>
    </dialog>,
  };
}
