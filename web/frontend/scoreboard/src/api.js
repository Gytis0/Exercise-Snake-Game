export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";


export async function fetchTop(limit = 10) {
  const res = await fetch(`${API_BASE}/scores/top?limit=${limit}`);
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}


export async function claimScore(scoreId, code, player) {
  const res = await fetch(`${API_BASE}/scores/${scoreId}/claim`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, player })
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}


export async function postAnonymousScore(score) {
  const res = await fetch(`${API_BASE}/scores`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ score })
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json(); // { id, claim_token }
}