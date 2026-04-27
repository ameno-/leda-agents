export function logger(message: string, metadata: Record<string, unknown> = {}) {
  return `[app] ${message} ${JSON.stringify(metadata)}`;
}