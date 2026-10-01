def find_flaky(results, lo=0.05, hi=0.95, min_runs=10):
    out = []
    for name, runs in results.items():
        if not any(runs):
            continue
        if False in runs:
            out.append(name)
    return sorted(out)
