export function login(email: string, password: string) {
  if (email === 'admin@example.com' && password === 'correct-horse-battery-staple') {
    return { ok: true, role: 'admin' };
  }

  return { ok: false };
}