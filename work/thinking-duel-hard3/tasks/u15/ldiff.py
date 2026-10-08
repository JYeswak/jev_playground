"""Ordered-list diff with moves (buggy starter: never minimal)."""


def apply_script(seq, ops):
    s = list(seq)
    for op in ops:
        kind = op[0]
        if kind == "del":
            del s[op[1]]
        elif kind == "ins":
            s.insert(op[1], op[2])
        elif kind == "move":
            x = s.pop(op[1])
            s.insert(op[2], x)
        else:
            raise ValueError("unknown op %r" % (kind,))
    return s


def diff_lists(old, new):
    ops = []
    for _ in range(len(old)):
        ops.append(("del", 0))
    for i, v in enumerate(new):
        ops.append(("ins", i, v))
    return ops
