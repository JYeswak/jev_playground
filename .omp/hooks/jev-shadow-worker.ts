// This legacy detached worker has no cross-process admission or recipient/data-class
// authorization contract. A stale loaded hook may still spawn it: refuse before
// reading stdin, resolving a key, writing a row, or contacting a provider.
process.stderr.write("NOT_RUN reason=permission-required\n");
process.exitCode = 2;
