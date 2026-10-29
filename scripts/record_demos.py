"""Record actual current-build demos, with synthetic data, in Chromium.

Use an isolated newly seeded server at SAMS_URL; output is retrospective,
not historical evidence of the original sprint date. Playback is silent.
"""

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from browser_smoke import sign_in, nav

OUT = Path("docs/demos")
OUT.mkdir(parents=True, exist_ok=True)


def record(browser, name, duration, flow):
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        record_video_dir=str(OUT / "raw"),
        record_video_size={"width": 1280, "height": 800},
    )
    page = context.new_page()
    start = time.monotonic()
    flow(page)
    remaining = duration - (time.monotonic() - start)
    if remaining > 0:
        page.wait_for_timeout(remaining * 1000)
    video = page.video
    context.close()
    video.save_as(str(OUT / name))
    video.delete()
    print(f"Recorded {name}: {time.monotonic() - start:.1f}s", flush=True)


def first(page):
    sign_in(page, "ADM001")
    page.wait_for_timeout(8000)
    nav(page, "Academic setup")
    page.wait_for_timeout(9000)
    page.locator("#content").get_by_role(
        "heading", name="Weekly timetable"
    ).scroll_into_view_if_needed()
    page.wait_for_timeout(5000)
    nav(page, "People")
    page.wait_for_timeout(7000)
    page.locator(".sidebar").get_by_role("button", name="Sign out", exact=False).click()
    sign_in(page, "STU001")
    page.wait_for_timeout(8000)
    nav(page, "Notifications")
    page.wait_for_timeout(3000)
    nav(page, "Overview")


def second(page):
    sign_in(page, "FAC001")
    page.wait_for_timeout(6000)
    nav(page, "Take attendance")
    page.wait_for_timeout(6000)
    form = (
        page.locator(".mark-form")
        .filter(has=page.get_by_role("button", name="Submit attendance", exact=True))
        .first
    )
    form.locator("select").nth(0).select_option("A")
    form.locator("select").nth(1).select_option("OD")
    page.wait_for_timeout(4000)
    form.get_by_role("button", name="Submit attendance", exact=True).click()
    expect(page.locator("#notice")).to_have_text("Saved successfully.")
    page.wait_for_timeout(5000)
    page.locator(".sidebar").get_by_role("button", name="Sign out", exact=False).click()
    sign_in(page, "STU001")
    page.wait_for_timeout(7000)
    nav(page, "Corrections")
    page.wait_for_timeout(4000)
    page.locator("#correction-form #requested_status").select_option("OD")
    page.locator("#correction-form #reason").fill(
        "University event participation verified by faculty"
    )
    page.wait_for_timeout(4000)
    page.locator("#correction-form").get_by_role("button", name="Send to faculty").click()
    expect(page.locator("#notice")).to_have_text("Saved successfully.")
    page.wait_for_timeout(4000)
    page.locator(".sidebar").get_by_role("button", name="Sign out", exact=False).click()
    sign_in(page, "FAC001")
    nav(page, "Corrections")
    page.wait_for_timeout(5000)
    decision = page.locator(".decision-form").first
    decision.locator("input").fill("Approved after checking the event register")
    decision.get_by_role("button", name="Approve", exact=True).click()
    expect(page.locator("#notice")).to_have_text("Saved successfully.")
    page.wait_for_timeout(4000)
    nav(page, "Reports")
    page.wait_for_timeout(7000)
    page.locator("#kind").select_option("defaulters")
    page.locator("#report-filter").get_by_role("button", name="Apply filters").click()
    page.wait_for_timeout(5000)
    with page.expect_download() as download:
        page.get_by_role("link", name="Download PDF", exact=False).click()
    assert download.value.suggested_filename.endswith(".pdf")
    page.wait_for_timeout(3000)
    page.locator(".sidebar").get_by_role("button", name="Sign out", exact=False).click()
    sign_in(page, "ADM001")
    nav(page, "Audit trail")
    page.wait_for_timeout(7000)
    assert "Correction approved" in page.locator("#content").inner_text()


if __name__ == "__main__":
    assert os.getenv("SAMS_URL"), "Set SAMS_URL to an isolated newly seeded demo server."
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chromium")
        record(browser, "sprint-1-retrospective.webm", 60, first)
        record(browser, "sprint-2-demo.webm", 120, second)
        browser.close()
