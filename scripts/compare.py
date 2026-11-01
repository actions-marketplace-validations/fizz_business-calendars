"""Compare two calendar files and print the added and removed dates as Markdown.

Used for release notes (old vs new) and for cross-checking a calendar from one
source against another, such as holidaydb against python-holidays.

Usage: python scripts/compare.py OLD.json NEW.json [--label US]
Exit 0 when the files agree, 1 when they differ.
"""

import argparse
import json
import sys
from pathlib import Path


def read(path):
    p = Path(path)
    return {h["date"]: h["name"] for h in json.loads(p.read_text())} if p.exists() else {}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--label", default="")
    args = ap.parse_args(argv)

    old, new = read(args.old), read(args.new)
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    renamed = sorted(d for d in set(old) & set(new) if old[d] != new[d])
    if not (added or removed or renamed):
        return 0

    prefix = f"{args.label}: " if args.label else ""
    for d in added:
        print(f"- {prefix}added {d} {new[d]}")
    for d in removed:
        print(f"- {prefix}removed {d} {old[d]}")
    for d in renamed:
        print(f"- {prefix}renamed {d} {old[d]} → {new[d]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
