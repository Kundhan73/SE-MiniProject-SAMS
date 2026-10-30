"""Regressions found during the independent local validation on 29 October."""

import json
from functools import partial

import pytest
from reportlab.pdfgen import canvas

from reports.services import export_report
from scripts import test_reports


@pytest.mark.parametrize("percentage,expected", [(None, b"No classes"), (100.0, b"100.0%")])
def test_pdf_missing_percentage_is_not_formatted_as_a_percent(monkeypatch, percentage, expected):
    # Keep the actual PDF content stream readable so this checks exported text,
    # including the numeric percentage that must retain its percent sign.
    monkeypatch.setattr(canvas, "Canvas", partial(canvas.Canvas, pageCompression=0))
    row = {
        "srn": "STU001",
        "course": "QA1029",
        "section": "QA",
        "held": 0,
        "attended": 0,
        "percentage": percentage,
    }
    response = export_report([row], "pdf")
    assert response.content.startswith(b"%PDF")
    assert expected in response.content
    assert b"No classes%" not in response.content


def test_system_report_labels_separately_supplied_evidence(monkeypatch, tmp_path):
    monkeypatch.setattr(test_reports, "OUT", tmp_path)
    (tmp_path / "junit.xml").write_text(
        '<testsuites><testsuite><testcase name="local_case"/></testsuite></testsuites>'
    )
    (tmp_path / "coverage.xml").write_text(
        '<coverage lines-valid="1" lines-covered="1" branches-valid="1" branches-covered="1"/>'
    )
    (tmp_path / "browser-results.json").write_text(
        json.dumps({"checks": ["Historical browser case"], "javascript_errors": [], "passed": True})
    )
    (tmp_path / "performance.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-10-28T10:00:00+00:00",
                "dataset_students": 2000,
                "dataset_faculty": 100,
                "concurrent_users": 20,
                "requests": 393,
                "failures": 0,
                "p95_ms": 1400.0,
            }
        )
    )
    test_reports.main()
    report = (tmp_path / "System_Validation_Report.md").read_text()
    assert "not rerun by this report command" in report
    assert "Browser execution timestamp: unavailable" in report
    assert "2026-10-28T10:00:00+00:00" in report
    assert "Source commit: unavailable" in report


def test_session_jwt_spec_security_definition():
    from core.schema import SessionJWTSpec

    spec = SessionJWTSpec(None)
    assert spec.get_security_definition(None) == {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }


@pytest.mark.django_db
def test_admin_user_query_filter_and_corrections_unfiltered(client, world):
    from accounts.models import User

    admin = User.objects.create_user(username="qa_admin", role="ADMIN")
    client.force_authenticate(admin)

    # Search with matching q filter
    res = client.get("/api/admin/users/?q=qa_admin")
    assert res.status_code == 200
    assert any(u["institute_id"] == "qa_admin" for u in res.data)

    # Search with non-matching q filter
    res_empty = client.get("/api/admin/users/?q=nonexistent_xyz")
    assert res_empty.status_code == 200
    assert len(res_empty.data) == 0

    # Admin access to corrections without role filtering
    res_corr = client.get("/api/corrections/")
    assert res_corr.status_code == 200


def test_signout_without_active_session_redirects(client):
    res = client.post("/logout/")
    assert res.status_code == 302
    assert res.url == "/login/"


def test_uptime_working_hours_and_maintenance_window():
    from datetime import datetime
    from scripts.monitor_uptime import is_working_hours, is_maintenance_window, IST

    # Monday 10:00 AM IST -> working hours, not maintenance
    mon_10am = datetime(2026, 11, 2, 10, 0, tzinfo=IST)
    assert is_working_hours(mon_10am) is True
    assert is_maintenance_window(mon_10am) is False

    # Monday 07:30 AM IST -> outside working hours
    mon_7am = datetime(2026, 11, 2, 7, 30, tzinfo=IST)
    assert is_working_hours(mon_7am) is False

    # Saturday 5:30 PM IST -> working hours
    sat_evening = datetime(2026, 11, 7, 17, 30, tzinfo=IST)
    assert is_working_hours(sat_evening) is True

    # Sunday 03:00 AM IST -> maintenance window
    sun_maint = datetime(2026, 11, 8, 3, 0, tzinfo=IST)
    assert is_working_hours(sun_maint) is False
    assert is_maintenance_window(sun_maint) is True


def test_uptime_summary_calculation_and_recording(tmp_path):
    from scripts.monitor_uptime import calculate_uptime_summary, record_probe

    sample_records = [
        {"in_working_hours": True, "in_maintenance": False, "is_up": True, "latency_ms": 42.0},
        {"in_working_hours": True, "in_maintenance": False, "is_up": True, "latency_ms": 58.0},
        {"in_working_hours": True, "in_maintenance": False, "is_up": False, "latency_ms": 100.0},
        {"in_working_hours": False, "in_maintenance": True, "is_up": False, "latency_ms": 0.0},
    ]
    summary = calculate_uptime_summary(sample_records)
    assert summary["total_probes"] == 4
    assert summary["working_hour_probes"] == 3
    assert summary["working_hour_up"] == 2
    assert summary["working_hour_down"] == 1
    assert summary["measured_uptime_percent"] == 66.67
    assert summary["sla_met"] is False

    # Test record_probe
    log_file = tmp_path / "test_uptime.json"
    record_probe(sample_records[0], log_file)
    assert log_file.exists()


@pytest.mark.django_db
def test_swagger_initialization_is_served_as_an_external_script(client):
    response = client.get("/api/docs/?script=")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/javascript")


def test_swagger_resources_are_local_and_do_not_require_inline_style(client):
    response = client.get("/api/docs/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "/static/drf_spectacular_sidecar/swagger-ui-dist/swagger-ui-bundle.js" in html
    assert '<script src="/api/docs/?script="></script>' in html
    assert "<style>" not in html
    assert "cdn.jsdelivr.net" not in html
