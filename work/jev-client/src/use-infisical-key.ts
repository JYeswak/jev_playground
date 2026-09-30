/**
 * Makes every askJev* call in this process fall back to the Infisical key when no key is passed
 * and TYPESAFE_API_KEY is unset. Called by .omp/tools factories on real use when no fake
 * asker is injected. The omp review extension currently disables scoring and does not call it.
 * It never replaces a provider the process already installed, so a test that pins
 * "no key anywhere" with setKeyProvider(async () => undefined) stays keyless.
 */
import { keyProviderInstalled, setKeyProvider } from "../../../kit/src/client.ts";
import { infisicalKeyProvider } from "./infisical-key.ts";

export function useInfisicalKey(): void {
  if (!keyProviderInstalled()) setKeyProvider(infisicalKeyProvider);
}
