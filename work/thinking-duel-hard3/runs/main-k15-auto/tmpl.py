import html
import re

_VAR_RE = re.compile(r"^(\w+)(?:\s*\|\s*escape)?$")
_VAR_ESC_RE = re.compile(r"^(\w+)\s*\|\s*escape$")
_IF_RE = re.compile(r"^if\s+(\w+)$")


def _str(val):
    if val is None:
        return ""
    return str(val)


def render(template, ctx):
    if ctx is None:
        ctx = {}

    def render_section(pos, in_if):
        out = []
        n = len(template)
        while pos < n:
            var_idx = template.find("{{", pos)
            blk_idx = template.find("{%", pos)
            if var_idx == -1 and blk_idx == -1:
                out.append(template[pos:])
                pos = n
                break
            if var_idx != -1 and (blk_idx == -1 or var_idx < blk_idx):
                out.append(template[pos:var_idx])
                end = template.find("}}", var_idx + 2)
                if end == -1:
                    out.append(template[var_idx:])
                    pos = n
                    break
                inner = template[var_idx + 2 : end].strip()
                m_esc = _VAR_ESC_RE.match(inner)
                m_var = _VAR_RE.match(inner)
                if m_esc:
                    out.append(
                        html.escape(_str(ctx.get(m_esc.group(1), "")), quote=True)
                    )
                elif m_var:
                    out.append(_str(ctx.get(m_var.group(1), "")))
                else:
                    out.append(template[var_idx : end + 2])
                pos = end + 2
            else:
                out.append(template[pos:blk_idx])
                end = template.find("%}", blk_idx + 2)
                if end == -1:
                    out.append(template[blk_idx:])
                    pos = n
                    break
                inner = template[blk_idx + 2 : end].strip()
                m_if = _IF_RE.match(inner)
                if m_if:
                    cond = bool(ctx.get(m_if.group(1)))
                    rendered, pos = render_section(end + 2, True)
                    if cond:
                        out.append(rendered)
                elif inner == "endif":
                    if in_if:
                        pos = end + 2
                        return "".join(out), pos
                    out.append(template[blk_idx : end + 2])
                    pos = end + 2
                else:
                    out.append(template[blk_idx : end + 2])
                    pos = end + 2
        return "".join(out), pos

    result, _ = render_section(0, False)
    return result
