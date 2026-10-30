# Working-product demonstrations

Recorded on 29 October 2026 using the actual running application and synthetic accounts. These are silent, automated Chromium recordings. No real student data or real credentials are shown.

- [Sprint 1 retrospective](sprint-1-retrospective.webm): approximately one minute showing authentication, role dashboards, setup and users.
- [Sprint 2 demonstration](sprint-2-demo.webm): approximately two minutes showing roll marking, private student view, correction request/approval, reports and audit history.

Sprint 1's original teacher window was 19–23 October. Its recording is retrospective; it does not claim a video or implementation existed during that week. See [demo guide](../DEMO_GUIDE.md) for narration and GitHub Actions talking points.

`scripts/record_demos.py` records the real interactions against an isolated freshly seeded server; `scripts/browser_smoke.py` independently asserts the persisted workflows. Temporary raw recordings are ignored by Git.
