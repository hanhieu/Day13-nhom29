from __future__ import annotations

import argparse
import sys

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
SCENARIOS = ["rag_slow", "tool_fail", "cost_spike"]


def get_status(client: httpx.Client, base_url: str) -> dict:
    r = client.get(f"{base_url}/health", timeout=10.0)
    r.raise_for_status()
    return r.json().get("incidents", {})


def toggle_incident(client: httpx.Client, base_url: str, scenario: str, disable: bool) -> dict:
    action = "disable" if disable else "enable"
    r = client.post(f"{base_url}/incidents/{scenario}/{action}", timeout=10.0)
    r.raise_for_status()
    return r.json()


def print_status(incidents: dict) -> None:
    print("\n  Incident Status:")
    for name, active in incidents.items():
        icon = "ON " if active else "OFF"
        print(f"    [{icon}] {name}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject or disable incidents for Day 13 Lab")
    parser.add_argument("--scenario", choices=SCENARIOS, help="Incident scenario to toggle")
    parser.add_argument("--disable", action="store_true", help="Disable the scenario (default: enable)")
    parser.add_argument("--all", action="store_true", help="Apply to all scenarios")
    parser.add_argument("--status", action="store_true", help="Show current incident status")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of the app")
    args = parser.parse_args()

    with httpx.Client(timeout=10.0) as client:
        if args.status:
            incidents = get_status(client, args.base_url)
            print_status(incidents)
            return

        if args.all:
            targets = SCENARIOS
        elif args.scenario:
            targets = [args.scenario]
        else:
            parser.error("Specify --scenario, --all, or --status")
            return

        action_label = "Disabling" if args.disable else "Enabling"
        for scenario in targets:
            print(f"  {action_label} '{scenario}'...")
            try:
                result = toggle_incident(client, args.base_url, scenario, args.disable)
                print(f"    -> OK: {result}")
            except httpx.HTTPStatusError as e:
                print(f"    -> FAILED ({e.response.status_code}): {e.response.text}")
                sys.exit(1)
            except httpx.ConnectError:
                print(f"    -> FAILED: Cannot connect to {args.base_url}")
                sys.exit(1)

        incidents = get_status(client, args.base_url)
        print_status(incidents)


if __name__ == "__main__":
    main()
