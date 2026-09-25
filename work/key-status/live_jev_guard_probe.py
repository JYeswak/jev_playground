#!/usr/bin/env python3
"""Import MiniWoB's LiveAsker and construct it for the revoked-key test."""

import sys

sys.path.insert(0, "work/miniwob-jev")
import jev_arm  # noqa: E402

jev_arm.LiveAsker()
