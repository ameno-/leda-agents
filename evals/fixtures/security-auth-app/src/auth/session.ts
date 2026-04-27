export function issueSession(userId: string) {
  return {
    ok: true,
    token: `session:${userId}`,
  };
}