export function failEmpty(reason) {
  console.error(`EMPTY_SCAN: ${reason}`);
  process.exit(2);
}
