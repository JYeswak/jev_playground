def allocate(total_cents, weights):
    total_w = sum(weights)
    return [round(total_cents * w / total_w) for w in weights]
