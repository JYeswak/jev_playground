import html
import re

_IF_RE = re.compile(r"\{%\s*if\s+(\w+)\s*%\}")
_ENDIF_RE = re.compile(r"\{%\s*endif\s*%\}")
_VAR_ESC_RE = re.compile(r"\{\{\s*(\w+)\s*\|\s*escape\s*\}\}")
_VAR_PLAIN_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _val(ctx, name):
    v = ctx.get(name, "")
    if v is None:
        return ""
    return v


def render(template, ctx):
    pos = 0
    n = len(template)

    def parse(stop=False):
        nonlocal pos
        parts = []
        while pos < n:
            if template.startswith("{%", pos):
                m_end = _ENDIF_RE.match(template, pos)
                if m_end:
                    if stop:
                        pos = m_end.end()
                        return "".join(parts)
                    parts.append(m_end.group(0))
                    pos = m_end.end()
                    continue
                m_if = _IF_RE.match(template, pos)
                if m_if:
                    pos = m_if.end()
                    inner = parse(stop=True)
                    if _val(ctx, m_if.group(1)):
                        parts.append(inner)
                    continue
                parts.append("{%")
                pos += 2
                continue
            if template.startswith("{{", pos):
                m_esc = _VAR_ESC_RE.match(template, pos)
                if m_esc:
                    parts.append(
                        html.escape(str(_val(ctx, m_esc.group(1))), quote=True)
                    )
                    pos = m_esc.end()
                    continue
                m_var = _VAR_PLAIN_RE.match(template, pos)
                if m_var:
                    parts.append(str(_val(ctx, m_var.group(1))))
                    pos = m_var.end()
                    continue
                parts.append("{{")
                pos += 2
                continue
            nxt1 = template.find("{{", pos)
            nxt2 = template.find("{%", pos)
            cands = [x for x in (nxt1, nxt2) if x != -1]
            nxt = min(cands) if cands else n
            parts.append(template[pos:nxt])
            pos = nxt
        return "".join(parts)

    return parse()
