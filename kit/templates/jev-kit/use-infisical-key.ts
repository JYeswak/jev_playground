/**
 * Makes every askJev* call in this process fall back to the Infisical key when no key is passed
 * and TYPESAFE_API_KEY is unset. Called only on real use: the .omp/tools factories when no fake
 * asker is injected, and the omp review extension. It never replaces a provider the process
 * already installed, so a test that pins "no key anywhere" with setKeyProvider(async () =>
 * undefined) stays keyless whatever it constructs afterwards.
 */
import { keyProviderInstalled, setKeyProvider } from "./client.ts";
import { infisicalKeyProvider } from "./infisical-key.ts";

export function useInfisicalKey(): void {
  if (!keyProviderInstalled()) setKeyProvider(infisicalKeyProvider);
}
