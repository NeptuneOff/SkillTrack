export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(message, status, details) { super(message); this.status = status; this.details = details; }
}

function readableError(payload, status) {
  if (Array.isArray(payload?.detail)) return payload.detail.map(e => `${e.loc?.slice(-1)[0] || 'champ'} : ${e.msg}`).join(' · ');
  return payload?.detail || payload?.message || `Erreur HTTP ${status}`;
}

export async function api(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {...options.headers};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  const response = await fetch(`${API_URL}${path}`, {...options, headers});
  if (response.status === 401) {
    localStorage.removeItem('token');
    window.dispatchEvent(new Event('skilltrack:unauthorized'));
  }
  if (!response.ok) {
    let payload;
    try { payload = await response.json(); } catch { payload = {detail: await response.text()}; }
    throw new ApiError(readableError(payload, response.status), response.status, payload);
  }
  if (options.download) {
    const blob = await response.blob();
    const disposition = response.headers.get('content-disposition') || '';
    const filename = disposition.match(/filename=([^;]+)/)?.[1]?.replaceAll('"', '') || 'skilltrack-export';
    const url = URL.createObjectURL(blob); const link = document.createElement('a');
    link.href = url; link.download = filename; link.click(); URL.revokeObjectURL(url); return;
  }
  return response.status === 204 ? null : response.json();
}
