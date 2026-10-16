// Fixture hostile entry for installer tests: declares a default export that
// is not a function. Both tiers must refuse it before any write, even though
// the `export default` prefix is present.
const nothing = null;

export default nothing;
