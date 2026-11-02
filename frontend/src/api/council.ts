import type { CouncilResponse } from "../types";

export async function runCouncil(prompt: string): Promise<CouncilResponse> {
  const response = await fetch("/api/council", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
