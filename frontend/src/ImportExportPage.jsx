import React, {useCallback, useEffect, useState} from 'react';
import {Download, Trash2} from 'lucide-react';
import {api} from './api';
import {EmptyState, Header, Loader} from './ui';

function formatDate(value) {
  if (!value) return 'Date inconnue';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : new Intl.DateTimeFormat('fr-FR', {dateStyle: 'medium', timeStyle: 'short'}).format(date);
}

export default function ImportExportPage({setToast}) {
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [downloading, setDownloading] = useState('');
  const [deletingImportId, setDeletingImportId] = useState('');
  const [error, setError] = useState('');

  const loadHistory = useCallback(async () => {
    setLoadingHistory(true);
    setError('');
    try {
      setHistory(await api('/imports/history'));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  async function upload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setReport(null);
    setError('');
    if (file.size > 2_000_000) {
      const message = 'Le fichier dépasse la limite de 2 Mo.';
      setError(message);
      setToast(`Erreur import : ${message}`);
      event.target.value = '';
      return;
    }
    if (!file.name.toLowerCase().endsWith('.csv')) {
      const message = 'Sélectionnez un fichier portant l’extension .csv.';
      setError(message);
      setToast(`Erreur import : ${message}`);
      event.target.value = '';
      return;
    }

    const body = new FormData();
    body.append('file', file);
    setUploading(true);
    try {
      const result = await api('/imports/csv', {method: 'POST', body});
      setReport(result);
      setToast(
        `Import terminé : ${result.imported_rows} importée(s), ${result.rejected_rows} rejetée(s).`,
      );
      await loadHistory();
    } catch (err) {
      setError(err.message);
      setToast(`Erreur import : ${err.message}`);
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  }

  async function download(path, label) {
    setDownloading(path);
    setError('');
    try {
      await api(path, {download: true});
      setToast(`${label} téléchargé`);
    } catch (err) {
      setError(err.message);
      setToast(`Erreur export : ${err.message}`);
    } finally {
      setDownloading('');
    }
  }

  async function removeHistory(item) {
    const accepted = window.confirm(
      `Supprimer le rapport d’import « ${item.filename} » ? Les séances et objectifs déjà importés seront conservés.`,
    );
    if (!accepted) return;
    setDeletingImportId(item.id);
    setError('');
    try {
      await api(`/imports/history/${item.id}`, {method: 'DELETE'});
      if (report && [report.id, report.import_id].includes(item.id)) setReport(null);
      setToast('Rapport d’import supprimé');
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingImportId('');
    }
  }

  return (
    <>
      <Header
        title="Import / Export"
        sub="Importez un CSV contrôlé et exportez vos données personnelles pour la portabilité RGPD."
      />
      {error && <p className="error-message" role="alert">{error}</p>}

      <section className="card" aria-labelledby="csv-import-title">
        <h2 id="csv-import-title">Importer un CSV</h2>
        <label htmlFor="csv-file">
          Fichier CSV UTF-8
          <input
            id="csv-file"
            type="file"
            accept=".csv,text/csv"
            aria-describedby="csv-file-help"
            onChange={upload}
            disabled={uploading}
          />
        </label>
        <p className="small" id="csv-file-help">
          Taille maximale : 2 Mo. Colonnes obligatoires : date, title, exercise. Les lignes
          invalides sont détaillées dans le rapport.
        </p>
        <pre role="region" aria-label="Exemple de colonnes CSV">
          date,title,type,intensity,duration_minutes,workout_notes,exercise,category,set_count,
          reps,load_kg,duration_seconds,difficulty,assistance_kg,set_notes
        </pre>
        {uploading && <p role="status">Import et validation en cours…</p>}
        {report && (
          <div className="import-report" role="status" aria-live="polite">
            <h3>Rapport du dernier import</h3>
            <p>
              <b>{report.imported_rows} ligne(s) importée(s)</b> et{' '}
              <b>{report.rejected_rows} rejetée(s)</b>
              {report.ignored_rows ? `, ${report.ignored_rows} ignorée(s)` : ''}.
            </p>
            {report.errors?.length ? (
              <ul>
                {report.errors.map((message, index) => <li key={`${message}-${index}`}>{message}</li>)}
              </ul>
            ) : (
              <p>Aucune erreur détectée.</p>
            )}
          </div>
        )}
        <button
          type="button"
          onClick={() => download('/imports/example', 'CSV d’exemple')}
          disabled={Boolean(downloading)}
        >
          <Download aria-hidden="true" />
          {downloading === '/imports/example' ? 'Téléchargement…' : 'Télécharger un CSV d’exemple'}
        </button>
      </section>

      <section className="card" aria-labelledby="data-export-title">
        <h2 id="data-export-title">Exporter mes données</h2>
        <p>Les téléchargements sont limités au compte connecté et protégés par le jeton JWT.</p>
        <div className="actions">
          <button
            type="button"
            onClick={() => download('/exports/csv', 'Export CSV')}
            disabled={Boolean(downloading)}
          >
            <Download aria-hidden="true" />
            {downloading === '/exports/csv' ? 'Téléchargement…' : 'Export CSV'}
          </button>
          <button
            type="button"
            onClick={() => download('/exports/json', 'Export JSON')}
            disabled={Boolean(downloading)}
          >
            <Download aria-hidden="true" />
            {downloading === '/exports/json' ? 'Téléchargement…' : 'Export JSON'}
          </button>
        </div>
      </section>

      <section className="card" aria-labelledby="import-history-title">
        <div className="section-heading">
          <div>
            <h2 id="import-history-title">Historique des imports</h2>
            <p className="small">Les 20 derniers imports du compte connecté.</p>
          </div>
          <button type="button" onClick={loadHistory} disabled={loadingHistory}>
            Actualiser
          </button>
        </div>
        {loadingHistory ? (
          <Loader label="Chargement de l’historique…" />
        ) : history.length ? (
          <div className="table-wrapper">
            <table>
              <caption className="visually-hidden">Historique des fichiers CSV importés</caption>
              <thead>
                <tr>
                  <th scope="col">Fichier</th>
                  <th scope="col">Date</th>
                  <th scope="col">Importées</th>
                  <th scope="col">Rejetées</th>
                  <th scope="col">Ignorées</th>
                  <th scope="col">Rapport</th>
                  <th scope="col">Action</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id}>
                    <th scope="row">{item.filename}</th>
                    <td>{formatDate(item.created_at)}</td>
                    <td>{item.imported_rows}</td>
                    <td>{item.rejected_rows}</td>
                    <td>{item.ignored_rows ?? 0}</td>
                    <td>{item.errors?.length ? item.errors.join(' · ') : 'Aucune erreur'}</td>
                    <td>
                      <button
                        type="button"
                        className="danger"
                        aria-label={`Supprimer l’historique ${item.filename}`}
                        onClick={() => removeHistory(item)}
                        disabled={deletingImportId === item.id}
                      >
                        <Trash2 aria-hidden="true" />
                        {deletingImportId === item.id ? 'Suppression…' : 'Supprimer'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="Aucun import">
            Les rapports de vos imports CSV apparaîtront ici.
          </EmptyState>
        )}
      </section>
    </>
  );
}
