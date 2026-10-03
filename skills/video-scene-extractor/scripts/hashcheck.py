#!/usr/bin/env python3
"""Frame identity / difference spot-check (arbitration tool).

Usage: hashcheck.py <a.png> <b.png>
Resizes both to 64x36 gray; prints md5 of each and mean|delta|. mean|delta| == 0.00
means pixel-identical at that scale (same frame). Use to arbitrate disputed
montage cells / extraction results: re-extract one frame independently and compare.
"""
import sys, hashlib
from PIL import Image

def g64(p):
    im = Image.open(p).convert("L").resize((64,36))
    return im.tobytes()

def main():
    a, b = g64(sys.argv[1]), g64(sys.argv[2])
    ma = sum(abs(x-y) for x,y in zip(a,b))/len(a)
    print(f"{sys.argv[1]}: md5={hashlib.md5(a).hexdigest()[:12]}")
    print(f"{sys.argv[2]}: md5={hashlib.md5(b).hexdigest()[:12]}")
    print(f"mean|delta| = {ma:.2f}  ({'IDENTICAL' if ma < 0.005 else 'different'})")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: hashcheck.py <a.png> <b.png>")
    main()
