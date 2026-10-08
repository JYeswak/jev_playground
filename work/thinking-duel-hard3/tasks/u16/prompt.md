# Task u16: semver range intersection

Work in $PWD. `semrange.py` has `intersects(r1, r2) -> bool`: do two
npm-style range strings share at least one version? Support `*`, exact
`1.2.3`, partials (`1`, `1.2`, `1.2.x`, `1.*`), caret (`^1.2.3` means
`>=1.2.3 <2.0.0`, but `^0.2.3` means `>=0.2.3 <0.3.0` and `^0.0.3` means
`>=0.0.3 <0.0.4`), tilde (`~1.2.3` means `>=1.2.3 <1.3.0`, `~1` means
`>=1.0.0 <2.0.0`), hyphen (`1.2.0 - 1.3.0`, BOTH ends inclusive; a partial
upper like `1.2.3 - 2.3` means `<2.4.0`, `1.2.3 - 2` means `<3.0.0`), and
comparator sets (`>=1.0.0 <2.0.0`, comma or space separated; partials in
comparators are zero-padded, so `>1.2` means `>1.2.0`); a leading `v` is
ignored. Prereleases: a version with a tag (e.g. `1.0.1-alpha`) satisfies
a range only if that range's text mentions a prerelease with the same
`major.minor.patch` (so `^1.0.0` does NOT match `1.0.1-alpha`, but
`>=1.0.1-alpha <2.0.0` DOES match `1.0.1-beta`). It is wrong (botches
`^0.x`, `~1`, hyphen ends, and ignores prerelease rules). Fix it, stdlib
only. Verify yourself with those cases plus disjoint/adjacent ranges.
