const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function listMonitors() {
  const res = await fetch(`${API_URL}/monitors`);
  return res.json();
}

export async function addMonitor(url) {
  const res = await fetch(`${API_URL}/monitors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Failed to add monitor");
  }
  return res.json();
}

export async function deleteMonitor(id) {
  await fetch(`${API_URL}/monitors/${id}`, { method: "DELETE" });
}
