import React, {useEffect, useRef} from 'react';
import {X} from 'lucide-react';

export function Header({title, sub}) {
  return (
    <header>
      <p className="eyebrow">SkillTrack</p>
      <h1 tabIndex="-1">{title}</h1>
      <p>{sub}</p>
    </header>
  );
}

export function Loader({label = 'Chargement…'}) {
  return (
    <div className="card state" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}

export function ErrorState({message, onRetry}) {
  return (
    <div className="card state error-state" role="alert">
      <h2>Impossible de charger cette section</h2>
      <p>{message}</p>
      {onRetry && (
        <button type="button" onClick={onRetry}>
          Réessayer
        </button>
      )}
    </div>
  );
}

export function EmptyState({title, children}) {
  return (
    <div className="empty">
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}

export function Dialog({open, title, children, onClose, actions, className = ''}) {
  const dialogRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const previousFocus = document.activeElement;
    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    window.requestAnimationFrame(() => dialogRef.current?.focus());
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      previousFocus?.focus?.();
    };
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="dialog-backdrop">
      <section
        className={`card dialog-card ${className}`.trim()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        tabIndex="-1"
        ref={dialogRef}
      >
        <div className="dialog-heading">
          <h2 id="dialog-title">{title}</h2>
          <button type="button" className="icon-button" aria-label="Fermer" onClick={onClose}>
            <X aria-hidden="true" />
          </button>
        </div>
        <div className="dialog-content">{children}</div>
        {actions && <div className="actions dialog-actions">{actions}</div>}
      </section>
    </div>
  );
}

export function ConfirmDialog({
  open,
  title,
  children,
  confirmLabel = 'Confirmer',
  onConfirm,
  onCancel,
  busy = false,
}) {
  return (
    <Dialog
      open={open}
      title={title}
      onClose={onCancel}
      className="confirm-dialog"
      actions={(
        <>
          <button type="button" onClick={onCancel} disabled={busy}>Annuler</button>
          <button type="button" className="danger" onClick={onConfirm} disabled={busy}>
            {busy ? 'Suppression…' : confirmLabel}
          </button>
        </>
      )}
    >
      {children}
    </Dialog>
  );
}

export function Toast({message, onClose}) {
  useEffect(() => {
    if (!message) return undefined;
    const timer = window.setTimeout(onClose, 4500);
    return () => window.clearTimeout(timer);
  }, [message, onClose]);

  if (!message) return null;
  const isError = /^(erreur|session expirée|impossible)/i.test(message);
  return (
    <div
      className={`toast${isError ? ' toast-error' : ''}`}
      role={isError ? 'alert' : 'status'}
      aria-live={isError ? 'assertive' : 'polite'}
      aria-atomic="true"
    >
      <span>{message}</span>
      <button
        type="button"
        className="icon-button"
        aria-label="Fermer la notification"
        onClick={onClose}
      >
        <X aria-hidden="true" />
      </button>
    </div>
  );
}
