import { CurrentUser } from "./api";

const TOKEN_KEY = "belediye_atik_token";
const USER_KEY = "belediye_atik_user";

export function saveSession(token: string, user: CurrentUser): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function loadToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function loadUser(): CurrentUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as CurrentUser;
  } catch {
    return null;
  }
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
