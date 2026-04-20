from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")


@dataclass
class RequestResult:
    status_code: int
    latency_ms: float
    correlation_id: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    error: str | None = None


@dataclass
class LoadTestReport:
    results: list[RequestResult] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def successes(self) -> int:
        return sum(1 for r in self.results if r.status_code == 200)

    @property
    def failures(self) -> int:
        return self.total - self.successes

    @property
    def error_rate_pct(self) -> float:
        return round((self.failures / self.total) * 100, 2) if self.total else 0.0

    @property
    def latencies(self) -> list[float]:
        return [r.latency_ms for r in self.results if r.status_code == 200]

    @property
    def total_cost(self) -> float:
        return round(sum(r.cost_usd for r in self.results), 6)

    @property
    def total_tokens_in(self) -> int:
        return sum(r.tokens_in for r in self.results)

    @property
    def total_tokens_out(self) -> int:
        return sum(r.tokens_out for r in self.results)

    @property
    def duration_sec(self) -> float:
        return round(self.end_time - self.start_time, 2) if self.end_time else 0.0

    def percentile(self, p: int) -> float:
        vals = sorted(self.latencies)
        if not vals:
            return 0.0
        idx = max(0, min(len(vals) - 1, round((p / 100) * len(vals) + 0.5) - 1))
        return round(vals[idx], 1)

    def print_summary(self, label: str = "Load Test") -> None:
        print(f"\n{'=' * 60}")
        print(f"  {label} Summary")
        print(f"{'=' * 60}")
        print(f"  Duration       : {self.duration_sec}s")
        print(f"  Total requests : {self.total}")
        print(f"  Successes      : {self.successes}")
        print(f"  Failures       : {self.failures}")
        print(f"  Error rate     : {self.error_rate_pct}%")
        print("  ---")
        print(f"  Latency avg    : {round(mean(self.latencies), 1) if self.latencies else 0}ms")
        print(f"  Latency P50    : {self.percentile(50)}ms")
        print(f"  Latency P95    : {self.percentile(95)}ms")
        print(f"  Latency P99    : {self.percentile(99)}ms")
        print("  ---")
        print(f"  Total cost     : ${self.total_cost}")
        print(f"  Avg cost/req   : ${round(self.total_cost / self.total, 6) if self.total else 0}")
        print(f"  Tokens in      : {self.total_tokens_in}")
        print(f"  Tokens out     : {self.total_tokens_out}")
        print(f"{'=' * 60}")

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "successes": self.successes,
            "failures": self.failures,
            "error_rate_pct": self.error_rate_pct,
            "latency_avg_ms": round(mean(self.latencies), 1) if self.latencies else 0,
            "latency_p50_ms": self.percentile(50),
            "latency_p95_ms": self.percentile(95),
            "latency_p99_ms": self.percentile(99),
            "total_cost_usd": self.total_cost,
            "tokens_in": self.total_tokens_in,
            "tokens_out": self.total_tokens_out,
            "duration_sec": self.duration_sec,
        }


def send_request(client: httpx.Client, base_url: str, payload: dict) -> RequestResult:
    try:
        start = time.perf_counter()
        r = client.post(f"{base_url}/chat", json=payload)
        latency = (time.perf_counter() - start) * 1000
        body = r.json()
        result = RequestResult(
            status_code=r.status_code,
            latency_ms=round(latency, 1),
            correlation_id=body.get("correlation_id", ""),
            tokens_in=body.get("tokens_in", 0),
            tokens_out=body.get("tokens_out", 0),
            cost_usd=body.get("cost_usd", 0.0),
        )
        status_icon = "OK" if r.status_code == 200 else "ERR"
        print(
            f"  [{status_icon}] {result.correlation_id} | "
            f"{payload.get('feature', '?'):>7} | "
            f"{result.latency_ms:>7.1f}ms | "
            f"${result.cost_usd:.6f}"
        )
        return result
    except Exception as e:
        print(f"  [FAIL] {e}")
        return RequestResult(status_code=0, latency_ms=0, correlation_id="", error=str(e))


def run_load_test(
    base_url: str,
    rounds: int = 1,
    concurrency: int = 1,
    delay: float = 0.0,
    label: str = "Load Test",
) -> LoadTestReport:
    if not QUERIES.exists():
        print(f"Error: {QUERIES} not found.")
        sys.exit(1)

    lines = [line for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]
    payloads = [json.loads(line) for line in lines]

    all_payloads = payloads * rounds
    report = LoadTestReport()

    print(f"\n>> {label}: {len(all_payloads)} requests ({len(payloads)} queries x {rounds} rounds), concurrency={concurrency}")
    print("-" * 60)

    report.start_time = time.perf_counter()

    with httpx.Client(timeout=30.0) as client:
        if concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = []
                for payload in all_payloads:
                    futures.append(executor.submit(send_request, client, base_url, payload))
                    if delay > 0:
                        time.sleep(delay)
                for future in concurrent.futures.as_completed(futures):
                    report.results.append(future.result())
        else:
            for payload in all_payloads:
                result = send_request(client, base_url, payload)
                report.results.append(result)
                if delay > 0:
                    time.sleep(delay)

    report.end_time = time.perf_counter()
    report.print_summary(label)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Load test for Day 13 Observability Lab")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of the app")
    parser.add_argument("--rounds", type=int, default=1, help="Number of times to repeat all queries")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between requests in seconds")
    args = parser.parse_args()

    run_load_test(
        base_url=args.base_url,
        rounds=args.rounds,
        concurrency=args.concurrency,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
