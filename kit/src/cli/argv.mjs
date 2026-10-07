const COMMANDS = ['doctor', 'health', 'repair', 'ask', 'rank', 'rerank', 'classify', 'verify', 'score', 'gate', 'omp', 'install', 'uninstall'];
const DESTRUCTIVE_OPTIONS = new Set(['--apply', '--force', '--yes', '--delete', '--remove', '--adopt', '--take-over-bin']);
const COMMON = new Set(['--json', '--robot', '--no-color']);
const VALUE_OPTIONS = {
  doctor: new Set(['--only', '--skip']),
  repair: new Set(['--only']),
  ask: new Set(['--state', '--question']),
  rerank: new Set(['--query', '--candidates']),
  classify: new Set(['--text', '--labels']),
  verify: new Set(['--claim', '--evidence']),
  score: new Set(['--text', '--levels']),
  gate: new Set(['--command']),
  omp: new Set(['--dir']),
  install: new Set(['--dir']),
  uninstall: new Set(['--dir']),
};
const BOOLEAN_OPTIONS = {
  doctor: new Set(['--quick', '--deep', '--online']),
  repair: new Set(['--apply']),
  ask: new Set(['--fake']),
  rerank: new Set(['--fake']),
  classify: new Set(['--fake']),
  verify: new Set(['--fake']),
  score: new Set(['--fake']),
  gate: new Set(['--fake']),
  omp: new Set(['--dry-run', '--apply']),
  install: new Set(['--dry-run', '--apply']),
  uninstall: new Set(['--dry-run', '--apply']),
};

function oneEditOrSwap(left, right) {
  if (left === right) return true;
  if (Math.abs(left.length - right.length) > 1) return false;
  if (left.length === right.length) {
    let first = -1;
    let second = -1;
    for (let i = 0; i < left.length; i += 1) {
      if (left[i] !== right[i]) {
        if (first === -1) first = i;
        else if (second === -1) second = i;
        else return false;
      }
    }
    if (second === -1) return first !== -1;
    return second === first + 1 && left[first] === right[second] && left[second] === right[first];
  }
  const shorter = left.length < right.length ? left : right;
  const longer = left.length < right.length ? right : left;
  let i = 0;
  let j = 0;
  let skipped = false;
  while (i < shorter.length && j < longer.length) {
    if (shorter[i] === longer[j]) {
      i += 1;
      j += 1;
    } else if (skipped) {
      return false;
    } else {
      skipped = true;
      j += 1;
    }
  }
  return true;
}

function suggestionFor(value, candidates) {
  if (value.length > 64 || DESTRUCTIVE_OPTIONS.has(value)) return undefined;
  const matches = candidates.filter((candidate) => !DESTRUCTIVE_OPTIONS.has(candidate) && oneEditOrSwap(value, candidate));
  return matches.length === 1 ? matches[0] : undefined;
}

function shellQuote(value) {
  if (value.length > 0 && value.length <= 256) {
    let safe = true;
    for (let i = 0; i < value.length; i += 1) {
      const code = value.charCodeAt(i);
      const alphaNumeric = (code >= 48 && code <= 57) || (code >= 65 && code <= 90) || (code >= 97 && code <= 122);
      if (!alphaNumeric && !'._/:=+-'.includes(value[i])) {
        safe = false;
        break;
      }
    }
    if (safe) return value;
  }
  return `'${value.replaceAll("'", "'\\''")}'`;
}

function optionsFor(command, subcommand) {
  const optionCommand = command === 'rank' ? 'rerank' : command;
  const values = new Set(VALUE_OPTIONS[optionCommand] ?? []);
  const booleans = new Set([...(BOOLEAN_OPTIONS[optionCommand] ?? []), ...COMMON]);
  if (optionCommand === 'omp' && subcommand === 'install') booleans.delete('--apply');
  if (optionCommand === 'omp' && subcommand === 'uninstall') booleans.delete('--dry-run');
  return { values, booleans };
}

export function parseArgv(args) {
  const tokens = [...args];
  const outputMode = tokens.includes('--robot') ? 'robot' : tokens.includes('--json') ? 'json' : 'human';
  const help = tokens.includes('--help') || tokens.includes('-h') || tokens[0] === 'help';
  const version = tokens.length === 1 && tokens[0] === '--version';
  const commandIndex = tokens.findIndex((token) => !token.startsWith('-') && token !== 'help');
  const command = commandIndex >= 0 ? tokens[commandIndex] : null;
  const commandArgs = commandIndex >= 0 ? tokens.filter((_, index) => index !== commandIndex) : tokens;
  if (help || version) return { command: command === 'help' ? null : command, subcommand: null, positionals: [], options: {}, outputMode, help, version };

  const commandError = command && !COMMANDS.includes(command) ? command : null;
  if (commandError) {
    const suggestion = suggestionFor(commandError, COMMANDS);
    const correctedArgs = tokens.slice();
    if (suggestion) correctedArgs[commandIndex] = suggestion;
    return {
      command: null, subcommand: null, positionals: [], options: {}, outputMode, help, version,
      error: { message: `Unknown command: ${commandError}`, ...(suggestion ? { correctedCommand: ['classifier', ...correctedArgs].map(shellQuote).join(' ') } : {}) },
    };
  }

  const subcommands = command === 'ask' ? ['choice', 'score', 'noul'] : command === 'omp' ? ['install', 'uninstall'] : command === 'repair' ? ['undo'] : [];
  let firstPositional = null;
  for (let i = 0; i < commandArgs.length; i += 1) {
    const token = commandArgs[i];
    if (token.startsWith('-')) {
      if (VALUE_OPTIONS[command]?.has(token)) i += 1;
      continue;
    }
    firstPositional = token;
    break;
  }
  const subcommand = subcommands.length ? firstPositional : null;
  const validSubcommand = !subcommands.length || (command === 'repair' && subcommand === null) || subcommands.includes(subcommand);
  const { values, booleans } = optionsFor(command, subcommand);
  const options = {};
  const positionals = [];
  let error;
  for (let i = 0; i < commandArgs.length; i += 1) {
    const token = commandArgs[i];
    if (token === '--json' || token === '--robot' || token === '--no-color') {
      options[token.slice(2)] = true;
      continue;
    }
    if (token.startsWith('-')) {
      if (booleans.has(token)) {
        options[token.slice(2)] = true;
        continue;
      }
      if (values.has(token)) {
        const value = commandArgs[i + 1];
        if (!value || value.startsWith('-')) {
          error = { message: `Missing value for ${token}` };
          break;
        }
        options[token.slice(2)] = value;
        i += 1;
        continue;
      }
      const candidates = [...booleans, ...values];
      const suggestion = suggestionFor(token, candidates);
      const correctedArgs = tokens.slice();
      if (suggestion) correctedArgs[i + (commandIndex >= 0 ? 1 : 0)] = suggestion;
      error = {
        message: `Unknown option: ${token}`,
        ...(suggestion ? { correctedCommand: ['classifier', ...correctedArgs].map(shellQuote).join(' ') } : {}),
      };
      break;
    }
    if (subcommand && subcommands.includes(token) && !positionals.length) {
      positionals.push(token);
      continue;
    }
    if (subcommand && positionals.length === 0) {
      positionals.push(token);
      continue;
    }
    positionals.push(token);
  }
  if (!validSubcommand && !error) error = { message: `Unknown ${command} command: ${subcommand}` };
  return { command, subcommand, positionals, options, outputMode, help, version, ...(error ? { error } : {}) };
}
