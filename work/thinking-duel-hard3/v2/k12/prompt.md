# Task k12: versioned dependency resolver

Work in $PWD. `resolver.py` has `resolve(index, reqs)` where index maps
package -> sorted ascending version list, and reqs maps package ->
(min_version, max_exclusive_or_None). Return a dict package -> version
picking the MAXIMUM version satisfying all constraints, or None if
unsatisfiable. Single-version packages: only that version qualifies.
shipped code picks minima and ignores unsatisfiability. Fix it, stdlib only
(plain version-string compare by numeric parts). Verify yourself.
