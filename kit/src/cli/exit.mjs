export const EXIT_CODES = Object.freeze({
  OK: 0,
  FINDINGS: 1,
  NOT_RUN: 2,
  REFUSED: 3,
  REFUSED_UNSAFE: 4,
  RETRYABLE: 5,
  ONLINE_REQUIRED: 6,
  USAGE: 64,
  NO_INPUT: 66,
  CANT_CREATE: 73,
  IO: 74,
});

export function statusForFailure(failure = {}) {
  if (failure.reason === 'unconfigured') return 'NOT_RUN';
  if (failure.reason === 'sdk-missing' || failure.reason === 'billing-hold') return 'ONLINE_REQUIRED';
  if (failure.reason === 'usage') return 'USAGE';
  if (failure.reason === 'no-input' || failure.code === 'ENOENT') return 'NO_INPUT';
  if (failure.reason === 'cannot-create') return 'CANT_CREATE';
  if (failure.reason === 'io' || ['EACCES', 'EIO', 'EISDIR'].includes(failure.code)) return 'IO';
  if (failure.reason === 'refused-unsafe') return 'REFUSED_UNSAFE';
  if (failure.reason === 'transport' || failure.reason === 'http') return 'RETRYABLE';
  if (failure.reason === 'non-json' || failure.reason === 'no-answers' || failure.reason === 'invalid-answer') return 'REFUSED';
  if (failure.status === 'NOT_RUN') return 'NOT_RUN';
  return 'FINDINGS';
}

export function exitCodeForFailure(failure = {}) {
  switch (statusForFailure(failure)) {
    case 'NOT_RUN': return EXIT_CODES.NOT_RUN;
    case 'ONLINE_REQUIRED': return EXIT_CODES.ONLINE_REQUIRED;
    case 'RETRYABLE': return EXIT_CODES.RETRYABLE;
    case 'REFUSED': return EXIT_CODES.REFUSED;
    case 'REFUSED_UNSAFE': return EXIT_CODES.REFUSED_UNSAFE;
    case 'USAGE': return EXIT_CODES.USAGE;
    case 'NO_INPUT': return EXIT_CODES.NO_INPUT;
    case 'CANT_CREATE': return EXIT_CODES.CANT_CREATE;
    case 'IO': return EXIT_CODES.IO;
    default: return EXIT_CODES.FINDINGS;
  }
}
