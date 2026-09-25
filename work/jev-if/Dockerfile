# Jev-PUCT on Jericho (bead jev-jy7t.1.4). Same Dockerfile for both architectures:
#   docker build --platform linux/arm64 -t jev-if:wave1 work/jev-if
#   docker build --platform linux/amd64 -t jev-if:wave1-amd64 work/jev-if
# Use the amd64 image for scored runs. jericho 3.3.1's frotz segfaults on aarch64 on actions that
# x86_64 reports as "Emulator halted" and survives (Zork1 forest, 'put all in nest' holding the
# broken egg and canary). MC-DML does not state its platform. On Apple Silicon amd64 runs emulated.
# ROMs: the z-machine-games archive named in the Jericho README (microsoft/jericho
# README.md at d3eb30b^, "Download supported games"), pinned to a commit and checked by sha256.
# zork1.z5 and deephome.z5 are byte-identical to the copies bundled in winni18/MC-DML@7f13122.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl unzip ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# jericho 3.3.1 is the last 3.x release; MC-DML asserts jericho 3.x (main.py:59), and in 3.x
# FrotzEnv(rom) without a seed uses the walkthrough seed (jericho.py:444 at tag 3.3.1).
RUN pip install --no-cache-dir jericho==3.3.1 typesafe-sdk==0.7.1 spacy==3.8.16 \
 && python -m spacy download en_core_web_sm \
 && pip freeze > /opt/pip-freeze.txt

ARG ZMG_SHA=bfd7544aa1f50549fc327bd4eb3bc8144bfd80ea
RUN mkdir -p /opt/roms \
 && curl -sSL -o /tmp/zmg.zip "https://github.com/BYU-PCCL/z-machine-games/archive/${ZMG_SHA}.zip" \
 && unzip -q -j /tmp/zmg.zip \
      "z-machine-games-${ZMG_SHA}/jericho-game-suite/zork1.z5" \
      "z-machine-games-${ZMG_SHA}/jericho-game-suite/deephome.z5" \
      "z-machine-games-${ZMG_SHA}/jericho-game-suite/detective.z5" \
      -d /opt/roms \
 && rm /tmp/zmg.zip \
 && printf '%s\n' \
      "0ae5ac229e79094ff368b6669356444af0f35e21d862a1baaa546989085c15fd  /opt/roms/zork1.z5" \
      "fdae5bd090fda6fc1b0390051531190968e04355060153ad5b2ab6b75a387b31  /opt/roms/deephome.z5" \
      "f6b0b9b5f4ff8890ab481b11e63ea18350b43640c88a9b8c23d6a2b269f9a040  /opt/roms/detective.z5" \
    | sha256sum -c -

WORKDIR /app
COPY puct.py run.py test_puct.py /app/
# jericho's valid-action generation iterates sets of strings, so the order (and, for tied diffs,
# the representative string) of get_valid_actions depends on str hashing. A fixed hash seed makes
# a run fully determined by --seed: two runs with the same flags write identical rows.
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=0
ENTRYPOINT ["python", "/app/run.py"]
