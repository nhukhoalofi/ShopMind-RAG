import axios from "axios";

import { API_BASE_URL } from "../config/env";
import { BACKEND_OFFLINE_MESSAGE } from "../utils/errors";

export const httpClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

httpClient.interceptors.response.use((response) => {
  if (
    response.data === null ||
    typeof response.data !== "object" ||
    Array.isArray(response.data)
  ) {
    return Promise.reject(
      new Error("Backend returned an invalid or empty response."),
    );
  }
  return response;
});

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error ? error.message : "An unknown error occurred.";
  }

  if (error.code === "ECONNABORTED") {
    return "The backend request timed out. Please try again.";
  }

  if (!error.response) {
    return BACKEND_OFFLINE_MESSAGE;
  }

  const detail = error.response.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg ?? "Invalid request")
      .join("; ");
  }

  if (error.response.status === 404) {
    return "The requested resource was not found.";
  }
  if (error.response.status >= 500) {
    return "The backend encountered an error. Please try again.";
  }
  return `Request failed with HTTP ${error.response.status}.`;
}
