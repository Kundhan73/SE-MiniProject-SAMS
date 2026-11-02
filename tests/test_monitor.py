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


def test_probe_health_http_error(monkeypatch):
    def fake_urlopen(*args, **kwargs):
        raise monitor.urllib.error.HTTPError(
            url=monitor.DEFAULT_ENDPOINT,
            code=503,
            msg="Service Unavailable",
            hdrs={},
            fp=io.BytesIO(b'{"status":"unavailable"}'),
        )

    monkeypatch.setattr(monitor.urllib.request, "urlopen", fake_urlopen)
    res = monitor.probe_health()
    assert res["status_code"] == 503
    assert res["is_up"] is False
    assert "HTTPError 503" in res["error"]


def test_probe_health_network_failure(monkeypatch):
    def fake_urlopen(*args, **kwargs):
        raise monitor.urllib.error.URLError("Connection refused")

    monkeypatch.setattr(monitor.urllib.request, "urlopen", fake_urlopen)
    res = monitor.probe_health()
    assert res["status_code"] == 0
    assert res["is_up"] is False
    assert "URLError" in res["error"]


def test_record_probe_rejects_non_list_json(tmp_path):
    path = tmp_path / "non_list.json"
    path.write_text('{"key": "value"}', encoding="utf-8")
    with pytest.raises(ValueError, match="must be a JSON list"):
        monitor.record_probe({"is_up": True}, path)


def test_monitor_cli_summary_mode(monkeypatch, tmp_path, capsys):
    path = tmp_path / "probes.json"
    path.write_text(
        json.dumps(
            [{"in_working_hours": True, "in_maintenance": False, "is_up": True, "latency_ms": 15.0}]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("sys.argv", ["monitor", "--summary", "--log-file", str(path)])
    monitor.main()
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["total_probes"] == 1
    assert data["working_hour_up"] == 1
    assert data["measured_uptime_percent"] == 100.0


def test_monitor_cli_summary_missing_file(monkeypatch, tmp_path):
    path = tmp_path / "absent.json"
    monkeypatch.setattr("sys.argv", ["monitor", "--summary", "--log-file", str(path)])
    with pytest.raises(SystemExit) as excinfo:
        monitor.main()
    assert excinfo.value.code == 1


def test_monitor_cli_check_once_and_record(monkeypatch, tmp_path, capsys):
    path = tmp_path / "record_once.json"
    monkeypatch.setattr(
        "sys.argv",
        ["monitor", "--check-once", "--record", "--log-file", str(path)],
    )
    probe = {
        "status_code": 200,
        "is_up": False,
        "latency_ms": 12.5,
        "in_working_hours": True,
        "in_maintenance": False,
        "error": "Unexpected health response",
    }
    monkeypatch.setattr(monitor, "probe_health", lambda endpoint: probe)
    monitor.main()
    out = capsys.readouterr().out
    assert "Probe Result: [200] DOWN" in out
    assert "Error: Unexpected health response" in out
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert len(saved) == 1
    assert saved[0]["status_code"] == 200


def test_monitor_cli_invalid_interval(monkeypatch):
    monkeypatch.setattr("sys.argv", ["monitor", "--interval", "-10"])
    with pytest.raises(SystemExit):
        monitor.main()


def test_sunday_outside_maintenance_window():
    from datetime import datetime

    sun_afternoon = datetime(2026, 11, 8, 14, 0, tzinfo=monitor.IST)
    assert monitor.is_working_hours(sun_afternoon) is False
    assert monitor.is_maintenance_window(sun_afternoon) is False
