"""Command-line interface for Creator QA."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .episode import parse_episode_json, render_package_markdown_from_file
from .parser import parse_markdown
from .profiles import PROFILES
from .report import render_hermes_report, render_linear_report, render_markdown, render_terminal
from .rules import run_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="creator-qa", description="Local VIDTOOLZ creator packaging verifier.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Run packaging gate on a Markdown package.")
    check.add_argument("input", help="Path to INPUT.md")
    check.add_argument("--profile", choices=sorted(PROFILES), help="QA profile to use for this package.")
    check.add_argument("--json", action="store_true", help="Print JSON output.")
    check.add_argument("--report", help="Write a Markdown report to this path.")
    check.add_argument("--hermes-report", action="store_true", help="Print a compact Markdown report for Hermes memory.")
    check.add_argument("--linear-report", action="store_true", help="Print a Markdown issue/comment body for Linear.")

    check_episode = subparsers.add_parser("check-episode-json", help="Run packaging gate on an Episode Factory JSON export.")
    check_episode.add_argument("input", help="Path to INPUT.json")
    check_episode.add_argument("--profile", choices=sorted(PROFILES), help="QA profile to use for this package.")
    check_episode.add_argument("--json", action="store_true", help="Print JSON output.")
    check_episode.add_argument("--report", help="Write a Markdown report to this path.")
    check_episode.add_argument("--hermes-report", action="store_true", help="Print a compact Markdown report for Hermes memory.")
    check_episode.add_argument("--linear-report", action="store_true", help="Print a Markdown issue/comment body for Linear.")

    render_package = subparsers.add_parser("render-package", help="Render an Episode Factory JSON export as a Creator QA Markdown package.")
    render_package.add_argument("input", help="Path to INPUT.json")
    render_package.add_argument("--output", required=True, help="Path to write rendered Markdown package.")
    return parser


def print_result(args: argparse.Namespace, package) -> int:
    result = run_checks(package, args.profile)

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


def run_check(args: argparse.Namespace) -> int:
    return print_result(args, parse_markdown(args.input))


def run_check_episode_json(args: argparse.Namespace) -> int:
    return print_result(args, parse_episode_json(args.input))


def run_render_package(args: argparse.Namespace) -> int:
    output = Path(args.output)
    output.write_text(render_package_markdown_from_file(args.input), encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return run_check(args)
    if args.command == "check-episode-json":
        return run_check_episode_json(args)
    if args.command == "render-package":
        return run_render_package(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
