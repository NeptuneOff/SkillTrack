import React, {useCallback, useEffect, useState} from 'react';
import {Download, Trash2} from 'lucide-react';
import {api} from './api';
import {ConfirmDialog, ErrorState, Header, Loader} from './ui';

function formatDate(value) {
  if (!value) return 'Non renseignée';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : new Intl.DateTimeFormat('fr-FR', {dateStyle: 'long', timeStyle: 'short'}).format(date);
}

export default function ProfilePage({setToast, onLogout}) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [exportFeedback, setExportFeedback] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setUser(await api('/users/me'));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function exportData() {
    setExporting(true);
    setError('');
    setExportFeedback('');
    try {
      await api('/exports/json', {download: true});
      setExportFeedback(
        'Export terminé : un fichier JSON de vos données personnelles a été téléchargé.',
      );
      setToast('Fichier de données personnelles téléchargé');
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(false);
    }
  }

  async function deleteAccount() {
    setDeleting(true);
    setError('');
    try {
      await api('/users/me', {method: 'DELETE'});
      setDeleteDialogOpen(false);
      onLogout('Compte et données supprimés');
    } catch (err) {
      setError(err.message);
      setDeleting(false);
    }
  }

  return (
    <>
      <Header
        title="Profil et RGPD"
        sub="Consultez, exportez ou effacez vos données personnelles."
      />
      {loading ? (
        <Loader label="Chargement du profil…" />
      ) : error && !user ? (
        <ErrorState message={error} onRetry={load} />
      ) : (
        <section className="card" aria-labelledby="personal-data-title">
          <h2 id="personal-data-title">Mes informations</h2>
          {error && <p className="error-message" role="alert">{error}</p>}
          <dl className="profile-data">
            <div>
              <dt>Email</dt>
              <dd>{user.email}</dd>
            </div>
            <div>
              <dt>Nom affiché</dt>
              <dd>{user.display_name || 'Non renseigné'}</dd>
            </div>
            <div>
              <dt>Compte créé le</dt>
              <dd>{formatDate(user.created_at)}</dd>
            </div>
          </dl>
          <section className="rgpd-notice" aria-labelledby="rgpd-rights-title">
            <h3 id="rgpd-rights-title">Vos données et vos droits RGPD</h3>
            <ul>
              <li><b>Accès et portabilité :</b> l’export JSON contient votre profil, vos séances, vos objectifs et vos historiques d’import.</li>
              <li><b>Effacement :</b> la suppression du compte efface définitivement ces données après confirmation.</li>
              <li><b>Confidentialité :</b> les opérations sont limitées au compte connecté par authentification JWT.</li>
            </ul>
          </section>
          <div className="actions profile-actions">
            <button type="button" onClick={exportData} disabled={exporting || deleting}>
              <Download aria-hidden="true" />
              {exporting ? 'Préparation…' : 'Exporter mes données'}
            </button>
            <button
              type="button"
              className="danger"
              onClick={() => setDeleteDialogOpen(true)}
              disabled={deleting || exporting}
            >
              <Trash2 aria-hidden="true" />
              {deleting ? 'Suppression…' : 'Supprimer mon compte et mes données'}
            </button>
          </div>
          {exportFeedback && (
            <p id="profile-export-feedback" className="import-report" role="status">
              {exportFeedback}
            </p>
          )}
        </section>
      )}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Supprimer mon compte et mes données ?"
        confirmLabel="Supprimer définitivement"
        onConfirm={deleteAccount}
        onCancel={() => {
          if (!deleting) setDeleteDialogOpen(false);
        }}
        busy={deleting}
      >
        <p>
          Vos séances, objectifs, historiques d’import et informations de profil seront supprimés.
          Cette action est irréversible. Exportez d’abord vos données si vous souhaitez en conserver
          une copie.
        </p>
      </ConfirmDialog>
    </>
  );
}
