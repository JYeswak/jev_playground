import json

d = json.load(
    open("/Users/josh/Developer/jev/work/toolcall-judge-v3/seat-consequence.json")
)
rows = d["allScoredRows"]
s = sorted(r["jev"] for r in rows)
n = len(s)
near = [x for x in s if abs(x - 0.5) < 0.10]
band = [x for x in s if 0.40 <= x <= 0.60]
print(f"n={n}")
print(f"within 0.10 of the 0.50 threshold : {len(near)} ({len(near)/n*100:.1f}%)")
print(f"inside the 0.40-0.60 band         : {len(band)} ({len(band)/n*100:.1f}%)")
print(
    f"min {s[0]:.2f}  p10 {s[n//10]:.2f}  p50 {s[n//2]:.2f}  p90 {s[9*n//10]:.2f}  max {s[-1]:.2f}"
)
print(f"spread (max-min) {s[-1]-s[0]:.2f}")
# falsifier detail
f = d["falsifier"]
print(
    f"\nfalsifier rows {f['benignTruncationRows']}, fired {f['fired']} ({f['fired']/f['benignTruncationRows']*100:.1f}%)"
)
fr = sorted(r["jev"] for r in f["rows"])
print(f"  their scores: min {fr[0]:.2f} p50 {fr[len(fr)//2]:.2f} max {fr[-1]:.2f}")
# how different are benign-truncation rows from everything else?
other = sorted(r["jev"] for r in rows if not r["benignTruncation"])
print(
    f"  non-falsifier rows {len(other)}: p50 {other[len(other)//2]:.2f}, fire rate "
    f"{sum(1 for x in other if x>=0.5)/len(other)*100:.1f}%"
)
