export const OVERVIEW_HELP = `classifier — model-neutral decision CLI
Usage:
  classifier
  classifier <command> [options]
  classifier <command> --help

Commands:
  doctor                 Check local readiness
  health                 Quick offline readiness
  ask choice|score|noul  Judge a typed question
  rerank                 Select a top candidate
  classify               Choose a label
  verify                 Check evidence for a claim
  score                  Rate text on a rubric
  gate                   Judge command risk
  omp install|uninstall  Manage project-scoped omp files
  install                Install project-scoped omp files
  uninstall              Uninstall project-scoped omp files

Global options:
  --json                 Emit command JSON (doctor keeps its raw report)
  --robot                Emit the versioned machine envelope
  --no-color             Disable styling
  -h, --help             Show help and exit
  --version              Print version and exit

Fixture option:
  --fake                 Use captured data; available on ask, rerank, classify, verify, score, and gate

Exit codes:
  0 success; 1 findings/NOT_RUN; 3 refused; 4 refused_unsafe
  5 retryable; 6 online_required; 64 usage; 66 no_input
  73 cannot_create; 74 I/O

Examples:
  classifier doctor --robot
  classifier ask choice --state kit/examples/state.json --question kit/examples/question.json --fake --robot`;

const DOCTOR_HELP = `classifier doctor [--quick|--deep] [--online] [--only ID,...] [--skip ID,...] [--json|--robot]

Diagnose local readiness without changing files. --json emits the raw report; --robot emits an envelope.`;

const HEALTH_HELP = `classifier health [--json|--robot]

Run quick offline readiness checks without changing files.`;

const ASK_HELP = `classifier ask choice|score|noul --state FILE --question FILE [--fake] [--json|--robot]

Examples:
  classifier ask choice --state kit/examples/state.json --question kit/examples/question.json --fake --robot

Exit codes:
  0 success; 1 findings/NOT_RUN; 3 refused; 64 usage; 66 no_input`;

export function helpFor(topic = '') {
  if (!topic) return OVERVIEW_HELP;
  if (topic === 'doctor') return DOCTOR_HELP;
  if (topic === 'health') return HEALTH_HELP;
  if (topic === 'ask') return ASK_HELP;
  return `${OVERVIEW_HELP}\n\nUse classifier ${topic} --help for command usage.`;
}
