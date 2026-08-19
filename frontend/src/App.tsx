import { useEffect, useState } from 'react'
import { Activity, Download, ShieldCheck } from 'lucide-react'
import { createDemoWorkout, listWorkouts, login, type Workout } from './api'
import './styles.css'

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('skilltrack_token') ?? '')
  const [email, setEmail] = useState('demo@skilltrack.local')
  const [password, setPassword] = useState('DemoPassword123!')
  const [workouts, setWorkouts] = useState<Workout[]>([])
  const [message, setMessage] = useState('')

  async function refresh(currentToken = token) {
    if (!currentToken) return
    setWorkouts(await listWorkouts(currentToken))
  }

  async function handleLogin() {
    const accessToken = await login(email, password)
    localStorage.setItem('skilltrack_token', accessToken)
    setToken(accessToken)
    setMessage('Connecté')
    await refresh(accessToken)
  }

  async function handleCreateDemo() {
    await createDemoWorkout(token)
    setMessage('Séance ajoutée')
    await refresh()
  }

  useEffect(() => { void refresh() }, [])

  return (
    <main className="shell">
      <section className="hero" aria-labelledby="title">
        <div>
          <p className="eyebrow">SkillTrack Calisthenics</p>
          <h1 id="title">Suivi structuré des séances, skills et progressions.</h1>
          <p>Application MVP pour journaliser l'entraînement, importer/exporter ses données et suivre son volume.</p>
        </div>
        <Activity size={72} aria-hidden="true" />
      </section>

      <section className="card" aria-labelledby="login-title">
        <h2 id="login-title">Connexion</h2>
        <label>Email<input value={email} onChange={e => setEmail(e.target.value)} /></label>
        <label>Mot de passe<input type="password" value={password} onChange={e => setPassword(e.target.value)} /></label>
        <button onClick={handleLogin}>Se connecter</button>
        <button disabled={!token} onClick={handleCreateDemo}>Ajouter une séance démo</button>
        {message && <p role="status">{message}</p>}
      </section>

      <section className="grid" aria-label="Indicateurs qualité">
        <article className="metric"><ShieldCheck /><strong>Sécurité</strong><span>JWT, hash, filtrage par user_id</span></article>
        <article className="metric"><Download /><strong>Données</strong><span>Import CSV, export JSON/CSV</span></article>
        <article className="metric"><Activity /><strong>Stats</strong><span>Volume, historique, progression</span></article>
      </section>

      <section className="card" aria-labelledby="workouts-title">
        <h2 id="workouts-title">Séances</h2>
        {workouts.length === 0 ? <p>Aucune séance chargée.</p> : workouts.map(workout => (
          <article key={workout.id} className="workout">
            <h3>{workout.title}</h3>
            <p>{workout.performed_on}</p>
            {workout.exercises.map(ex => <p key={ex.id}>{ex.name} — {ex.sets.length} série(s)</p>)}
          </article>
        ))}
      </section>
    </main>
  )
}
