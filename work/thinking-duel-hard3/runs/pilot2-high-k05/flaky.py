def find_flaky(results, lo=0.05, hi=0.95, min_runs=10):
    out = []
    for name, runs in results.items():
        if not runs:
            continue
        n = len(runs)
        if n < min_runs:
            continue
        fails = sum(1 for r in runs if not r)
        if fails == 0 or fails == n:
            continue
        fail_rate = fails / n
        if lo <= fail_rate <= hi:
            out.append(name)
    return sorted(out)
