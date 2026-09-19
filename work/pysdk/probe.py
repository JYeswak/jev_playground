"""Live labeled probe: answers are fixed by construction and never shown to the model."""

import os
from typesafe_sdk import TypeSafeClient, Noul

client = TypeSafeClient(api_key=os.environ["TYPESAFE_API_KEY"])
CASES = [
    (
        "The engine caught fire and the flight was diverted. Two passengers were injured.",
        True,
    ),
    ("The in-flight meal was cold and the movie selection was limited.", False),
]
# The Python SDK REQUIRES instructions or criteria on a Noul; the JS `noul()` helper does not.
q = {"incident": Noul(instructions="Does this text describe a safety incident?")}
for text, want in CASES:
    r = client.system_one(state={"text": text}, questions=q)
    p = float(r.answers["incident"].noul)  # NoulAnswer exposes .noul, not .probability
    print(f"want={str(want):5} p={p:.3f} {'CORRECT' if (p > 0.5) == want else 'WRONG'}")
