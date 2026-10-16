import { exitCodeForFailure, statusForFailure } from './exit.mjs';

function resultData(result) {
  if (result === null || typeof result !== 'object' || Array.isArray(result)) return result ?? null;
  const data = { ...result };
  delete data.ok;
  delete data.latencyMs;
  delete data.latency_ms;
  delete data.usage;
  delete data.backend;
  delete data.backendRequested;
  delete data.routeReason;
  delete data.fallbackReason;
  return data;
}

export function createEnvelope(command, result, options = {}) {
  const version = options.version ?? '0.0.0';
  const backendRequested = result?.backendRequested ?? options.backendRequested ?? options.backend ?? 'jev';
  const backend = result?.backend ?? options.backend ?? (backendRequested === 'auto' ? 'jev' : backendRequested);
  const fallbackReason = result?.fallbackReason ?? result?.routeReason ?? options.fallbackReason ?? null;
  const failed = !result?.ok;
  const failure = failed ? result ?? {} : {};
  const status = failed ? statusForFailure(failure) : 'OK';
  const code = failed ? exitCodeForFailure(failure) : 0;
  const data = Object.hasOwn(options, 'data') ? options.data : failed ? null : resultData(result);
  const error = failed ? {
    code: status,
    exit_code: code,
    message: failure.error ?? failure.message ?? status,
    command: 'classifier ' + command + ' --help',
  } : null;
  return {
    ok: !failed,
    schema: 'classifier.' + command + '.v1',
    status,
    data,
    meta: {
      version,
      backend,
      backend_requested: backendRequested,
      fallback_reason: fallbackReason,
      model: result?.model ?? null,
      latency_ms: result?.latencyMs ?? 0,
      usage: result?.usage ?? null,
    },
    warnings: [],
    commands: error ? [error.command] : [],
    errors: error ? [error] : [],
  };
}
