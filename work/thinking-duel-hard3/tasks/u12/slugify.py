import unicodedata


def slugify(text, max_len=50):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower()
    out = []
    for ch in text:
        out.append(ch if ch.isalnum() else "-")
    return "".join(out).strip("-")[:max_len]
