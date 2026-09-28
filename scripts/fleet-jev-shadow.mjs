// A previously started watcher may still launch this child. Until pane owners
// approve the recipient and allowed evidence fields, refuse before reading stdin.
process.stderr.write("NOT_RUN reason=permission-required\n");
process.exitCode = 2;
