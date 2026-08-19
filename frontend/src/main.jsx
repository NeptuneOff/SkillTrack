import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  BarChart3,
  CalendarPlus,
  Download,
  Upload,
  Target,
  User,
  Trash2,
  Plus,
  LogOut,
} from "lucide-react";
import "./style.css";
import "./improvements.css";
import { api } from "./api";
import GoalsPage from "./GoalsPage";

const demo = { email: "demo@skilltrack.dev", password: "DemoPassword123!" };

class PageErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Erreur de rendu SkillTrack", error, info);
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
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [page, setPage] = useState("dashboard");
  const [toast, setToast] = useState("");
  const authed = !!token;
  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
  };
  return (
    <div className="app">
      <aside className="side">
        <div className="brand">
          <div className="mark">ST</div>
          <div>
            <b>SkillTrack</b>
            <span>Nocturne Kinetic</span>
          </div>
        </div>
        {authed && (
          <nav>
            <button
              onClick={() => setPage("dashboard")}
              className={page === "dashboard" ? "on" : ""}
            >
              <BarChart3 />
              Dashboard
            </button>
            <button
              onClick={() => setPage("workouts")}
              className={page === "workouts" ? "on" : ""}
            >
              <Activity />
              Séances
            </button>
            <button
              onClick={() => setPage("goals")}
              className={page === "goals" ? "on" : ""}
            >
              <Target />
              Objectifs
            </button>
            <button
              onClick={() => setPage("import")}
              className={page === "import" ? "on" : ""}
            >
              <Upload />
              Import / Export
            </button>
            <button
              onClick={() => setPage("profile")}
              className={page === "profile" ? "on" : ""}
            >
              <User />
              Profil RGPD
            </button>
            <button onClick={logout}>
              <LogOut />
              Déconnexion
            </button>
          </nav>
        )}
        <p className="small">
          Application complète de suivi calisthénie : auth, CRUD, stats,
          import/export, RGPD, API documentée.
        </p>
      </aside>
      <main>
        {toast && <div className="toast">{toast}</div>}
        {!authed ? (
          <Login setToken={setToken} setToast={setToast} />
        ) : (
          <PageErrorBoundary key={page}>
            <Shell page={page} token={token} setToast={setToast} />
          </PageErrorBoundary>
        )}
      </main>
    </div>
  );
}
function authHeaders(token) {
  return {
    "Content-Type": "application/json",
    Authorization: "Bearer " + token,
  };
}
async function request(path, opts = {}) {
  return api(path, opts);
}
function Login({ setToken, setToast }) {
  const [email, setEmail] = useState(demo.email),
    [password, setPassword] = useState(demo.password),
    [loading, setLoading] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await request("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
      setToast("Connexion réussie");
    } catch (err) {
      setToast("Erreur connexion: " + err.message);
    } finally {
      setLoading(false);
    }
  }
  return (
    <section className="hero">
      <div>
        <p className="eyebrow">RNCP 36463 · Projet démontrable</p>
        <h1>Suivi intelligent de progression calisthénie.</h1>
        <p>
          Connecte-toi au compte démo pour tester le dashboard, les séances, les
          objectifs, les imports/exports et les fonctions RGPD.
        </p>
      </div>
      <form className="card login" onSubmit={submit}>
        <h2>Connexion</h2>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Mot de passe
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <button className="primary" disabled={loading}>
          {loading ? "Connexion..." : "Se connecter"}
        </button>
      </form>
    </section>
  );
}
function Shell({ page, token, setToast }) {
  if (page === "dashboard") return <Dashboard token={token} />;
  if (page === "workouts")
    return <Workouts token={token} setToast={setToast} />;
  if (page === "goals") return <GoalsPage setToast={setToast} />;
  if (page === "import")
    return <ImportExport token={token} setToast={setToast} />;
  return <Profile token={token} setToast={setToast} />;
}
function Dashboard({ token }) {
  const [d, setD] = useState(null);
  useEffect(() => {
    request("/dashboard", { headers: authHeaders(token) }).then(setD);
  }, []);
  if (!d) return <Loader />;
  return (
    <>
      <Header
        title="Tableau de bord"
        sub="Vue globale de ta charge, fréquence et progression."
      />
      <div className="grid4">
        <Metric label="Séances" value={d.workout_count} />
        <Metric label="Séries" value={d.set_count} />
        <Metric label="Volume" value={d.total_volume} />
        <Metric label="Intensité moy." value={d.average_intensity} />
      </div>
      <div className="cols">
        <section className="card">
          <h2>Volume hebdomadaire</h2>
          <div className="bars">
            {d.weekly_volume.map((w) => (
              <div key={w.week}>
                <span
                  style={{ height: Math.max(8, w.volume / 10) + "px" }}
                ></span>
                <small>{w.week.slice(5)}</small>
              </div>
            ))}
          </div>
        </section>
        <section className="card">
          <h2>Objectifs actifs</h2>
          {d.goals.map((g) => (
            <div className="row" key={g.id}>
              <b>{g.skill}</b>
              <span>
                {g.current_level} → {g.target}
              </span>
            </div>
          ))}
        </section>
      </div>
      <section className="card">
        <h2>Dernières séances</h2>
        {d.recent_workouts.map((w) => (
          <WorkoutCard w={w} key={w.id} />
        ))}
      </section>
    </>
  );
}
function Header({ title, sub }) {
  return (
    <header>
      <p className="eyebrow">SkillTrack</p>
      <h1>{title}</h1>
      <p>{sub}</p>
    </header>
  );
}
function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}
function Loader() {
  return <div className="card">Chargement...</div>;
}
function WorkoutCard({ w, onEdit, onDelete }) {
  return (
    <div className="workout">
      <div>
        <b>{w.title}</b>
        <span>
          {w.date} · {w.type} · intensité {w.intensity}/10 ·{" "}
          {w.duration_minutes} min · volume {w.volume}
        </span>
        <p>{w.notes}</p>
        {w.sets.map((s) => (
          <small key={s.id || s.exercise}>
            • {s.exercise} — {s.reps} reps · {s.load_kg} kg ·{" "}
            {s.duration_seconds}s · diff {s.difficulty}/10
          </small>
        ))}
      </div>
      <div className="actions">
        {onEdit && <button onClick={() => onEdit(w)}>Modifier</button>}
        {onDelete && (
          <button className="danger" onClick={() => onDelete(w.id)}>
            <Trash2 size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
const emptySet = {
  exercise: "",
  reps: 0,
  load_kg: 0,
  duration_seconds: 0,
  difficulty: 5,
  notes: "",
};
function Workouts({ token, setToast }) {
  const [items, setItems] = useState([]),
    [editing, setEditing] = useState(null);
  const load = () =>
    request("/workouts", { headers: authHeaders(token) }).then(setItems);
  useEffect(() => {
    load();
  }, []);
  async function del(id) {
    await request("/workouts/" + id, {
      method: "DELETE",
      headers: authHeaders(token),
    });
    setToast("Séance supprimée");
    load();
  }
  return (
    <>
      <Header
        title="Séances"
        sub="Créer, modifier et supprimer des entraînements complets."
      />
      <WorkoutForm
        token={token}
        editing={editing}
        done={() => {
          setEditing(null);
          load();
          setToast("Séance enregistrée");
        }}
      />
      <section className="card">
        <h2>Historique</h2>
        {items.map((w) => (
          <WorkoutCard w={w} key={w.id} onEdit={setEditing} onDelete={del} />
        ))}
      </section>
    </>
  );
}
function WorkoutForm({ token, editing, done }) {
  const [form, setForm] = useState({
    title: "Séance planche",
    date: new Date().toISOString().slice(0, 10),
    type: "Skill",
    intensity: 7,
    duration_minutes: 70,
    notes: "",
    sets: [
      {
        ...emptySet,
        category: "planche",
        set_count: 1,
        assistance_kg: 0,
        exercise: "Tuck planche hold",
        duration_seconds: 20,
        difficulty: 7,
      },
    ],
  });
  const [error, setError] = useState("");
  useEffect(() => {
    if (editing)
      setForm({ ...editing, sets: editing.sets.map((s) => ({ ...s })) });
  }, [editing]);
  function ch(k, v) {
    setForm({ ...form, [k]: v });
  }
  function setSet(i, k, v) {
    const sets = [...form.sets];
    sets[i] = { ...sets[i], [k]: v };
    setForm({ ...form, sets });
  }
  function removeSet(i) {
    if (form.sets.length === 1)
      return setError("Une séance doit contenir au moins un exercice.");
    if (confirm("Supprimer cet exercice ?"))
      ch(
        "sets",
        form.sets.filter((_, index) => index !== i),
      );
  }
  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const path = editing ? "/workouts/" + editing.id : "/workouts";
      await request(path, {
        method: editing ? "PUT" : "POST",
        headers: authHeaders(token),
        body: JSON.stringify(form),
      });
      done();
    } catch (err) {
      setError(err.message);
    }
  }
  return (
    <form className="card form" onSubmit={submit}>
      <h2>{editing ? "Modifier la séance" : "Ajouter une séance"}</h2>
      <p className="small">
        Tous les champs marqués * sont obligatoires. RPE : 1 très facile, 10
        maximal.
      </p>
      {error && (
        <p role="alert" className="danger">
          {error}
        </p>
      )}
      <div className="fields">
        <label>
          Titre *
          <input
            required
            minLength="2"
            placeholder="Ex. Planche technique"
            value={form.title}
            onChange={(e) => ch("title", e.target.value)}
          />
        </label>
        <label>
          Date *
          <input
            required
            type="date"
            value={form.date}
            onChange={(e) => ch("date", e.target.value)}
          />
        </label>
        <label>
          Type *
          <select
            value={form.type}
            onChange={(e) => ch("type", e.target.value)}
          >
            {["Push", "Pull", "Legs", "Skill", "Mobilité", "Mixte"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label>
          RPE global *
          <input
            required
            type="number"
            min="1"
            max="10"
            value={form.intensity}
            onChange={(e) => ch("intensity", +e.target.value)}
          />
        </label>
        <label>
          Durée (minutes) *
          <input
            required
            type="number"
            min="1"
            max="1440"
            value={form.duration_minutes}
            onChange={(e) => ch("duration_minutes", +e.target.value)}
          />
        </label>
      </div>
      <label>
        Notes
        <textarea
          placeholder="Sensations, douleurs, points techniques…"
          value={form.notes}
          onChange={(e) => ch("notes", e.target.value)}
        />
      </label>
      <h3>Exercices</h3>
      {form.sets.map((s, i) => (
        <fieldset className="exercise" key={i}>
          <legend>Exercice {i + 1}</legend>
          <div className="set">
            <label>
              Nom *
              <input
                required
                minLength="2"
                placeholder="Ex. Tuck planche hold"
                value={s.exercise}
                onChange={(e) => setSet(i, "exercise", e.target.value)}
              />
            </label>
            <label>
              Séries *
              <input
                required
                type="number"
                min="1"
                max="50"
                value={s.set_count || 1}
                onChange={(e) => setSet(i, "set_count", +e.target.value)}
              />
            </label>
            <label>
              Répétitions
              <input
                type="number"
                min="0"
                placeholder="8"
                value={s.reps}
                onChange={(e) => setSet(i, "reps", +e.target.value)}
              />
            </label>
            <label>
              Charge kg
              <input
                type="number"
                min="0"
                placeholder="0"
                value={s.load_kg}
                onChange={(e) => setSet(i, "load_kg", +e.target.value)}
              />
            </label>
            <label>
              Durée sec.
              <input
                type="number"
                min="0"
                placeholder="20"
                value={s.duration_seconds}
                onChange={(e) => setSet(i, "duration_seconds", +e.target.value)}
              />
            </label>
            <label>
              RPE *
              <input
                required
                type="number"
                min="1"
                max="10"
                value={s.difficulty}
                onChange={(e) => setSet(i, "difficulty", +e.target.value)}
              />
            </label>
          </div>
          <button type="button" className="danger" onClick={() => removeSet(i)}>
            <Trash2 size={16} />
            Supprimer cet exercice
          </button>
        </fieldset>
      ))}
      <div className="actions">
        <button
          type="button"
          onClick={() =>
            ch("sets", [
              ...form.sets,
              {
                ...emptySet,
                category: "autre",
                set_count: 1,
                assistance_kg: 0,
              },
            ])
          }
        >
          <Plus size={16} />
          Ajouter un exercice
        </button>
        <button className="primary">
          <CalendarPlus size={16} />
          Enregistrer la séance
        </button>
      </div>
    </form>
  );
}
function Goals({ token, setToast }) {
  const [goals, setGoals] = useState([]),
    [form, setForm] = useState({
      skill: "Full planche",
      target: "Tenir 5 secondes",
      current_level: "Straddle",
      deadline: "",
      is_done: false,
    });
  const load = () =>
    request("/goals", { headers: authHeaders(token) }).then(setGoals);
  useEffect(() => {
    load();
  }, []);
  async function submit(e) {
    e.preventDefault();
    await request("/goals", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ ...form, deadline: form.deadline || null }),
    });
    setToast("Objectif ajouté");
    load();
  }
  async function done(g) {
    await request("/goals/" + g.id, {
      method: "PUT",
      headers: authHeaders(token),
      body: JSON.stringify({ ...g, is_done: !g.is_done }),
    });
    load();
  }
  return (
    <>
      <Header
        title="Objectifs"
        sub="Suivi des skills, niveaux actuels et deadlines."
      />
      <form className="card form" onSubmit={submit}>
        <div className="fields">
          <input
            value={form.skill}
            onChange={(e) => setForm({ ...form, skill: e.target.value })}
          />
          <input
            value={form.target}
            onChange={(e) => setForm({ ...form, target: e.target.value })}
          />
          <input
            value={form.current_level}
            onChange={(e) =>
              setForm({ ...form, current_level: e.target.value })
            }
          />
          <input
            type="date"
            value={form.deadline}
            onChange={(e) => setForm({ ...form, deadline: e.target.value })}
          />
        </div>
        <button className="primary">Ajouter objectif</button>
      </form>
      <section className="card">
        {goals.map((g) => (
          <div className="row" key={g.id}>
            <b>{g.skill}</b>
            <span>
              {g.current_level} → {g.target}{" "}
              {g.deadline ? "· " + g.deadline : ""}
            </span>
            <button onClick={() => done(g)}>
              {g.is_done ? "Réouvrir" : "Terminer"}
            </button>
          </div>
        ))}
      </section>
    </>
  );
}
function ImportExport({ token, setToast }) {
  const [report, setReport] = useState(null);
  async function upload(e) {
    const f = e.target.files[0];
    if (!f) return;
    const fd = new FormData();
    fd.append("file", f);
    try {
      const result = await api("/imports/csv", { method: "POST", body: fd });
      setReport(result);
      setToast(
        `Import terminé : ${result.imported_rows} importée(s), ${result.rejected_rows} rejetée(s).`,
      );
    } catch (err) {
      setToast("Erreur import : " + err.message);
    }
  }
  function dl(path) {
    api(path, { download: true }).catch((err) =>
      setToast("Erreur export : " + err.message),
    );
  }
  return (
    <>
      <Header
        title="Import / Export"
        sub="Importez un CSV contrôlé et exportez vos données personnelles (portabilité RGPD)."
      />
      <section className="card">
        <h2>Importer un CSV</h2>
        <label>
          Fichier CSV UTF-8 (2 Mo maximum)
          <input type="file" accept=".csv,text/csv" onChange={upload} />
        </label>
        <p className="small">
          Colonnes obligatoires : date, title, exercise. Les lignes invalides
          sont détaillées dans le rapport.
        </p>
        <pre>
          date,title,exercise,reps,load_kg,duration_seconds,difficulty,notes
        </pre>
        {report && (
          <div role="status">
            <b>
              {report.imported_rows} ligne(s) importée(s),{" "}
              {report.rejected_rows} rejetée(s)
            </b>
            {report.errors?.map((x, i) => (
              <p key={i}>{x}</p>
            ))}
          </div>
        )}
        <button onClick={() => dl("/imports/example")}>
          <Download />
          Télécharger un CSV d’exemple
        </button>
      </section>
      <section className="card">
        <h2>Exporter mes données</h2>
        <p>Les téléchargements sont protégés par votre jeton JWT.</p>
        <div className="actions">
          <button onClick={() => dl("/exports/csv")}>
            <Download />
            Export CSV
          </button>
          <button onClick={() => dl("/exports/json")}>
            <Download />
            Export JSON
          </button>
        </div>
      </section>
    </>
  );
}
function Profile({ token, setToast }) {
  const [u, setU] = useState(null);
  useEffect(() => {
    request("/users/me", { headers: authHeaders(token) })
      .then(setU)
      .catch((e) => setToast(e.message));
  }, []);
  async function del() {
    if (
      confirm(
        "Supprimer définitivement le compte, les séances, objectifs et imports ?",
      )
    ) {
      await request("/users/me", {
        method: "DELETE",
        headers: authHeaders(token),
      });
      localStorage.removeItem("token");
      location.reload();
    }
  }
  return (
    <>
      <Header
        title="Profil et RGPD"
        sub="Consultez, exportez ou effacez vos données personnelles."
      />
      <section className="card">
        {u && (
          <>
            <p>
              <b>Email :</b> {u.email}
            </p>
            <p>
              <b>Nom :</b> {u.display_name}
            </p>
            <p>
              <b>Créé le :</b> {u.created_at}
            </p>
          </>
        )}
        <p>
          Vous disposez d’un droit d’accès, de portabilité et d’effacement de
          vos données.
        </p>
        <button
          onClick={() =>
            api("/exports/json", { download: true }).catch((e) =>
              setToast(e.message),
            )
          }
        >
          <Download />
          Exporter mes données
        </button>
        <button className="danger" onClick={del}>
          <Trash2 />
          Supprimer mon compte et mes données
        </button>
      </section>
    </>
  );
}

const rootElement = document.getElementById("root");
if (rootElement) createRoot(rootElement).render(<App />);
