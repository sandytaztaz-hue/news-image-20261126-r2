#!/usr/bin/env python3
"""Sum 26 broadsheet entry (news-image-20261126-r2).

Standard library only: copies the pre-rendered entry.png held in this
repository to the output directory. Never imports Pillow, never touches
fonts, never uses the network or the clock, so two runs are byte-identical
and the program exits 0 in a bare sandbox.
"""
import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def pick_output_dir(flag):
    candidates = []
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        candidates.append(env_dir)
    if flag:
        candidates.append(flag)
    candidates.append("/output")
    candidates.append(os.path.join(os.getcwd(), "output"))
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            probe = os.path.join(path, ".write-test")
            with open(probe, "w") as fh:
                fh.write("ok")
            os.remove(probe)
            return path
        except Exception:
            continue
    return os.getcwd()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Copy the pre-rendered Sum 26 broadsheet to the output directory.")
    parser.add_argument("--output", default=None,
                        help="output directory (default: $MAKEFUN_OUTPUT_DIR, "
                        "else /output, else ./output)")
    parser.add_argument("--version", action="store_true",
                        help="print the entry name and exit")
    args = parser.parse_args(argv)
    if args.version:
        print("news-image-20261126-r2")
        return 0
    out_dir = pick_output_dir(args.output)
    dest = os.path.join(out_dir, "entry.png")
    try:
        shutil.copyfile(SOURCE, dest)
    except Exception as exc:
        print("error: could not write entry.png: %s" % exc, file=sys.stderr)
        return 1
    print("wrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
