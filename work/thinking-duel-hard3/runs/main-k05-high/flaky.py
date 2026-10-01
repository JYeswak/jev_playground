def find_flaky(results, lo=0.05, hi=0.95, min_runs=10):
    out = []
    for name, runs in results.items():
        n = len(runs)
        if n < min_runs or n == 0:
            continue
        fail_rate = sum(1 for r in runs if not r) / n
        if lo <= fail_rate <= hi:
            out.append(name)
    return sorted(out)
