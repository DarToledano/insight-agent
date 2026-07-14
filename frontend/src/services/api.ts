import type { AskRequest, AskResponse, ApiError } from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const body: AskRequest = { question: question.trim() };

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    const error: ApiError = {
      message:
        "Unable to reach the backend. Make sure the API is running at " +
        API_BASE_URL,
    };
    throw error;
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const payload = (await response.json()) as { detail?: string | { msg?: string }[] };
      if (typeof payload.detail === "string") {
        message = payload.detail;
      } else if (Array.isArray(payload.detail) && payload.detail[0]?.msg) {
        message = payload.detail[0].msg;
      }
    } catch {
      // use default message
    }
    const error: ApiError = { message, status: response.status };
    throw error;
  }

  return (await response.json()) as AskResponse;
}
