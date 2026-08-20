"""Reproductible concurrent load probe for the SkillTrack dashboard.

The script uses only Python's standard library so a jury can run it from a
fresh checkout once Docker Compose is healthy.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import math
import os
from pathlib import Path
import platform
import statistics
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Sample:
    status: int
    duration_ms: float
    error: str | None = None


def percentile(values: list[float], percent: float) -> float:
    """Return the nearest-rank percentile for an already collected sample."""

    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(percent / 100 * len(ordered)) - 1)
    return round(ordered[index], 2)


def request_json(url: str, *, token: str | None = None, body: dict | None = None) -> tuple[int, object]:
    payload = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, data=payload, headers=headers, method="POST" if payload is not None else "GET")
    with urlopen(request, timeout=15) as response:
        return response.status, json.loads(response.read())


def measure(url: str, token: str) -> Sample:
    started = time.perf_counter()
    try:
        status, _ = request_json(url, token=token)
        return Sample(status=status, duration_ms=round((time.perf_counter() - started) * 1000, 2))
    except HTTPError as exc:
        return Sample(
            status=exc.code,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            error=f"HTTP {exc.code}",
        )
    except (URLError, TimeoutError, OSError) as exc:
        return Sample(
            status=0,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            error=type(exc).__name__,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure SkillTrack under concurrent read load.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--users", type=int, default=20, help="Concurrent workers (default: 20)")
    parser.add_argument("--requests", type=int, default=200, help="Measured requests (default: 200)")
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--max-p95-ms", type=float, default=1000)
    parser.add_argument("--min-success-rate", type=float, default=99)
    parser.add_argument("--email", default="demo@skilltrack.dev")
    parser.add_argument("--password", default="DemoPassword123!")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.users < 1 or args.requests < 1 or args.warmup < 0:
        raise SystemExit("users/requests must be positive and warmup cannot be negative")

    login_status, login = request_json(
        f"{args.base_url.rstrip('/')}/auth/login",
        body={"email": args.email, "password": args.password},
    )
    if login_status != 200 or not isinstance(login, dict) or "access_token" not in login:
        raise SystemExit("Authentication failed; start the stack and verify the demo account.")

    token = str(login["access_token"])
    endpoint = f"{args.base_url.rstrip('/')}/dashboard"
    for _ in range(args.warmup):
        measure(endpoint, token)

    started = time.perf_counter()
    samples: list[Sample] = []
    with ThreadPoolExecutor(max_workers=args.users) as pool:
        futures = [pool.submit(measure, endpoint, token) for _ in range(args.requests)]
        for future in as_completed(futures):
            samples.append(future.result())
    elapsed = time.perf_counter() - started

    successes = [sample for sample in samples if sample.status == 200]
    durations = [sample.duration_ms for sample in successes]
    success_rate = round(len(successes) / len(samples) * 100, 2)
    p95 = percentile(durations, 95)
    passed = success_rate >= args.min_success_rate and p95 <= args.max_p95_ms
    result = {
        "schema_version": "1.0",
        "measured_at_utc": datetime.now(UTC).isoformat(),
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "logical_cpu_count": os.cpu_count(),
            "base_url": args.base_url,
            "endpoint": "/dashboard",
        },
        "scenario": {
            "concurrent_users": args.users,
            "requests": args.requests,
            "warmup_requests": args.warmup,
            "read_only": True,
        },
        "thresholds": {
            "minimum_success_rate_percent": args.min_success_rate,
            "maximum_p95_ms": args.max_p95_ms,
        },
        "results": {
            "passed": passed,
            "successes": len(successes),
            "failures": len(samples) - len(successes),
            "success_rate_percent": success_rate,
            "elapsed_seconds": round(elapsed, 3),
            "throughput_requests_per_second": round(len(samples) / elapsed, 2),
            "latency_ms": {
                "minimum": round(min(durations), 2) if durations else 0,
                "mean": round(statistics.fmean(durations), 2) if durations else 0,
                "median": round(statistics.median(durations), 2) if durations else 0,
                "p95": p95,
                "p99": percentile(durations, 99),
                "maximum": round(max(durations), 2) if durations else 0,
            },
            "errors": [asdict(sample) for sample in samples if sample.error],
        },
    }

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
