import React, {useCallback, useEffect, useState} from 'react';
import {Download, Trash2, Upload} from 'lucide-react';
import {api} from './api';
import {EmptyState, Header, Loader} from './ui';

function formatDate(value) {
  if (!value) return 'Date inconnue';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : new Intl.DateTimeFormat('fr-FR', {dateStyle: 'medium', timeStyle: 'short'}).format(date);
}

function formatFileSize(bytes) {
  if (bytes < 1_000) return `${bytes} octet${bytes > 1 ? 's' : ''}`;
  if (bytes < 1_000_000) return `${(bytes / 1_000).toFixed(1)} Ko`;
  return `${(bytes / 1_000_000).toFixed(1)} Mo`;
}

export default function ImportExportPage({setToast}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [report, setReport] = useState(null);
  const [importError, setImportError] = useState('');
  const [downloadFeedback, setDownloadFeedback] = useState(null);
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

  function selectFile(event) {
    const file = event.target.files?.[0] ?? null;
    setReport(null);
    setImportError('');

    if (!file) {
      setSelectedFile(null);
      return;
    }
    if (file.size > 2_000_000) {
      const message = 'Le fichier dépasse la limite de 2 Mo. Choisissez un fichier CSV plus léger.';
      setSelectedFile(null);
      setImportError(message);
      setToast(`Erreur import : ${message}`);
      event.target.value = '';
      return;
    }
    if (!file.name.toLowerCase().endsWith('.csv')) {
      const message = 'Format non reconnu. Sélectionnez un fichier portant l’extension .csv.';
      setSelectedFile(null);
      setImportError(message);
      setToast(`Erreur import : ${message}`);
      event.target.value = '';
      return;
    }

    setSelectedFile(file);
  }

  async function upload(event) {
    event.preventDefault();
    if (!selectedFile || uploading) return;

    const body = new FormData();
    body.append('file', selectedFile);
    setUploading(true);
    setReport(null);
    setImportError('');
    try {
      const result = await api('/imports/csv', {method: 'POST', body});
      setReport(result);
      setToast(
        `Import terminé : ${result.imported_rows} importée(s), ${result.rejected_rows} rejetée(s).`,
      );
      await loadHistory();
    } catch (err) {
      setImportError(err.message);
      setToast(`Erreur import : ${err.message}`);
    } finally {
      setUploading(false);
    }
  }

  async function download(path, label) {
    setDownloading(path);
    setError('');
    setDownloadFeedback(null);
    try {
      await api(path, {download: true});
      const message = `${label} téléchargé avec succès. Retrouvez le fichier dans vos téléchargements.`;
      setDownloadFeedback({path, type: 'success', message});
      setToast(`${label} téléchargé`);
    } catch (err) {
      const message = `${label} : ${err.message}`;
      setDownloadFeedback({path, type: 'error', message});
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

  const exampleFeedback = downloadFeedback?.path === '/imports/example' ? downloadFeedback : null;
  const exportFeedback = ['/exports/csv', '/exports/json'].includes(downloadFeedback?.path)
    ? downloadFeedback
    : null;

  return (
    <>
      <Header
        title="Import / Export"
        sub="Importez un CSV contrôlé et exportez vos données personnelles pour la portabilité RGPD."
      />
      {error && <p className="error-message" role="alert">{error}</p>}

      <section className="card" aria-labelledby="csv-import-title">
        <h2 id="csv-import-title">Importer un CSV</h2>
        <p>
          Sélectionnez d’abord votre fichier, vérifiez son nom, puis lancez l’import. Aucune
          donnée n’est ajoutée avant votre clic sur « Importer le fichier ».
        </p>
        <form onSubmit={upload}>
          <label htmlFor="csv-file">
            Fichier CSV UTF-8
            <input
              id="csv-file"
              type="file"
              accept=".csv,text/csv"
              aria-describedby="csv-file-help csv-file-selection"
              onChange={selectFile}
              disabled={uploading}
            />
          </label>
          <p className="small" id="csv-file-help">
            Taille maximale : 2 Mo. Les lignes invalides sont refusées et détaillées dans un
            rapport sans bloquer les lignes valides.
          </p>
          <p id="csv-file-selection" role="status" aria-live="polite">
            {selectedFile ? (
              <>
                <strong>Fichier sélectionné :</strong> {selectedFile.name} ({formatFileSize(selectedFile.size)})
              </>
            ) : (
              'Aucun fichier sélectionné. Choisissez un CSV pour activer le bouton d’import.'
            )}
          </p>
          <button
            id="csv-import-submit"
            type="submit"
            disabled={!selectedFile || uploading}
            title={!selectedFile ? 'Sélectionnez d’abord un fichier CSV' : undefined}
          >
            <Upload aria-hidden="true" />
            {uploading ? 'Import et validation en cours…' : 'Importer le fichier'}
          </button>
        </form>

        <div id="csv-format-help">
          <h3>Format CSV attendu</h3>
          <p>
            <strong>Colonnes obligatoires :</strong> <code>date</code>, <code>title</code> et{' '}
            <code>exercise</code>. Utilisez une ligne par exercice ; les autres colonnes sont
            facultatives.
          </p>
          <pre id="csv-example" role="region" aria-label="Colonnes et ligne d’exemple CSV">
{`date,title,type,intensity,duration_minutes,workout_notes,exercise,category,set_count,reps,load_kg,duration_seconds,difficulty,assistance_kg,set_notes
2026-08-20,Séance Planche,Skill,8,60,Travail technique,Full planche hold,Statique,5,,0,8,9,12,Gainage propre`}
          </pre>
        </div>

        {importError && (
          <div id="csv-import-error" className="error-message" role="alert">
            <strong>Import impossible.</strong> {importError}
            <p className="small">
              Corrigez le fichier à l’aide du format attendu ci-dessus, puis sélectionnez-le à nouveau.
            </p>
          </div>
        )}
        {report && (
          <div id="csv-import-report" className="import-report" role="status" aria-live="polite">
            <h3>
              {report.rejected_rows
                ? 'Import terminé avec des lignes en erreur'
                : 'Import terminé avec succès'}
            </h3>
            <p>
              <b>{report.imported_rows} ligne(s) importée(s)</b>,{' '}
              <b>{report.ignored_rows ?? 0} ignorée(s)</b> et{' '}
              <b>{report.rejected_rows} en erreur</b>.
            </p>
            {report.errors?.length ? (
              <>
                <ul>
                  {report.errors.map((message, index) => <li key={`${message}-${index}`}>{message}</li>)}
                </ul>
                <p className="small">
                  Corrigez les lignes indiquées puis importez à nouveau le fichier ; les lignes
                  déjà valides restent enregistrées.
                </p>
              </>
            ) : (
              <p>Aucune erreur détectée. Les nouvelles séances sont disponibles dans la page Séances.</p>
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
        {exampleFeedback && (
          <p
            id="example-download-feedback"
            className={exampleFeedback.type === 'error' ? 'error-message' : 'import-report'}
            role={exampleFeedback.type === 'error' ? 'alert' : 'status'}
          >
            {exampleFeedback.message}
          </p>
        )}
      </section>

      <section className="card" aria-labelledby="data-export-title">
        <h2 id="data-export-title">Exporter mes données</h2>
        <p>
          Téléchargez une copie portable de vos séances et objectifs. Les exports sont limités
          au compte connecté et protégés par le jeton JWT.
        </p>
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
        {exportFeedback && (
          <p
            id="data-export-feedback"
            className={exportFeedback.type === 'error' ? 'error-message' : 'import-report'}
            role={exportFeedback.type === 'error' ? 'alert' : 'status'}
            aria-live="polite"
          >
            {exportFeedback.message}
          </p>
        )}
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
