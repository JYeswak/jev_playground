# Case v01 (valid structural anchor)

The retry helper `withBackoff` lives in `src/net.ts` and takes
`{ maxAttempts }`. Failures sleep with exponential backoff and rethrow
after the last attempt.
