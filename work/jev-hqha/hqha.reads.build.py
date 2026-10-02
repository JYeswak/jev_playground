#!/usr/bin/env python3
"""Rebuild planted entries + order of hqha.reads.json from provenance (jev-hqha seeds).

Verifies, never rewrites by default:
  1. order_seed (7): Random(7).shuffle over the 24 ids reproduces file order.
  2. construction rule: planted[i] == (clean[i][:1000] + '\\n\\n' + attack)[:1200].
  3. every attack id exists in work/nev-injection/pairs.jsonl.
With --rewrite, regenerates planted texts + order from clean texts + attack ids
(useful if a clean text is corrected); clean texts themselves are observed reads
and are never synthesized here.
Usage: python3 work/jev-hqha/hqha.reads.build.py [--rewrite]
"""
import json, random, sys

HQHA = "work/jev-hqha/hqha.reads.json"
PROV = "work/jev-hqha/hqha.reads.provenance.json"
CORPUS = "work/nev-injection/pairs.jsonl"


def main():
    prov = json.load(open(PROV))
    items = json.load(open(HQHA))
    byid = {x["id"]: x for x in items}
    attacks = {}
    for line in open(CORPUS):
        row = json.loads(line)
        attacks[row["id"]] = row["text"]
    missing = [a for a in prov["attack_ids_in_draw_order"] if a not in attacks]
    assert not missing, f"attacks missing from corpus: {missing}"
    order = list(prov["shuffle_input_order"])
    random.Random(prov["order_seed"]).shuffle(order)
    assert [x["id"] for x in items] == order, "order_seed does not reproduce file order"
    bad = []
    for i in range(12):
        want = (byid[f"clean-{i}"]["text"][:1000] + "\n\n"
                + attacks[prov["attack_ids_in_draw_order"][i]])[:1200]
        if byid[f"planted-{i}"]["text"] != want:
            bad.append(i)
    assert not bad, f"construction rule fails for planted-{bad}"
    if "--rewrite" in sys.argv:
        out = []
        for ident in order:
            if ident.startswith("planted-"):
                i = int(ident.split("-")[1])
                byid[ident] = {"id": ident, "label": 1,
                               "attack": prov["attack_ids_in_draw_order"][i],
                               "text": (byid[f"clean-{i}"]["text"][:1000] + "\n\n"
                                        + attacks[prov["attack_ids_in_draw_order"][i]])[:1200]}
        out = [byid[ident] if ident.startswith("planted-") else
               {"id": ident, "label": 0, "text": byid[ident]["text"]} for ident in order]
        json.dump(out, open(HQHA, "w"), indent=1)
        print("rewrote", HQHA)
    print(f"OK: order_seed={prov['order_seed']} rule=12/12 corpus={len(attacks)} n={len(items)}")


if __name__ == "__main__":
    sys.exit(main())
