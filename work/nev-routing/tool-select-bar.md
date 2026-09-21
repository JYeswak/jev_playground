# Tool-selection bar — written before the first score

Corpus: `work/nev-routing/tool-select-labelled.jsonl`. Unlabelled rows are not negatives.

Decision, fixed now:

- Score a name-match router: overlap between `context` tokens and each candidate tool name. Top-1 is the highest overlap. Zero overlap abstains.
- Report top-1 and recall separately. Recall is only over rows where `label != prev_tool`, so repeating the same tool cannot hide a collapse.
- **Bit 1 YES, seat dies,** if that recall is at least 0.25.
- **Collapse, seat live,** if that recall is below 0.10.
- Between those, UNDERPOWERED. Do not kill and do not claim a seat.
- Moving this bar after seeing the rate is forbidden.

Not scored in the turn that wrote this file.
