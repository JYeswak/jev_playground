export async function withBackoff(fn, { maxAttempts = 3 } = {}) {
  let last;
  for (let i = 0; i < maxAttempts; i++) {
    try {
      return await fn();
    } catch (err) {
      last = err;
      await new Promise((r) => setTimeout(r, 100 * 2 ** i));
    }
  }
  throw last;
}
