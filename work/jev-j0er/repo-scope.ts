export function isJevRepoPath(cwd: unknown, repoRoot: string): boolean {
  const path = String(cwd ?? "");
  return path === repoRoot || path.startsWith(repoRoot + "/");
}
