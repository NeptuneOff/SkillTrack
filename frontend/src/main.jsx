import React, {useCallback, useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {
  Activity,
  BarChart3,
  LogOut,
  Target,
  Upload,
  User,
} from 'lucide-react';
import './style.css';
import './improvements.css';
import {api} from './api';
import DashboardPage from './DashboardPage';
import GoalsPage from './GoalsPage';
import ImportExportPage from './ImportExportPage';
import ProfilePage from './ProfilePage';
import WorkoutsPage from './WorkoutsPage';
import {Toast} from './ui';

const demo = {email: 'demo@skilltrack.dev', password: 'DemoPassword123!'};

const pages = [
  {id: 'dashboard', label: 'Dashboard', icon: BarChart3},
  {id: 'workouts', label: 'Séances', icon: Activity},
  {id: 'goals', label: 'Objectifs', icon: Target},
  {id: 'import', label: 'Import / Export', icon: Upload},
  {id: 'profile', label: 'Profil RGPD', icon: User},
];

class PageErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {error: null};
  }

  static getDerivedStateFromError(error) {
    return {error};
  }

  componentDidCatch(error, info) {
    console.error('Erreur de rendu SkillTrack', error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <section className="card" role="alert">
          <h1>Cette page n’a pas pu s’afficher</h1>
          <p>La navigation reste disponible. Changez de page puis réessayez.</p>
          <details>
            <summary>Détail technique</summary>
            <pre>{this.state.error.message}</pre>
          </details>
        </section>
      );
    }
    return this.props.children;
  }
}

export function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token') || '');
  const [page, setPage] = useState('dashboard');
  const [toast, setToast] = useState('');
  const contentRef = useRef(null);
  const authenticated = Boolean(token);

  const logout = useCallback((message = '') => {
    localStorage.removeItem('token');
    setToken('');
    setPage('dashboard');
    if (message) setToast(message);
  }, []);
  const clearToast = useCallback(() => setToast(''), []);

  useEffect(() => {
    const unauthorized = () => logout('Session expirée : reconnectez-vous.');
    window.addEventListener('skilltrack:unauthorized', unauthorized);
    return () => window.removeEventListener('skilltrack:unauthorized', unauthorized);
  }, [logout]);

  function navigate(nextPage) {
    setPage(nextPage);
    window.requestAnimationFrame(() => contentRef.current?.focus());
  }

  return (
    <div className="app">
      <a className="skip-link" href="#main-content">Aller au contenu principal</a>
      <aside className="side" aria-label="Présentation et navigation SkillTrack">
        <div className="brand">
          <div className="mark" aria-hidden="true">ST</div>
          <div>
            <b>SkillTrack</b>
            <span>Nocturne Kinetic</span>
          </div>
        </div>
        {authenticated && (
          <nav aria-label="Navigation principale">
            {pages.map(({id, label, icon: Icon}) => (
              <button
                type="button"
                key={id}
                onClick={() => navigate(id)}
                className={page === id ? 'on' : ''}
                aria-current={page === id ? 'page' : undefined}
              >
                <Icon aria-hidden="true" />
                {label}
              </button>
            ))}
            <button type="button" onClick={() => logout('Vous êtes déconnecté.')}>
              <LogOut aria-hidden="true" />
              Déconnexion
            </button>
          </nav>
        )}
        <p className="small side-description">
          Suivi calisthénie : authentification, séances, objectifs, statistiques, import/export
          et droits RGPD.
        </p>
      </aside>

      <main id="main-content" ref={contentRef} tabIndex="-1">
        <Toast message={toast} onClose={clearToast} />
        {!authenticated ? (
          <Login
            onAuthenticated={(accessToken) => {
              localStorage.setItem('token', accessToken);
              setToken(accessToken);
              setPage('dashboard');
              setToast('Connexion réussie');
            }}
          />
        ) : (
          <PageErrorBoundary key={page}>
            <Shell page={page} setToast={setToast} onLogout={logout} />
          </PageErrorBoundary>
        )}
      </main>
    </div>
  );
}

export function Login({onAuthenticated}) {
  const [email, setEmail] = useState(demo.email);
  const [password, setPassword] = useState(demo.password);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify({email: email.trim(), password}),
      });
      onAuthenticated(data.access_token);
    } catch (err) {
      setError(`Connexion impossible : ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="hero">
      <div>
        <p className="eyebrow">RNCP 36463 · Projet démontrable</p>
        <h1>Suivi intelligent de progression en calisthénie.</h1>
        <p>
          Connectez-vous au compte de démonstration pour tester le tableau de bord, les séances,
          les objectifs, les imports et exports ainsi que les fonctions RGPD.
        </p>
      </div>
      <form className="card login" onSubmit={submit} aria-describedby="login-help">
        <h2>Connexion</h2>
        <p className="small" id="login-help">
          Le compte de démonstration est prérempli. Tous les champs sont obligatoires.
        </p>
        {error && <p className="error-message" role="alert">{error}</p>}
        <label htmlFor="login-email">
          Adresse email *
          <input
            id="login-email"
            type="email"
            required
            autoComplete="username"
            placeholder="nom@exemple.fr"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label htmlFor="login-password">
          Mot de passe *
          <input
            id="login-password"
            type="password"
            required
            minLength="8"
            autoComplete="current-password"
            placeholder="8 caractères minimum"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button className="primary" type="submit" disabled={loading}>
          {loading ? 'Connexion…' : 'Se connecter'}
        </button>
      </form>
    </section>
  );
}

function Shell({page, setToast, onLogout}) {
  if (page === 'dashboard') return <DashboardPage />;
  if (page === 'workouts') return <WorkoutsPage setToast={setToast} />;
  if (page === 'goals') return <GoalsPage setToast={setToast} />;
  if (page === 'import') return <ImportExportPage setToast={setToast} />;
  return <ProfilePage setToast={setToast} onLogout={onLogout} />;
}

const rootElement = document.getElementById('root');
if (rootElement) createRoot(rootElement).render(<App />);
