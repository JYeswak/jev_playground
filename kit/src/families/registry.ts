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

export const FAMILIES = Object.freeze([
  { name: 'classify', runner: 'classify', primitive: 'choice', aliases: [], usage: 'classify --text T --labels FILE', description: 'Choose a label from the offered set.' },
  { name: 'rank', runner: 'rerank', primitive: 'choice', aliases: ['rerank'], usage: 'rank --query Q --candidates FILE', description: 'Select a top candidate; rerank is an alias.' },
  { name: 'verify', runner: 'verify', primitive: 'noul', aliases: [], usage: 'verify --claim C --evidence FILE', description: 'Check a claim against evidence.' },
  { name: 'score', runner: 'score', primitive: 'score', aliases: [], usage: 'score --text T --levels FILE', description: 'Rate text against an ordered rubric.' },
  { name: 'gate', runner: 'gate', primitive: 'noul', aliases: [], usage: 'gate --command C', description: 'Assess command risk.' },
]);

const META_VERBS: Record<string, true> = {
  overview: true, capabilities: true, 'robot-docs': true, schema: true,
  doctor: true, install: true, ask: true, help: true, skillgap: true,
};
const FAMILY_VERBS: Record<string, true> = {
  run: true, batch: true, explain: true, cases: true, eval: true, calibrate: true,
};
const HERMES_VERBS: Record<string, true> = {
  route: true, rerank: true, triage: true, search: true, plan: true, choose: true,
};

export function validateFamilyNames(families: readonly { name: string; aliases?: readonly string[] }[] = FAMILIES): string[] {
  const errors: string[] = [];
  const names = new Set<string>();
  for (const family of families) {
    const name = family.name;
    if (names.has(name)) errors.push(`duplicate family name: ${name}`);
    names.add(name);
    if (name.length < 3 || name.length > 10 || name !== name.toLowerCase() || name.includes('-')) errors.push(`invalid family name: ${name}`);
    if (META_VERBS[name] || FAMILY_VERBS[name] || HERMES_VERBS[name]) errors.push(`reserved family name: ${name}`);
  }
  return errors;
}

export type FamilyDefinition = {
  name: string;
  runner: string;
  primitive: string;
  aliases?: readonly string[];
  usage: string;
  description: string;
};

type CommandInfo = { name: string; usage: string; exit_codes: number[]; description: string; [key: string]: unknown };
type Capabilities = { version: string; contract_version: string; features: Record<string, boolean>; commands: Record<string, CommandInfo>; exit_codes: typeof EXIT_CODES; env_vars: Record<string, string> };

export function createFamilyRegistry(families: readonly FamilyDefinition[] = FAMILIES) {
  const registeredFamilies = Object.freeze(families.map((family) => Object.freeze({
    ...family,
    aliases: Object.freeze([...(family.aliases ?? [])]),
  })));

  function familyForCommand(name: string) {
    return registeredFamilies.find((candidate) => candidate.name === name || candidate.aliases.includes(name));
  }

  function dispatchCommand(name: string): string {
    const family = familyForCommand(name);
    return family?.aliases[0] ?? name;
  }

  function capabilities(): Capabilities {
    const commands: Record<string, CommandInfo> = {
      capabilities: { name: 'capabilities', usage: 'capabilities --json', exit_codes: [0, 64], description: 'Print the command registry.' },
      'robot-docs': { name: 'robot-docs', usage: 'robot-docs guide', exit_codes: [0, 64], description: 'Print the concise agent guide.' },
      schema: { name: 'schema', usage: 'schema [--command NAME]', exit_codes: [0, 64], description: 'Print the full or command-specific JSON schema.' },
      help: { name: 'help', usage: 'help [COMMAND]', exit_codes: [0], description: 'Show command help.' },
      doctor: { name: 'doctor', usage: 'doctor [--json|--robot]', exit_codes: [0, 2, 6, 64, 74], description: 'Check local readiness.' },
      ask: { name: 'ask', usage: 'ask choice|score|noul --state FILE --question FILE', exit_codes: [0, 1, 2, 3, 64, 66, 74], description: 'Judge a typed question.' },
      'omp install': { name: 'omp install', usage: 'omp install [--dir DIR] [--dry-run]', exit_codes: [0, 1, 4, 64, 66, 73, 74], description: 'Install project-scoped omp files.' },
      'omp uninstall': { name: 'omp uninstall', usage: 'omp uninstall [--dir DIR] [--apply]', exit_codes: [0, 4, 64, 74], description: 'Uninstall unedited project-scoped omp files.' },
    };
    for (const family of registeredFamilies) {
      const { runner: _runner, ...metadata } = family;
      commands[family.name] = {
        ...metadata,
        name: family.name,
        exit_codes: [0, 1, 2, 3, 5, 6, 64, 66, 74],
        output_format: 'classifier.<command>.v1',
      };
    }
    return {
      version: '0.0.0',
      contract_version: '1',
      features: { json: true, robot: true, fake: true, family_registry: true },
      commands,
      exit_codes: EXIT_CODES,
      env_vars: { TYPESAFE_API_KEY: 'Optional; presence only, never printed.' },
    };
  }

  function robotDocs(): string {
    const commandLines = Object.values(capabilities().commands)
      .map((command) => `- ${command.name}: ${command.description} Usage: ${command.usage}.`);
    const aliasLines = registeredFamilies
      .filter((family) => family.aliases.length > 0)
      .map((family) => `- \`${family.aliases.join('`, `')}\` aliases \`${family.name}\`.`);
    return [
      '# classifier robot guide',
      'Use `classifier capabilities --json` to inspect the supported command contract.',
      'Use `--robot` for versioned JSON envelopes; use `--json` for command JSON.',
      'Decision commands accept `--fake` for captured, offline fixtures.',
      'Exit codes: 0 success, 1 findings, 2 NOT_RUN, 3 refused, 4 refused_unsafe, 5 retryable, 6 online_required, 64 usage, 66 no_input, 73 cant_create, 74 io.',
      ...commandLines,
      ...aliasLines,
      'Errors in robot mode are returned in the envelope `errors` array.',
    ].join('\n');
  }

  function schema(command?: string): Capabilities {
    const contract = capabilities();
    if (!command) return contract;
    const aliasName = registeredFamilies.find((family) => family.aliases.includes(command))?.name;
    const name = Object.hasOwn(contract.commands, command) ? command : aliasName;
    if (!name) throw Object.assign(new Error(`unknown schema command: ${command}`), { code: 'USAGE' });
    return { ...contract, commands: { [name]: contract.commands[name] } };
  }

  return Object.freeze({
    families: registeredFamilies,
    validateFamilyNames: () => validateFamilyNames(registeredFamilies),
    familyForCommand,
    dispatchCommand,
    capabilities,
    robotDocs,
    schema,
  });
}

export const FAMILY_REGISTRY = createFamilyRegistry();

export function dispatchCommand(name: string): string {
  return FAMILY_REGISTRY.dispatchCommand(name);
}

export function capabilities(): Capabilities {
  return FAMILY_REGISTRY.capabilities();
}

export function robotDocs(): string {
  return FAMILY_REGISTRY.robotDocs();
}

export function schema(command?: string): Capabilities {
  return FAMILY_REGISTRY.schema(command);
}
