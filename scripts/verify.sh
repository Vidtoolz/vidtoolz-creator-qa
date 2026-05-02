#!/usr/bin/env bash
set -euo pipefail

python -m compileall -q src tests
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
PYTHONPATH=src python -m creator_qa.cli check examples/resolve-tutorial-sample.md >/tmp/creator-qa-smoke.txt
PYTHONPATH=src python -m creator_qa.cli check examples/resolve-tutorial-sample.md --json >/tmp/creator-qa-smoke.json
