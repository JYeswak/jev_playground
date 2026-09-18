export function parse(input) {
  if (input == null || input === '') throw new Error('empty input');
  return [input];
}
