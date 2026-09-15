#!/usr/bin/env python3
# betterfinder - reads a subdomain list, writes out the narrower "levels"
# worth re-running your discovery tools against. does not query anything
# itself.
#
# free recon sources (crt.sh, hackertarget, otx, whatever) each do ONE
# bulk lookup per apex domain, and on a big/high-volume domain that
# single query can silently come back incomplete - no error, just fewer
# rows than actually exist. the fix that works: once a label shows up
# more than once in what you've already found ("staging.domain.com",
# "data.domain.com"...), rerun your discovery tools against THAT LABEL
# ALONE. narrower queries dodge the same truncation and often reveal
# whole clusters the bulk query hid.
#
# betterfinder does only that one thing. feed it a subdomain list, it
# hands back which narrower domains are worth another discovery pass.
# pipe that into subfinder/crt.sh/whatever, merge what you find back in,
# and run betterfinder again on the bigger list for another round if you
# want. no deps, no network calls.

import argparse
import sys
from pathlib import Path


def in_scope(h, apex):
    return h == apex or h.endswith("." + apex)


def ancestors(hosts, apex):
    # every strict ancestor domain (apex-exclusive, leaf-exclusive) in
    # `hosts`, with a count of how many hosts share it. leaf-self is
    # skipped on purpose: a host's own exact name is a low-value rescan
    # target, ancestor labels with fan-out are where hidden clusters
    # actually turn up.
    a = apex.split(".")
    counts = {}
    for h in hosts:
        parts = h.split(".")
        depth = len(parts) - len(a)
        for i in range(1, depth):  # skip i=0, the leaf itself
            lvl = ".".join(parts[i:])
            counts[lvl] = counts.get(lvl, 0) + 1
    return counts


def main():
    p = argparse.ArgumentParser(
        description="extract narrower domains worth re-running discovery "
                     "against, from a subdomain list you already have")
    p.add_argument("-d", "--domain", required=True)
    p.add_argument("-i", "--input", type=Path, help="subdomain list, one per line (default: stdin)")
    p.add_argument("-o", "--output", type=Path, help="default: stdout")
    p.add_argument("--fanout", type=int, default=2, help="min known children before a label counts (default: 2)")
    p.add_argument("--seen", type=Path, help="labels already probed - excluded from output, then appended to")
    args = p.parse_args()

    text = args.input.read_text() if args.input else sys.stdin.read()
    hosts = {h for h in (l.strip().lower() for l in text.splitlines()) if h and in_scope(h, args.domain)}

    seen = set()
    if args.seen and args.seen.exists():
        seen = {l.strip().lower() for l in args.seen.read_text().splitlines() if l.strip()}

    counts = ancestors(hosts, args.domain)
    levels = sorted(l for l, n in counts.items() if n >= args.fanout and l not in seen)

    out = "".join(l + "\n" for l in levels)
    (args.output.write_text(out) if args.output else sys.stdout.write(out))

    if args.seen:
        with args.seen.open("a") as f:
            f.writelines(l + "\n" for l in levels)

    print(f"[betterfinder] {len(levels)} level(s) to rescan", file=sys.stderr)


if __name__ == "__main__":
    main()
