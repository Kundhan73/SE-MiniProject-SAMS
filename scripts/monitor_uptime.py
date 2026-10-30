"""SAMS Working-Hours Uptime Monitoring Utility (SAMS-NF-002).

Monitors endpoint health, tracks latency and availability during working hours
(8:00 AM - 6:00 PM IST, Monday through Saturday), excluding announced
maintenance windows (Sundays 00:00 - 06:00 IST).

Usage:
    python scripts/monitor_uptime.py --check-once [--host http://127.0.0.1:8000]
    python scripts/monitor_uptime.py --summary [--log-file docs/reports/uptime_probes.json]
    python scripts/monitor_uptime.py --daemon --interval 60 [--log-file docs/reports/uptime_probes.json]
"""

import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.request
import urllib.error

# IST is UTC+05:30
IST = timezone(timedelta(hours=5, minutes=30))
DEFAULT_ENDPOINT = "http://127.0.0.1:8000/api/health/"
DEFAULT_LOG_PATH = Path(__file__).resolve().parents[1] / "docs/reports/uptime_probes.json"
TARGET_SLA_PERCENT = 99.0


def is_working_hours(dt: datetime) -> bool:
    """Check if given datetime in IST falls within working hours.

    Working hours: Monday (0) through Saturday (5), 8:00 AM (08:00) to 6:00 PM (18:00) IST.
    Sundays (6) are outside working hours.
    """
    dt_ist = dt.astimezone(IST)
    weekday = dt_ist.weekday()  # Monday is 0, Sunday is 6
    if weekday == 6:
        return False
    hour = dt_ist.hour
    minute = dt_ist.minute
    total_minutes = hour * 60 + minute
    # 8:00 AM = 480 min, 18:00 (6:00 PM) = 1080 min
    return 480 <= total_minutes < 1080


def is_maintenance_window(dt: datetime) -> bool:
    """Check if given datetime falls into announced maintenance window.

    Announced maintenance: Sundays 00:00 - 06:00 IST.
    """
    dt_ist = dt.astimezone(IST)
    if dt_ist.weekday() == 6 and 0 <= dt_ist.hour < 6:
        return True
    return False


def probe_health(endpoint: str = DEFAULT_ENDPOINT, timeout: float = 3.0) -> dict:
    """Send probe to health endpoint and record latency and status."""
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST)
    start = time.perf_counter()
    status_code = 0
    response_body = ""
    is_up = False
    error_message = None

    try:
        req = urllib.request.Request(
            endpoint,
            headers={"User-Agent": "SAMS-UptimeMonitor/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status_code = resp.status
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            response_body = resp.read().decode("utf-8", errors="replace")
            if resp.geturl().rstrip("/") != endpoint.rstrip("/"):
                error_message = "Health endpoint redirected; use its canonical URL."
            else:
                try:
                    payload = json.loads(response_body)
                except ValueError:
                    payload = None
                is_up = (
                    status_code == 200
                    and isinstance(payload, dict)
                    and payload.get("status") == "ok"
                )
                if not is_up:
                    error_message = "Unexpected health response; expected HTTP 200 with status ok."
    except urllib.error.HTTPError as e:
        status_code = e.code
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response_body = e.read().decode("utf-8", errors="replace")
        error_message = f"HTTPError {e.code}"
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        error_message = f"{type(e).__name__}: {e}"

    in_working_hours = is_working_hours(now_ist)
    in_maintenance = is_maintenance_window(now_ist)

    return {
        "timestamp_utc": now_utc.isoformat(),
        "timestamp_ist": now_ist.isoformat(),
        "endpoint": endpoint,
        "status_code": status_code,
        "latency_ms": elapsed_ms,
        "response": response_body,
        "is_up": is_up,
        "in_working_hours": in_working_hours,
        "in_maintenance": in_maintenance,
        "error": error_message,
    }


def record_probe(probe_data: dict, log_path: Path):
    """Append probe entry to JSON log file."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    records = []
    if log_path.exists():
        records = json.loads(log_path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError("Monitoring history must be a JSON list; original file preserved.")
    records.append(probe_data)
    # One monitor process owns each log. Replace atomically so interruption cannot
    # leave a truncated history that is mistaken for an empty observation period.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=log_path.parent, delete=False
        ) as output:
            temporary = Path(output.name)
            json.dump(records, output, indent=2)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, log_path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def calculate_uptime_summary(records: list) -> dict:
    """Calculate uptime statistics filtering by working hours and excluding maintenance."""
    total_probes = len(records)
    working_hour_probes = [
        r for r in records if r.get("in_working_hours") and not r.get("in_maintenance")
    ]
    up_probes = [r for r in working_hour_probes if r.get("is_up")]
    down_probes = [r for r in working_hour_probes if not r.get("is_up")]

    total_wh = len(working_hour_probes)
    uptime_pct = round((len(up_probes) / total_wh) * 100, 2) if total_wh > 0 else None
    sla_met = uptime_pct >= TARGET_SLA_PERCENT if uptime_pct is not None else None

    latencies = [r["latency_ms"] for r in up_probes if "latency_ms" in r]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

    return {
        "total_probes": total_probes,
        "working_hour_probes": total_wh,
        "working_hour_up": len(up_probes),
        "working_hour_down": len(down_probes),
        "measured_uptime_percent": uptime_pct,
        "target_sla_percent": TARGET_SLA_PERCENT,
        "sla_met": sla_met,
        "average_latency_ms": avg_latency,
        "scope": "Recorded working-hour probes only; unobserved intervals and semester availability are not established.",
    }


def main():
    parser = argparse.ArgumentParser(description="SAMS Uptime Monitor")
    parser.add_argument("--host", default="http://127.0.0.1:8000", help="Base URL of SAMS")
    parser.add_argument("--endpoint", default="/api/health/", help="Health endpoint path")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check-once", action="store_true", help="Perform single probe check")
    mode.add_argument("--summary", action="store_true", help="Print summary from log file")
    mode.add_argument(
        "--daemon", action="store_true", help="Probe repeatedly and record every result"
    )
    parser.add_argument("--interval", type=float, default=60, help="Seconds between daemon probes")
    parser.add_argument(
        "--log-file", type=Path, default=DEFAULT_LOG_PATH, help="Path to JSON probe log"
    )
    parser.add_argument("--record", action="store_true", help="Record probe in log file")
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be positive")

    full_url = args.host.rstrip("/") + "/" + args.endpoint.lstrip("/")

    if args.summary:
        if not args.log_file.exists():
            print(f"Log file not found: {args.log_file}")
            sys.exit(1)
        records = json.loads(args.log_file.read_text(encoding="utf-8"))
        summary = calculate_uptime_summary(records)
        print(json.dumps(summary, indent=2))
        return

    try:
        while True:
            probe = probe_health(full_url)
            print(
                f"Probe Result: [{probe['status_code']}] {'UP' if probe['is_up'] else 'DOWN'} "
                f"({probe['latency_ms']} ms) | Working Hours: {probe['in_working_hours']} | Maintenance: {probe['in_maintenance']}"
            )
            if probe["error"]:
                print(f"Error: {probe['error']}")
            if args.record or args.daemon:
                record_probe(probe, args.log_file)
                print(f"Recorded probe to {args.log_file}")
            if not args.daemon:
                return
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Monitor stopped; recorded history retained.")


if __name__ == "__main__":
    main()
