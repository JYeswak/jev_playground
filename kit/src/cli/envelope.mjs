import { exitCodeForFailure, statusForFailure } from './exit.mjs';

function resultData(result) {
  if (result === null || typeof result !== 'object' || Array.isArray(result)) return result ?? null;
  const data = { ...result };
  delete data.ok;
  delete data.latencyMs;
  delete data.latency_ms;
  delete data.usage;
  return data;
}

export function createEnvelope(command, result, options = {}) {
  const { backend = 'jev', version = '0.0.0' } = options;
  const failed = !result?.ok;
  const failure = failed ? result ?? {} : {};
  const status = failed ? statusForFailure(failure) : 'OK';
  const code = failed ? exitCodeForFailure(failure) : 0;
  const data = Object.hasOwn(options, 'data') ? options.data : failed ? null : resultData(result);
  const error = failed ? {
    code: status,
    exit_code: code,
    message: failure.error ?? failure.message ?? status,
    command: `classifier ${command} --help`,
  } : null;
  return {
    ok: !failed,
    schema: `classifier.${command}.v1`,
    status,
    data,
    meta: {
      version,
      backend,
      model: result?.model ?? null,
      latency_ms: result?.latencyMs ?? 0,
      usage: result?.usage ?? null,
    },
    warnings: [],
    commands: error ? [error.command] : [],
    errors: error ? [error] : [],
  };
}
