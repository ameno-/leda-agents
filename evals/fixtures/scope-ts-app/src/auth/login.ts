import { validateCredentials } from '../utils/validator';

type LoginInput = {
  email: string;
  password: string;
};

export function login(input: LoginInput) {
  if (!validateCredentials(input.email, input.password)) {
    return { ok: false, error: 'invalid credentials' };
  }

  return {
    ok: true,
    userId: input.email.toLowerCase(),
  };
}