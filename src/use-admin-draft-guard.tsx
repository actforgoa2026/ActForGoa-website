import {useEffect, useRef, useState} from 'react';
import {useBlocker} from 'react-router-dom';
import {Button} from './components/arc/button/button';

/** Keep the editor mounted until a router transition or local action is accepted. */
export function useAdminDraftGuard(isDirty: () => boolean, saving: boolean, onDiscard: () => void) {
  const blocker = useBlocker(({currentLocation, nextLocation}) => (isDirty() || saving) &&
    (currentLocation.pathname !== nextLocation.pathname || currentLocation.search !== nextLocation.search));
  const [action, setAction] = useState<(() => void) | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const open = blocker.state === 'blocked' || action !== null;
  const dirty = isDirty();
  useEffect(() => {
    if (open && !dialog.current?.open) dialog.current?.showModal();
    else if (!open) dialog.current?.close();
  }, [open]);
  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (isDirty() || saving) { event.preventDefault(); event.returnValue = ''; }
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [isDirty, saving]);
  function cancel() { setAction(null); if (blocker.state === 'blocked') blocker.reset(); }
  return {
    confirm: (next: () => void) => { if (isDirty() || saving) setAction(() => next); else next(); },
    dialog: <dialog ref={dialog} className="admin-leave-dialog" aria-labelledby="admin-leave-title" onCancel={cancel}>
      <h2 id="admin-leave-title">{saving ? 'Your story is saving' : dirty ? 'Leave unsaved changes?' : 'Your story is saved'}</h2>
      <p>{saving ? 'Wait for confirmation before leaving this page.' : dirty ? 'Your unsaved story edits will be discarded. The last saved version will stay in your workspace.' : 'Your latest edits have been saved. You can leave this page or keep editing.'}</p>
      <div className="admin-leave-actions"><Button type="button" autoFocus onClick={cancel}>Keep editing</Button>
        {!saving && <Button type="button" variant="secondary" onClick={() => {
          const next = action; setAction(null); onDiscard();
          if (blocker.state === 'blocked') blocker.proceed(); else next?.();
        }}>{dirty ? 'Discard changes' : 'Leave page'}</Button>}
      </div>
    </dialog>,
  };
}
