import { EXIT_CODES } from '../families/registry.js';

type ErrorInput = {
  reason?: string;
  message?: string;
  code?: string;
  command?: string;
  option?: string;
  correctedCommand?: string;
  cwd?: string;
  path?: string;
  count?: number;
  files?: string[];
};

export type CliError = {
  code: string;
  exit_code: number;
  message: string;
  remediation: string[];
  see: string;
};

function result(code: string, exitCode: number, message: string, remediation: string[], command = 'classifier'): CliError {
  return { code, exit_code: exitCode, message, remediation, see: `${command} --help` };
}

export function rewriteCliError(input: ErrorInput): CliError {
  const command = input.command ?? 'classifier';
  const message = input.message ?? '';
  if (input.reason === 'unknown-command') {
    const suggestion = input.correctedCommand ? `\ndid you mean: ${input.correctedCommand}` : '';
    return result('USAGE', EXIT_CODES.USAGE, `error: unknown command '${input.option ?? message}'${suggestion}`, [], command);
  }
  if (input.reason === 'unknown-option' && input.option === '--label') {
    return result('USAGE', EXIT_CODES.USAGE,
      'error: classify requires --labels FILE (got --label; did you mean --labels?)',
      ['example: classifier classify --text "How do I locate my card?" --labels kit/examples/banking77-labels.json --fake --json'], command);
  }
  if (input.reason === 'no-input' || input.code === 'ENOENT') {
    const option = input.option ?? (message.includes('labels') ? '--labels' : 'input');
    const path = input.path ?? message;
    const example = option === '--labels'
      ? 'example file: kit/examples/banking77-labels.json'
      : 'check that the input path exists and is readable';
    return result('NO_INPUT', EXIT_CODES.NO_INPUT,
      `error: ${option} file not found: ${path}${input.cwd ? ` (cwd ${input.cwd})` : ''}`,
      [example, `rerun: ${command} --help`], command);
  }
  if (input.reason === 'unconfigured' || message.includes('(unconfigured)')) {
    return result('NOT_RUN', EXIT_CODES.NOT_RUN, 'NOT_RUN: Jev backend has no key (TYPESAFE_API_KEY unset)',
      ['offline: add --fake', 'diagnose: classifier doctor'], command);
  }
  if (input.reason === 'invalid-answer' || input.reason === 'no-answers' || message.includes('unoffered label')) {
    const marker = 'unoffered label';
    const remainder = message.includes(marker) ? message.slice(message.indexOf(marker) + marker.length) : '';
    const label = remainder.replaceAll(':', '').replaceAll("'", '').trim().split(' ')[0];
    return result('REFUSED', EXIT_CODES.REFUSED,
      `REFUSED: model returned unoffered label '${label || 'unknown'}'; no decision emitted`, ['inspect: classifier classify --help'], command);
  }
  if (message.includes('chunking is not supported')) {
    const count = message.includes('got ') ? message.slice(message.indexOf('got ') + 4).split(';')[0] : 'more than 20';
    return result('USAGE', EXIT_CODES.USAGE, `error: rank takes 2-20 candidates, got ${count}`,
      ['keep the top 20 from your first-stage ranker, then: classifier rank --query Q --candidates top20.json'], command);
  }
  if (message.includes('captured public example command') || message.includes('fixture')) {
    return result('USAGE', EXIT_CODES.USAGE, `error: ${message}`,
      ['fixture command: classifier gate --fake --command "npm publish --access public"', 'list: classifier gate --help'], command);
  }
  if (message.includes('refusing to overwrite')) {
    const files = input.files ?? (message.includes(':') ? message.slice(message.indexOf(':') + 1).split(',').map((file) => file.trim()) : []);
    const listed = files.slice(0, 3).join(', ');
    return result('REFUSED_UNSAFE', EXIT_CODES.REFUSED_UNSAFE,
      `error: refusing to overwrite ${input.count ?? files.length} unmanaged files${listed ? `: ${listed}` : ''}`,
      ['preview: classifier install omp-project --dir REPO --dry-run', 'adopt only files you own: classifier install omp-project --dir REPO --apply'], command);
  }
  if (input.reason === 'refused-unsafe') {
    return result('REFUSED_UNSAFE', EXIT_CODES.REFUSED_UNSAFE,
      message || 'REFUSED_UNSAFE: installer refused to modify files', ['inspect the reported path before retrying'], command);
  }
  if (input.reason === 'transport' || input.reason === 'http') {
    return result('RETRYABLE', EXIT_CODES.RETRYABLE,
      message || 'RETRYABLE: transient operation failure', ['retry after the active operation or transient failure clears'], command);
  }
  if (input.reason === 'clef-unreachable') {
    return result('ONLINE_REQUIRED', EXIT_CODES.ONLINE_REQUIRED,
      `error: clef backend unreachable at ${input.path ?? 'http://127.0.0.1:8010/v1/systemone'}`,
      ['use hosted: --backend jev', 'diagnose: classifier doctor'], command);
  }
  const status = input.reason === 'usage' ? 'USAGE' : input.reason === 'io' ? 'IO' : 'FINDINGS';
  const exitCode = status === 'USAGE' ? EXIT_CODES.USAGE : status === 'IO' ? EXIT_CODES.IO : EXIT_CODES.FINDINGS;
  return result(status, exitCode, message || `error: ${status.toLowerCase()}`, [`rerun: ${command} --help`], command);
}

export function formatCliError(error: CliError): string {
  return [`${error.message}`, ...error.remediation, `see: ${error.see}`].join('\n');
}
