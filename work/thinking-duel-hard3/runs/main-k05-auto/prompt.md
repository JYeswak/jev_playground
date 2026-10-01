# Task k05: flaky test detector

Work in $PWD. `flaky.py` has `find_flaky(results, lo=0.05, hi=0.95,
min_runs=10)` where results maps test name -> list of bool (True = pass).
Return the sorted names whose fail rate is within [lo, hi] AND that ran at
least min_runs times. Always-failing and always-passing tests are NOT flaky.
Empty result lists are ignored. shipped code flags every failure. Fix it.
Verify yourself.
