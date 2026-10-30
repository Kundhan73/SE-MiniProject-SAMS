"""Protect monitoring evidence from false uptime and accidental history loss."""

import io
import json

import pytest

from scripts import monitor_uptime as monitor


@pytest.mark.parametrize(
    "records",
    [[], [{"in_working_hours": False, "in_maintenance": False, "is_up": False}]],
)
def test_no_working_hour_observations_cannot_pass_sla(records):
    summary = monitor.calculate_uptime_summary(records)
    assert summary["measured_uptime_percent"] is None
    assert summary["sla_met"] is None


class HealthResponse(io.BytesIO):
    status = 200

    def __init__(self, body, url):
        super().__init__(body)
        self.url = url

    def geturl(self):
        return self.url


@pytest.mark.parametrize(
    "body,url,expected",
    [
        (b'{"status":"ok"}', monitor.DEFAULT_ENDPOINT, True),
        (b'{"status":"unavailable"}', monitor.DEFAULT_ENDPOINT, False),
        (b"<html>Sign in</html>", monitor.DEFAULT_ENDPOINT, False),
        (b'{"status":"ok"}', "http://127.0.0.1:8000/login/", False),
    ],
)
def test_probe_checks_health_contract_and_final_url(monkeypatch, body, url, expected):
    monkeypatch.setattr(
        monitor.urllib.request, "urlopen", lambda *a, **k: HealthResponse(body, url)
    )
    assert monitor.probe_health()["is_up"] is expected


def test_corrupt_monitoring_history_is_not_overwritten(tmp_path):
    path = tmp_path / "probes.json"
    original = b'[{"is_up": false},'
    path.write_bytes(original)
    with pytest.raises(ValueError):
        monitor.record_probe({"is_up": True}, path)
    assert path.read_bytes() == original


def test_daemon_records_repeated_probes_and_stops_cleanly(monkeypatch, tmp_path):
    path = tmp_path / "probes.json"
    monkeypatch.setattr(
        "sys.argv", ["monitor", "--daemon", "--interval", "1", "--log-file", str(path)]
    )
    probe = {
        "status_code": 200,
        "is_up": True,
        "latency_ms": 1,
        "in_working_hours": True,
        "in_maintenance": False,
        "error": None,
    }
    monkeypatch.setattr(monitor, "probe_health", lambda endpoint: probe)
    pauses = []

    def pause(seconds):
        pauses.append(seconds)
        if len(pauses) == 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(monitor.time, "sleep", pause)
    monitor.main()
    assert pauses == [1, 1]
    assert len(json.loads(path.read_text())) == 2
