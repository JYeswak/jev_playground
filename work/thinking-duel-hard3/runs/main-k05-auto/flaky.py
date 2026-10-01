def find_flaky(results, lo=0.05, hi=0.95, min_runs=10):
    out = []
    for name, runs in results.items():
        if len(runs) < min_runs:
            continue
        fail_rate = sum(1 for r in runs if not r) / len(runs)
        if lo <= fail_rate <= hi:
            out.append(name)
    return sorted(out)
