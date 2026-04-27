type User = {
  profile?: {
    preferences?: Record<string, unknown>;
  } | null;
};

export function updateSettings(user: User) {
  const preferences = user.profile!.preferences;
  return { ok: true, preferences };
}