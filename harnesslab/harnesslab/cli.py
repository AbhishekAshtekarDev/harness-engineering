"""Command line entry point.

    python -m harnesslab demo                       offline scripted run, no API key
    python -m harnesslab run --provider anthropic   real model on ticket HT-142
    python -m harnesslab trace runs/HT-142.jsonl    print a saved trace as a waterfall
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="harnesslab")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="offline scripted run of the habit-tracker harness")
    run = sub.add_parser("run", help="run a real model on ticket HT-142 inside the harness")
    run.add_argument("--provider", choices=["anthropic", "openai"], required=True)
    run.add_argument("--model", default=None, help="model name (or set HARNESSLAB_MODEL)")
    run.add_argument("--trace", default="runs/HT-142.jsonl", help="where to write the trace")
    run.add_argument("--interactive", action="store_true", help="ask you to approve 'ask' actions")
    run.add_argument("--keep", action="store_true", help="keep the workspace and print its path")
    tr = sub.add_parser("trace", help="show a saved trace as a waterfall")
    tr.add_argument("path")
    args = parser.parse_args(argv)

    if args.cmd == "demo":
        from .demo import main as demo_main
        return demo_main()

    if args.cmd == "trace":
        from .trace import load, waterfall
        print(waterfall(load(args.path)))
        return 0

    from .models import load_model
    from .permissions import console_approver, deny_all_approver
    from .presets import build_habit_tracker_harness, ticket

    Path(args.trace).parent.mkdir(parents=True, exist_ok=True)
    Path(args.trace).unlink(missing_ok=True)
    loop, ws = build_habit_tracker_harness(
        load_model(args.provider, args.model), trace_path=args.trace,
        approver=console_approver if args.interactive else deny_all_approver, on_step=print)
    try:
        result = loop.run(ticket(), task_id="HT-142")
        print(f"\nstatus: {result.status} ({result.reason}) after {result.iterations} iterations, "
              f"{result.input_tokens + result.output_tokens:,} tokens")
        print(f"changed: {', '.join(ws.changed_files())}\ntrace: {args.trace}")
        if args.keep:
            print(f"workspace kept at {ws.root}")
        return 0 if result.status == "succeeded" else 1
    finally:
        if not args.keep:
            ws.destroy()


if __name__ == "__main__":
    sys.exit(main())
