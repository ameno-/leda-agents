import { validateCredentials } from '../utils/validator';

export function register(email: string, password: string) {
  if (!validateCredentials(email, password)) {
    return { ok: false, error: 'invalid registration payload' };
  }

  return {
    ok: true,
    email,
  };
}