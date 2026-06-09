from __future__ import annotations

import argparse
import json

from .db import get_db
from .seed import SAMPLE_REVIEW_INPUT
from .workflow import run_local_workflow


def seed_demo() -> None:
    review = get_db().create_review(SAMPLE_REVIEW_INPUT)
    print(review.model_dump_json(indent=2))


def run_local(review_id: str) -> None:
    review = run_local_workflow(review_id)
    print(review.model_dump_json(indent=2))


def reset_db() -> None:
    get_db().reset()
    print(json.dumps({"ok": True}))


def show_review(review_id: str) -> None:
    review = get_db().get_review(review_id)
    events = get_db().list_events(review_id)
    print(json.dumps({"review": review.model_dump(mode="json"), "events": [e.model_dump(mode="json") for e in events]}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="SagadOS Feedback Review CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed-demo")
    run_parser = sub.add_parser("run-local")
    run_parser.add_argument("review_id")
    sub.add_parser("reset-db")
    show_parser = sub.add_parser("show-review")
    show_parser.add_argument("review_id")
    args = parser.parse_args()

    if args.command == "seed-demo":
        seed_demo()
    elif args.command == "run-local":
        run_local(args.review_id)
    elif args.command == "reset-db":
        reset_db()
    elif args.command == "show-review":
        show_review(args.review_id)


if __name__ == "__main__":
    main()
