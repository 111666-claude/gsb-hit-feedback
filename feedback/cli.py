"""命令行入口：跑飘字样例。"""

import argparse

from .core import Numbers


def build_parser():
    parser = argparse.ArgumentParser(prog="hit-feedback", description="伤害飘字")
    parser.add_argument("--sample", default="merge", help="merge / cap / ttl / order / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "merge":
        numbers = Numbers(merge_ms=300, max_numbers=8)
        numbers.hit("mob", 10, 0)
        numbers.hit("mob", 20, 100)
        numbers.hit("mob", 30, 200)
        rows = numbers.floats(200)
        print("entries=%d total=%d" % (len(rows), rows[0][1] if rows else 0))
    elif args.sample == "cap":
        numbers = Numbers(merge_ms=1, max_numbers=2)
        for index in range(3):
            numbers.hit("mob-%d" % index, 10, index * 1000)
        print("entries=%d" % len(numbers.floats(3000)))
    elif args.sample == "ttl":
        numbers = Numbers(merge_ms=100, max_numbers=8)
        numbers.hit("mob", 10, 0)
        print("entries=%d" % len(numbers.floats(1000)))
    elif args.sample == "order":
        numbers = Numbers(merge_ms=1, max_numbers=8)
        numbers.hit("zebra", 10, 0)
        numbers.hit("alpha", 10, 1000)
        print("first=%s" % numbers.floats(2000)[0][0])
    elif args.sample == "scan":
        numbers = Numbers(merge_ms=1, max_numbers=10000)
        for index in range(3000):
            numbers.hit("mob-%d" % index, 10, index * 1000)
        for index in range(3000):
            numbers.floats(index * 1000)
        print("scanned=%d" % numbers.scanned_count())
    else:
        raise SystemExit("需要 --sample merge|cap|ttl|order|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
