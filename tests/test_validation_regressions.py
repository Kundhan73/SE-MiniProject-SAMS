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


@pytest.mark.django_db
def test_swagger_initialization_is_served_as_an_external_script(client):
    response = client.get("/api/docs/?script=")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/javascript")
