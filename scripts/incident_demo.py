"""
Automated Incident Response Demo
=================================
Runs a full incident lifecycle:
  Phase 1 – Baseline traffic (normal)
  Phase 2 – Inject incident
  Phase 3 – Traffic under incident
  Phase 4 – Disable incident
  Phase 5 – Recovery traffic
  Phase 6 – Print comparison table (Baseline vs Incident vs Recovery)

Usage:
  python scripts/incident_demo.py --scenario rag_slow
  python scripts/incident_demo.py --scenario cost_spike --rounds 2
  python scripts/incident_demo.py --scenario tool_fail
  python scripts/incident_demo.py --all
"""
from __future__ import annotations

import argparse
import sys
import time

import httpx

from load_test import run_load_test

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
SCENARIOS = ["rag_slow", "tool_fail", "cost_spike"]

SCENARIO_DESCRIPTIONS = {
    "rag_slow": "RAG retrieval latency spike (~2.5s added per request)",
    "tool_fail": "Vector store timeout (all RAG calls throw RuntimeError)",
    "cost_spike": "Token usage spike (output tokens x4)",
}


def toggle_incident(base_url: str, scenario: str, enable: bool) -> None:
    action = "enable" if enable else "disable"
    with httpx.Client(timeout=10.0) as client:
        r = client.post(f"{base_url}/incidents/{scenario}/{action}")
        r.raise_for_status()


def disable_all(base_url: str) -> None:
    for scenario in SCENARIOS:
        try:
            toggle_incident(base_url, scenario, enable=False)
        except Exception:
            pass


def print_comparison(scenario: str, baseline: dict, incident: dict, recovery: dict | None) -> None:
    print(f"\n{'=' * 72}")
    print(f"  INCIDENT ANALYSIS: {scenario}")
    print(f"  {SCENARIO_DESCRIPTIONS.get(scenario, '')}")
    print(f"{'=' * 72}")

    headers = ["Metric", "Baseline", "Incident", "Delta"]
    if recovery:
        headers.append("Recovery")

    col_w = 14
    header_line = f"  {'Metric':<22} {'Baseline':>{col_w}} {'Incident':>{col_w}} {'Delta':>{col_w}}"
    if recovery:
        header_line += f" {'Recovery':>{col_w}}"
    print(header_line)
    print(f"  {'-' * 22} {'-' * col_w} {'-' * col_w} {'-' * col_w}", end="")
    if recovery:
        print(f" {'-' * col_w}", end="")
    print()

    rows = [
        ("Requests", "total", "", False),
        ("Successes", "successes", "", False),
        ("Failures", "failures", "", False),
        ("Error rate", "error_rate_pct", "%", False),
        ("Latency avg", "latency_avg_ms", "ms", True),
        ("Latency P50", "latency_p50_ms", "ms", True),
        ("Latency P95", "latency_p95_ms", "ms", True),
        ("Latency P99", "latency_p99_ms", "ms", True),
        ("Total cost", "total_cost_usd", "$", True),
        ("Tokens in", "tokens_in", "", False),
        ("Tokens out", "tokens_out", "", False),
    ]

    for label, key, unit, show_delta_pct in rows:
        b_val = baseline.get(key, 0)
        i_val = incident.get(key, 0)

        if unit == "$":
            b_str = f"${b_val:.6f}"
            i_str = f"${i_val:.6f}"
        elif unit == "%":
            b_str = f"{b_val}%"
            i_str = f"{i_val}%"
        elif unit == "ms":
            b_str = f"{b_val}ms"
            i_str = f"{i_val}ms"
        else:
            b_str = str(b_val)
            i_str = str(i_val)

        if show_delta_pct and b_val > 0:
            delta_pct = round(((i_val - b_val) / b_val) * 100, 1)
            sign = "+" if delta_pct >= 0 else ""
            delta_str = f"{sign}{delta_pct}%"
        else:
            diff = i_val - b_val
            if isinstance(diff, float):
                delta_str = f"{diff:+.4f}"
            else:
                delta_str = f"{diff:+d}" if isinstance(diff, int) else str(diff)

        line = f"  {label:<22} {b_str:>{col_w}} {i_str:>{col_w}} {delta_str:>{col_w}}"

        if recovery:
            r_val = recovery.get(key, 0)
            if unit == "$":
                r_str = f"${r_val:.6f}"
            elif unit == "%":
                r_str = f"{r_val}%"
            elif unit == "ms":
                r_str = f"{r_val}ms"
            else:
                r_str = str(r_val)
            line += f" {r_str:>{col_w}}"

        print(line)

    print(f"{'=' * 72}")

    print(f"\n  Root Cause Hints for '{scenario}':")
    if scenario == "rag_slow":
        print("    - Latency P95/P99 should spike significantly (2500ms+ added)")
        print("    - Look at trace waterfall: 'rag_retrieval' span dominates total time")
        print("    - Logs show normal completion but with high latency_ms values")
    elif scenario == "tool_fail":
        print("    - Error rate should jump to ~100% (all requests fail)")
        print("    - Logs show error_type='RuntimeError', detail='Vector store timeout'")
        print("    - Traces show failed 'rag_retrieval' span with exception")
    elif scenario == "cost_spike":
        print("    - Cost per request increases ~4x (output tokens multiplied)")
        print("    - tokens_out increases dramatically while tokens_in stays stable")
        print("    - Traces show 'llm_generation' span with inflated token usage")
    print()


def run_scenario(base_url: str, scenario: str, rounds: int, concurrency: int) -> None:
    print(f"\n{'#' * 72}")
    print(f"  SCENARIO: {scenario}")
    print(f"  Description: {SCENARIO_DESCRIPTIONS.get(scenario, 'Unknown')}")
    print(f"{'#' * 72}")

    # Phase 1 -- Baseline
    print("\n>> Phase 1: Baseline traffic (no incidents)")
    disable_all(base_url)
    time.sleep(0.5)
    baseline_report = run_load_test(
        base_url=base_url,
        rounds=rounds,
        concurrency=concurrency,
        label=f"Baseline ({scenario})",
    )

    # Phase 2 -- Inject
    print(f"\n>> Phase 2: Injecting incident '{scenario}'...")
    toggle_incident(base_url, scenario, enable=True)
    time.sleep(0.5)
    print(f"   Incident '{scenario}' is now ACTIVE")

    # Phase 3 -- Traffic under incident
    print(f"\n>> Phase 3: Traffic under incident '{scenario}'")
    incident_report = run_load_test(
        base_url=base_url,
        rounds=rounds,
        concurrency=concurrency,
        label=f"Under Incident ({scenario})",
    )

    # Phase 4 -- Disable
    print(f"\n>> Phase 4: Disabling incident '{scenario}'...")
    toggle_incident(base_url, scenario, enable=False)
    time.sleep(0.5)
    print(f"   Incident '{scenario}' is now DISABLED")

    # Phase 5 -- Recovery
    print("\n>> Phase 5: Recovery traffic (post-incident)")
    recovery_report = run_load_test(
        base_url=base_url,
        rounds=rounds,
        concurrency=concurrency,
        label=f"Recovery ({scenario})",
    )

    # Phase 6 -- Comparison
    print_comparison(
        scenario=scenario,
        baseline=baseline_report.to_dict(),
        incident=incident_report.to_dict(),
        recovery=recovery_report.to_dict(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automated incident response demo for Day 13 Lab",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/incident_demo.py --scenario rag_slow
  python scripts/incident_demo.py --scenario cost_spike --rounds 2
  python scripts/incident_demo.py --all
        """,
    )
    parser.add_argument("--scenario", choices=SCENARIOS, help="Incident to simulate")
    parser.add_argument("--all", action="store_true", help="Run all scenarios sequentially")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of the app")
    parser.add_argument("--rounds", type=int, default=1, help="Rounds per phase")
    parser.add_argument("--concurrency", type=int, default=1, help="Concurrent requests")
    args = parser.parse_args()

    if not args.scenario and not args.all:
        parser.error("Specify --scenario or --all")

    scenarios = SCENARIOS if args.all else [args.scenario]

    # Verify connectivity
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(f"{args.base_url}/health")
            r.raise_for_status()
            print(f"Connected to {args.base_url} -- app is healthy")
    except Exception as e:
        print(f"Cannot connect to {args.base_url}: {e}")
        print("Make sure the app is running: uvicorn app.main:app --port 8000")
        sys.exit(1)

    disable_all(args.base_url)

    for scenario in scenarios:
        run_scenario(
            base_url=args.base_url,
            scenario=scenario,
            rounds=args.rounds,
            concurrency=args.concurrency,
        )

    disable_all(args.base_url)
    print("\nAll incidents disabled. Demo complete.")


if __name__ == "__main__":
    main()
