import base64


def decode_chunks(chunks):
    return base64.b64decode("".join(chunks))
