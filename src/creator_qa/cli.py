"""Command-line interface for Creator QA."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import parse_markdown
from .report import render_hermes_report, render_linear_report, render_markdown, render_terminal
from .rules import run_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="creator-qa", description="Local VIDTOOLZ creator packaging verifier.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Run packaging gate on a Markdown package.")
    check.add_argument("input", help="Path to INPUT.md")
    check.add_argument("--json", action="store_true", help="Print JSON output.")
    check.add_argument("--report", help="Write a Markdown report to this path.")
    check.add_argument("--hermes-report", action="store_true", help="Print a compact Markdown report for Hermes memory.")
    check.add_argument("--linear-report", action="store_true", help="Print a Markdown issue/comment body for Linear.")
    return parser


def run_check(args: argparse.Namespace) -> int:
    package = parse_markdown(args.input)
    result = run_checks(package)

    if args.report:
        Path(args.report).write_text(render_markdown(result), encoding="utf-8")

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    elif args.hermes_report:
        print(render_hermes_report(result), end="")
    elif args.linear_report:
        print(render_linear_report(result), end="")
    else:
        print(render_terminal(result))

    return 0 if result.status == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return run_check(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
