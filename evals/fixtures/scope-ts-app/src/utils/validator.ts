export function validateCredentials(email: string, password: string) {
  return Boolean(email && password && password.length >= 8);
}