# Release status · 2 November 2026

PR #1 was merged into main at `c9e305f149970b3596ac7fd370c27f1c8e47f5ce` on 30 October, including QA PR #48, application/browser fixes PR #50 and validation/evidence PR #53. Main CI (41098273611), expanded browser acceptance (41098273791), and Delivery publication (41098586616) passed. This publication does not establish a remote deployment. Original contributor history, archived failures and source commits are retained.

PR #54 contains Tarun's new acceptance retests and a proposed performance change. The [2 November evidence](testing/tarun-2026-11-02/README.md) records actual application/Actions merge commits, passes, failed measurements, environment limits and remaining handoff. New commits use DarkTJ7's identity without an assistant co-author. Tool-assisted execution remains distinct from Tarun's personal conclusion.

## Developer integration completed

- Preserve both contributors' regression additions when resolving their shared test-file conflict.
- Include the health database-outage fix, corrected maintenance plan, monitor, final report and presentation outline.
- Include unique form labels, proxy headers, keyboard-scrollable tables and CSP-compatible Swagger assets.
- Include both dated tester reports and archives without relabeling their execution as testing of a newer commit.
- Correct monitoring of empty observation periods, wrong/redirected health responses and corrupt history; implement the advertised repeated-probe command.
- Strengthen positive browser/Lighthouse checks and verify that a mocked API failure is rejected.
- Refresh integrated backend reports from actual execution. Read docs/reports/summary.json and latest Actions artifacts for current counts and coverage.

## Decisions and work that remain open

| Owner | Remaining action |
| --- | --- |
| Tarun (DarkTJ7) | Personally review the evidence and record a scoped tester conclusion; confirm affected integration retests and required human/device observations. Assisted case execution alone is not his signature. |
| Anish (planetai05) | Review PR #54's diff and dated evidence, revised submission documents and unresolved acceptance items. The old 05ce028 review is dismissed; the owner-directed PR #1 merge does not constitute a new teammate review. |
| Developer / Tester / QA | Review the complete 2 November performance comparison and the proposed connection-reuse change in PR #54 before merging. The earlier 3,100 ms, merged-main 3,800 ms and threaded-repeat 6,800 ms scale failures remain recorded; the first threaded 2,900 ms pass alone is insufficient. |
| Owner / Faculty or IT | Supply a staging host/domain and external test email service if public TLS/internet delivery is required; otherwise obtain an explicit scope decision. No shared public server or mailbox is currently configured. |
| Team / Faculty | Complete faculty UAT and any required Jenkins/Sonar execution; confirm the evaluator's report format and rehearse the 15-minute demo. |
| Operator / QA | Install/rehearse backup, recovery, encrypted offsite retention and external monitoring. Semester/year observations cannot be completed instantaneously. |

Jira synchronization remains paused at the owner's request. GitHub is the current source of assignments and evidence. Do not automatically run the backlog sync script over reviewed statuses or restart Jira synchronization.

## Merge and delivery

Main retains its real peer-review requirement. PR #1 is already merged and published by Delivery; PR #54 still requires actual review and the required checks before merge. Recheck main CI and Delivery after any subsequent merge. Keep unresolved testing/operational tasks open; no faculty approval or teammate sign-off is inferred from integration, automated checks or an administrator merge.
