import React, {useCallback, useEffect, useState} from 'react';
import {Download, Trash2} from 'lucide-react';
import {api} from './api';
import {ErrorState, Header, Loader} from './ui';

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
    try {
      await api('/exports/json', {download: true});
      setToast('Archive personnelle téléchargée');
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(false);
    }
  }

  async function deleteAccount() {
    const accepted = window.confirm(
      'Supprimer définitivement votre compte, vos séances, vos objectifs et vos imports ? Cette action est irréversible.',
    );
    if (!accepted) return;
    setDeleting(true);
    setError('');
    try {
      await api('/users/me', {method: 'DELETE'});
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
          <p>
            Vous disposez d’un droit d’accès, de portabilité et d’effacement de vos données.
            L’export JSON permet d’en obtenir une copie.
          </p>
          <div className="actions profile-actions">
            <button type="button" onClick={exportData} disabled={exporting || deleting}>
              <Download aria-hidden="true" />
              {exporting ? 'Préparation…' : 'Exporter mes données'}
            </button>
            <button
              type="button"
              className="danger"
              onClick={deleteAccount}
              disabled={deleting || exporting}
            >
              <Trash2 aria-hidden="true" />
              {deleting ? 'Suppression…' : 'Supprimer mon compte et mes données'}
            </button>
          </div>
        </section>
      )}
    </>
  );
}
