import { useEffect, useState } from "react";
import { listMonitors, addMonitor, deleteMonitor } from "./api";
import "./App.css";

const POLL_MS = 5000;

function statusLabel(m) {
  if (m.checked_at === null) return { text: "pending", cls: "pending" };
  return m.is_up ? { text: "up", cls: "up" } : { text: "down", cls: "down" };
}

function formatChecked(iso) {
  if (!iso) return "-";
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export default function App() {
  const [monitors, setMonitors] = useState([]);
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    try {
      setMonitors(await listMonitors());
    } catch {
      setError("Could not reach backend");
    }
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await addMonitor(url);
      setUrl("");
      refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    await deleteMonitor(id);
    refresh();
  }

  return (
    <div className="container">
      <h1>Uptime Monitor</h1>

      <form onSubmit={handleSubmit} className="add-form">
        <input
          type="text"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
        <button type="submit">Add URL</button>
      </form>
      {error && <p className="error">{error}</p>}

      {monitors.length === 0 ? (
        <p className="empty">No monitors yet — add a URL above to start tracking it.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>URL</th>
              <th>Status</th>
              <th>Response time</th>
              <th>Last checked</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {monitors.map((m) => {
              const status = statusLabel(m);
              return (
                <tr key={m.id}>
                  <td>{m.url}</td>
                  <td>
                    <span className={`badge ${status.cls}`}>{status.text}</span>
                  </td>
                  <td>{m.response_time_ms !== null ? `${m.response_time_ms} ms` : "-"}</td>
                  <td>{formatChecked(m.checked_at)}</td>
                  <td>
                    <button onClick={() => handleDelete(m.id)}>remove</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
