const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type Workout = {
  id: string
  title: string
  performed_on: string
  notes?: string | null
  exercises: { id: string; name: string; variation?: string | null; sets: { id: string; reps: number; external_load_kg: number; hold_seconds?: number | null; rpe?: number | null }[] }[]
}

export async function login(email: string, password: string): Promise<string> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  if (!response.ok) throw new Error('Connexion impossible')
  const data = await response.json()
  return data.access_token
}

export async function listWorkouts(token: string): Promise<Workout[]> {
  const response = await fetch(`${API_URL}/workouts`, { headers: { Authorization: `Bearer ${token}` } })
  if (!response.ok) throw new Error('Chargement impossible')
  return response.json()
}

export async function createDemoWorkout(token: string): Promise<void> {
  const response = await fetch(`${API_URL}/workouts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      title: 'Push statics',
      performed_on: new Date().toISOString().slice(0, 10),
      notes: 'Séance générée depuis le frontend',
      exercises: [
        { name: 'Planche lean', variation: 'parallettes', position: 0, sets: [{ reps: 5, external_load_kg: 0, hold_seconds: 12, rpe: 7 }] }
      ]
    })
  })
  if (!response.ok) throw new Error('Création impossible')
}
