import { useEffect, useState } from 'react'

async function api(path, options) {
  const r = await fetch(`/api/v1${path}`, options)
  const body = await r.json()
  if (!r.ok) throw new Error(body.detail ?? r.status)
  return body
}

function Status() {
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api('/status').then(setStatus).catch((e) => setError(e.message))
  }, [])

  if (error) return <p className="err">Could not load status: {error}</p>
  if (!status) return <p>Loading…</p>
  const on = (flag) => <span className={flag ? 'ok' : 'off'}>{flag ? 'configured' : 'not configured'}</span>
  return (
    <dl>
      <dt>App</dt><dd>{status.app}</dd>
      <dt>Region</dt><dd>{status.region}</dd>
      <dt>Machine</dt><dd>{status.machine}</dd>
      <dt>Postgres</dt><dd>{on(status.database)}</dd>
      <dt>Tailscale</dt>
      <dd className={status.tailscale.status === 'connected' ? 'ok' : 'off'}>
        {status.tailscale.status}{status.tailscale.ip && ` (${status.tailscale.ip})`}
      </dd>
      <dt>Ollama</dt><dd>{on(status.ollama)}</dd>
    </dl>
  )
}

function Notes() {
  const [notes, setNotes] = useState([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState(null)

  const load = () => api('/notes').then(setNotes).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    try {
      await api('/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body: draft }),
      })
      setDraft('')
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <section>
      <h2>Postgres notes</h2>
      {error && <p className="err">{error}</p>}
      <form onSubmit={submit}>
        <input value={draft} onChange={(e) => setDraft(e.target.value)} maxLength={280} placeholder="Write a note…" />
        <button disabled={!draft.trim()}>Add</button>
      </form>
      <ul>
        {notes.map((n) => (
          <li key={n.id}>{n.body} <small>{new Date(n.created_at).toLocaleString()}</small></li>
        ))}
      </ul>
    </section>
  )
}

function Ollama() {
  const [models, setModels] = useState(null)
  const [error, setError] = useState(null)

  const check = () => {
    setError(null)
    api('/ollama/models').then(setModels).catch((e) => setError(e.message))
  }

  return (
    <section>
      <h2>Ollama over Tailscale <small>(stub)</small></h2>
      <button onClick={check}>List models</button>
      {error && <p className="err">{error}</p>}
      {models && (
        <ul>{models.map((m) => <li key={m.name}>{m.name} <small>{m.size_gb} GB</small></li>)}</ul>
      )}
    </section>
  )
}

export default function App() {
  return (
    <main>
      <h1>flyby ✈</h1>
      <p>React + FastAPI on Fly.io, with Fly Managed Postgres and a Tailscale stub.</p>
      <Status />
      <Notes />
      <Ollama />
    </main>
  )
}
