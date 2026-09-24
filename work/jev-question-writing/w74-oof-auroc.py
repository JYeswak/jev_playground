#!/usr/bin/env python3
"""OOF AUROC per shape + focus-free gain check. Usage: oof.py <scores.jsonl>.
Prints accuracy/CI per shape, 5-fold StratifiedKFold logreg OOF AUROC
(port of jev-spam-eval/spam_noul.py:333-343), and plain_focus minus plain
AUROC (the planted negative: must show no gain)."""
import json, math, sys
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
y = [1 if r['label'] == 'spam' else 0 for r in rows]
print(f'n={len(rows)} prev={sum(y)/len(y):.4f}')

def logit(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))

def oof_auc(scores):
    X = [[logit(s)] for s in scores]
    probs = cross_val_predict(LogisticRegression(max_iter=1000), X, y,
                              cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=0),
                              method='predict_proba')[:, 1]
    return roc_auc_score(y, probs)

res = {}
for shape in ['current', 'variant', 'plain', 'plain_focus']:
    s = [r[shape] for r in rows]
    acc = sum((v >= 0.5) == bool(t) for v, t in zip(s, y)) / len(y)
    res[shape] = oof_auc(s)
    print(f'{shape}: acc={acc:.4f} oof-auroc={res[shape]:.4f}')

gain = res['variant'] - res['current']
neg = res['plain_focus'] - res['plain']
print(f'variant-minus-current: {gain:+.4f} (bar: no regression, >= -0.0)')
print(f'focus-free gain: {neg:+.4f} (bar: no gain, <= +0.0)')
