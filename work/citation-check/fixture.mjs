/** Miniature of the cookbook's eight-row table. Labels are planted, not authored by a model. */

export const SOURCE = [
  '4.1.3. "aud" (Audience) Claim',
  "",
  'If the principal processing the claim does not identify itself with a value in the "aud" claim when this claim is present, then the JWT MUST be rejected.',
  "",
  '4.1.4. "exp" (Expiration Time) Claim',
  "",
  'The "exp" (expiration time) claim identifies the expiration time. Use of this claim is OPTIONAL.',
].join("\n");

export const CASES = [
  {
    id: "aud_reject",
    claim: "If a validator does not find itself in a token's audience list, it has to reject the token.",
    quote: 'If the principal processing the claim does not identify itself with a value in the "aud" claim when this claim is present, then the JWT MUST be rejected.',
    answer: { ok: true, choice: "supports", confidence: 0.95 },
    expect: { verdict: "verified", action: "auto", calledModel: true },
  },
  {
    id: "exp_required",
    claim: "Validators must reject a token that omits the exp claim.",
    quote: "Use of this claim is OPTIONAL.",
    answer: { ok: true, choice: "contradicts", confidence: 0.99 },
    expect: { verdict: "contradicted", action: "auto", calledModel: true },
  },
  {
    id: "sig_reporting",
    claim: "Implementations must report signature failures to a central log.",
    quote: "This quote does not appear in the source at all.",
    answer: { ok: true, choice: "supports", confidence: 0.99 },
    expect: { verdict: "fabricated", action: "auto", calledModel: false },
  },
  {
    id: "pii_encryption",
    claim: "The exp claim requires encrypting personally identifiable information.",
    quote: "Use of this claim is OPTIONAL.",
    answer: { ok: true, choice: "says_nothing", confidence: 0.27 },
    expect: { verdict: "unsupported", action: "review", calledModel: true },
  },
  {
    id: "below_threshold",
    claim: "A validator that is not in the audience list must reject the token.",
    quote: "the JWT MUST be rejected.",
    answer: { ok: true, choice: "supports", confidence: 0.79 },
    expect: { verdict: "verified", action: "review", calledModel: true },
  },
];
