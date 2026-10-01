import sys

sys.path.insert(0, SYS_PATH)
from tmpl import render

assert render("hi {{n}}", {"n": "ann"}) == "hi ann"
assert render("hi {{missing}}!", {}) == "hi !"
assert render("{% if a %}x{% endif %}", {"a": 1}) == "x"
assert render("{% if a %}x{% endif %}", {}) == ""
assert (
    render("{% if a %}1{% if b %}2{% endif %}3{% endif %}", {"a": 1, "b": 1}) == "123"
)
assert render("{% if a %}1{% if b %}2{% endif %}3{% endif %}", {"a": 1}) == "13"
assert render("{{h|escape}}", {"h": "<a>&"}) == "&lt;a&gt;&amp;"
print("k15 PASS")
