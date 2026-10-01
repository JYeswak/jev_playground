import html
import re

VAR_RE = re.compile(r"\{\{\s*(\w+)\s*(?:\|\s*(\w+)\s*)?\}\}")
IF_RE = re.compile(r"\{%\s*if\s+(\w+)\s*%\}")
ENDIF_RE = re.compile(r"\{%\s*endif\s*%\}")
TOKEN_RE = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.DOTALL)


def _render_vars(tok, ctx):
    m = VAR_RE.fullmatch(tok)
    if not m:
        return tok
    name, filt = m.group(1), m.group(2)
    val = ctx.get(name, "")
    if val is None:
        val = ""
    else:
        val = str(val)
    if filt is None:
        return val
    if filt == "escape":
        return html.escape(val, quote=True)
    return ""


def _parse(template, ctx, pos, in_block):
    out = []
    while True:
        m = TOKEN_RE.search(template, pos)
        if not m:
            out.append(template[pos:])
            pos = len(template)
            break
        out.append(template[pos : m.start()])
        tok = m.group(0)
        pos = m.end()
        if IF_RE.fullmatch(tok):
            name = IF_RE.fullmatch(tok).group(1)
            cond = bool(ctx.get(name))
            inner, pos = _parse(template, ctx, pos, True)
            if cond:
                out.append(inner)
        elif ENDIF_RE.fullmatch(tok):
            if in_block:
                break
        elif VAR_RE.fullmatch(tok):
            out.append(_render_vars(tok, ctx))
        else:
            out.append(tok)
    return "".join(out), pos


def render(template, ctx):
    out, _ = _parse(template, ctx, 0, False)
    return out
