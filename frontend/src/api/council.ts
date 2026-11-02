import type { CouncilResponse } from "../types";

export async function runCouncil(prompt: string): Promise<CouncilResponse> {
  const response = await fetch("/api/council", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}`;
    try {
      const data = await response.json();
      if (data && data.detail) {
        errorDetail = data.detail;
      }
    } catch {
      const rawText = await response.text().catch(() => "");
      if (rawText && rawText.length < 250) {
        errorDetail = `${errorDetail}: ${rawText}`;
      } else if (response.status === 404) {
        errorDetail = "API endpoint /api/council not found (HTTP 404).";
      } else if (response.status === 504) {
        errorDetail = "Gateway timeout (HTTP 504). Deliberation took longer than server limit.";
      } else {
        errorDetail = `Server error (HTTP ${response.status}).`;
      }
    }
    throw new Error(errorDetail);
  }

  return response.json();
}
