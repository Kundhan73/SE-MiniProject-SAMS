# Team responsibilities and handoffs

Effective 29 October 2026. [GitHub Project](https://github.com/users/Kundhan73/projects/1) is the source of current assignments. Jira remains a reference backlog. The application access roles Student, Faculty and Admin describe users of SAMS and are separate from the project roles below.

| Role | Member | GitHub | Accountable work |
| --- | --- | --- | --- |
| Developer | Kundhan Vudutha | Kundhan73 | Implement all functional requirements, UI/API/database changes, test fixtures, CI/CD and fixes. Explain design decisions and supply regression checks. |
| Tester | Tarun J | DarkTJ7 | Independently design and execute functional/integration/system cases; test security, performance and accessibility; report reproducible defects; retest fixes. |
| QA | Anish | planetai05 | Review SRS/design/test plan, maintain traceability, inspect report quality and coverage, review PRs and confirm release readiness against the acceptance criteria. |

## Handoff

1. Developer links the requirement, implementation PR and automated regression evidence. Implementation remains in review until its checks and review are complete.
2. Tester runs the relevant cases against the exact commit, records actual results and files reproducible bugs. A passing CI run is evidence; it does not replace the Tester's assigned independent checks.
3. QA checks requirement coverage and the Tester's evidence, reviews unresolved defects and the release checklist, and gives an actual review decision. No approval is recorded on someone's behalf.
4. Developer addresses defects; Tester retests; QA rechecks the release evidence. Merge requires passing protected-branch checks and a real peer approval. Faculty UAT remains a separate requirement.

The board's Team role field identifies each item's accountable workstream. Feature stories belong to the Developer; linked testing tasks belong to the Tester; documentation assurance, traceability and release checks belong to QA. There is one accountable assignee per item.

CODEOWNERS routes QA review to planetai05 and test-related review to DarkTJ7/planetai05. It defines review responsibility, not a claim about who historically wrote each file.
