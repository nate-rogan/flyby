import { useEffect, useState } from 'react'

export default function App() {
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/status.json', { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(setStatus)
      .catch((e) => setError(String(e)))
  }, [])

  return (
    <main>
      <h1>flyby ✈</h1>
      <p>A static React site deployed to Fly.io, with optional Tailscale.</p>

      {error && <p className="err">Could not load status: {error}</p>}
      {!status && !error && <p>Loading…</p>}
      {status && (
        <dl>
          <dt>App</dt><dd>{status.app}</dd>
          <dt>Region</dt><dd>{status.region}</dd>
          <dt>Machine</dt><dd>{status.machine}</dd>
          <dt>Tailscale</dt>
          <dd className={`ts ts-${status.tailscale.status}`}>
            {status.tailscale.status}{status.tailscale.ip && ` (${status.tailscale.ip})`}
          </dd>
          <dt>Started</dt><dd>{status.started ?? '—'}</dd>
        </dl>
      )}
    </main>
  )
}
