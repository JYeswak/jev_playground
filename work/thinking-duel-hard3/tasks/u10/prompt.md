# Task u10: stable lazy merge of k sorted iterables

Work in $PWD. `kmerge.py` has `merge_sorted(sources, key=None)` returning an
iterator over all items of `sources` (an iterable of sorted iterables, each
ascending by `key`) in ascending `key` order. It is wrong. Fix it, standard
library only. Verify yourself with unorderable items sharing keys, a pull
count check proving laziness, a `key` function, and empty inputs.

Spec:
- `key=None` means identity. Items with equal keys come out in source
  order (lower source index first); within one source, original order.
- Lazy: never hold more than one pending item per source; pulling `N`
  outputs advances each source iterator by at most (outputs taken from it
  + 1). Must handle sources that can only be iterated once, and empty
  sources (skip them); empty `sources` yields nothing.
