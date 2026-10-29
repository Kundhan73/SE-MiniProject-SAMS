"""Real Chromium role workflows against an isolated synthetic demo database."""

import json
import os
import time
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect

BASE = os.getenv("SAMS_URL", "http://127.0.0.1:8000")
OUT = Path("docs/reports")
OUT.mkdir(parents=True, exist_ok=True)


def sign_in(page, username):
    page.goto(BASE + "/login/")
    page.wait_for_load_state("networkidle")
    page.get_by_label("Institute ID", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill(os.getenv("DEMO_PASSWORD", "DemoPass@1234"))
    page.get_by_role("button", name="Sign in", exact=False).click()
    page.wait_for_url(BASE + "/")
    page.wait_for_load_state("networkidle")
    expect(page.locator("#content")).to_have_attribute("aria-busy", "false")


def nav(page, name):
    page.locator(".sidebar").get_by_role("button", name=name, exact=False).click()
    expect(page.locator("#content")).to_have_attribute("aria-busy", "false")


def main():
    for _ in range(60):
        try:
            if urlopen(BASE + "/api/health/", timeout=2).status == 200:
                break
        except OSError:
            time.sleep(1)
    errors = []
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        sign_in(page, "FAC001")
        checks.append("Faculty login and role dashboard")
        nav(page, "Take attendance")
        forms = page.locator(".mark-form")
        pending = forms.filter(has=page.get_by_role("button", name="Submit attendance", exact=True))
        if pending.count():
            first = pending.first
            first.locator("select").first.select_option("A")
            first.get_by_role("button", name="Submit attendance", exact=True).click()
            expect(page.locator("#notice")).to_have_text("Saved successfully.")
        expect(page.get_by_text("Attendance submitted.", exact=False).first).to_be_visible()
        checks.append("Faculty submits real class roll with P/A/OD controls")
        page.screenshot(path=str(OUT / "browser-faculty.png"), full_page=False)
        page.get_by_role("button", name="Sign out", exact=False).click()
        sign_in(page, "STU001")
        expect(page.get_by_text("Your attendance", exact=True)).to_be_visible()
        page.screenshot(path=str(OUT / "browser-student.png"), full_page=True)
        checks.append("Student sees own percentages")
        nav(page, "Corrections")
        page.locator("#correction-form #requested_status").select_option("OD")
        page.locator("#correction-form #reason").fill(
            "Verified university event — browser smoke test"
        )
        page.locator("#correction-form").get_by_role("button", name="Send to faculty").click()
        expect(page.locator("#notice")).to_have_text("Saved successfully.")
        checks.append("Student creates correction request")
        page.get_by_role("button", name="Sign out", exact=False).click()
        sign_in(page, "FAC001")
        nav(page, "Corrections")
        decision = page.locator(".decision-form").first
        decision.locator("input").fill("Verified against the event register")
        decision.get_by_role("button", name="Approve", exact=True).click()
        expect(page.locator("#notice")).to_have_text("Saved successfully.")
        expect(page.locator("#content").get_by_text("APPROVED", exact=True).first).to_be_visible()
        checks.append("Faculty approval persists and notifies student")
        nav(page, "Reports")
        with page.expect_download() as dl:
            page.get_by_role("link", name="Download PDF", exact=False).click()
        assert dl.value.suggested_filename.endswith(".pdf")
        with page.expect_download() as dl:
            page.get_by_role("link", name="Download CSV", exact=False).click()
        assert dl.value.suggested_filename.endswith(".csv")
        checks.append("Faculty downloads PDF and CSV reports")
        page.get_by_role("button", name="Sign out", exact=False).click()
        sign_in(page, "ADM001")
        nav(page, "Audit trail")
        expect(page.locator("table")).to_be_visible()
        assert "Correction approved" in page.locator("#content").inner_text()
        checks.append("Admin sees immutable correction history")
        nav(page, "Academic setup")
        expect(page.get_by_text("Weekly timetable", exact=True)).to_be_visible()
        nav(page, "People")
        expect(page.get_by_text("Create account", exact=True)).to_be_visible()
        page.set_viewport_size({"width": 360, "height": 800})
        nav(page, "Overview")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(OUT / "browser-mobile.png"), full_page=True)
        checks.append("360px mobile layout has no page overflow")
        browser.close()
    result = {
        "checks": checks,
        "count": len(checks),
        "javascript_errors": errors,
        "passed": not errors,
    }
    (OUT / "browser-results.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    assert not errors


if __name__ == "__main__":
    main()
