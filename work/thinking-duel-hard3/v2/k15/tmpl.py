import re


def render(template, ctx):
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: str(ctx.get(m.group(1), "")), template)
    return out
