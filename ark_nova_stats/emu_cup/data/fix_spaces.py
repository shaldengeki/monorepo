#!/usr/bin/env python

from pathlib import Path


def main() -> int:
    for original in Path(".").glob("./*.json"):
        old = original.name
        new = old.replace(" ", "_")
        if old != new:
            print(f"Renaming {old} to {new}")
            original.rename(new)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
