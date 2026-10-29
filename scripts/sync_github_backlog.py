"""Idempotently create the teacher-aligned GitHub backlog and optional Project.

Run python scripts/sync_github_backlog.py [--project]. Uses gh's existing login;
never stores credentials. Teammates without verified GitHub accounts remain unassigned.
"""

import argparse
import json
import subprocess
from pathlib import Path

REPO = "Kundhan73/SE-MiniProject-SAMS"
OWNER = "Kundhan73"
ROOT = Path(__file__).resolve().parents[1]


def gh(*args, payload=None):
    result = subprocess.run(
        ["gh", *map(str, args)],
        input=json.dumps(payload) if payload else None,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else None


def api(path, payload=None):
    return gh(
        "api", path, *(["--method", "POST", "--input", "-"] if payload else []), payload=payload
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", action="store_true")
    args = parser.parse_args()
    backlog = json.loads((ROOT / "docs/backlog.json").read_text())
    # Check Project authorization before mutating anything when Project creation is requested.
    projects = gh("project", "list", "--owner", OWNER, "--format", "json") if args.project else None
    milestone_specs = {
        "Sprint 1 (19–23 Oct)": (
            "2026-10-23T18:29:59Z",
            "Teacher window: 19–23 October 2026. Recovery tracking created on 29 October; no claim of historical completion.",
        ),
        "Sprint 2 (26–30 Oct)": ("2026-10-30T18:29:59Z", "Teacher window: 26–30 October 2026."),
        "Testing (2–6 Nov)": (
            "2026-11-06T18:29:59Z",
            "Testing and optional Sprint 3: 2–6 November 2026.",
        ),
    }
    milestones = {m["title"]: m for m in api(f"repos/{REPO}/milestones?state=all&per_page=100")}
    for name, (due, description) in milestone_specs.items():
        if name not in milestones:
            milestones[name] = api(
                f"repos/{REPO}/milestones",
                {"title": name, "due_on": due, "description": description},
            )
    existing_labels = {x["name"] for x in api(f"repos/{REPO}/labels?per_page=100")}
    for name in ["sams-backlog", "needs-review", "validation-pending"] + [
        f"points:{p}" for p in [2, 3, 5]
    ]:
        if name not in existing_labels:
            api(
                f"repos/{REPO}/labels",
                {"name": name, "color": "245845", "description": "SAMS requirement tracking"},
            )
    issues = gh(
        "issue",
        "list",
        "--repo",
        REPO,
        "--state",
        "all",
        "--limit",
        "200",
        "--json",
        "number,title,url",
    )
    by_title = {i["title"]: i for i in issues}
    results = []
    for item in backlog:
        title = (item["jira"] + ": " if item["jira"] else "") + item["title"]
        issue = by_title.get(title)
        if not issue:
            source = (
                f"Source Jira: https://pes1ug24am327.atlassian.net/browse/{item['jira']}\n\n"
                if item["jira"]
                else ""
            )
            body = f"{item['description']}\n\n{source}Estimate: **{item['points']} story points**.\nOwner in submitted design: **{item['owner']}**.\nTeacher sprint: **{item['sprint']}**.\n\nImplementation is being reviewed in PR #1. Creation of this issue does not claim work occurred during a past sprint. External validation and team review remain pending where documented.\n"
            if not item["assignee"]:
                body += "\nGitHub assignee pending: this member has no verified collaborator account on the repository.\n"
            payload = {
                "title": title,
                "body": body,
                "milestone": milestones[item["sprint"]]["number"],
                "labels": [
                    "sams-backlog",
                    f"points:{item['points']}",
                    "validation-pending"
                    if item["sprint"].startswith("Testing")
                    else "needs-review",
                ],
            }
            if item["assignee"]:
                payload["assignees"] = [item["assignee"]]
            created = api(f"repos/{REPO}/issues", payload)
            issue = {
                "number": created["number"],
                "title": created["title"],
                "url": created["html_url"],
            }
        results.append({**item, **issue})
        print(issue["url"], flush=True)
    (ROOT / "docs/github-backlog.json").write_text(json.dumps(results, indent=2) + "\n")
    if args.project:
        project = next(
            (p for p in projects["projects"] if p["title"] == "SAMS · Course delivery"), None
        )
        if not project:
            project = gh(
                "project",
                "create",
                "--owner",
                OWNER,
                "--title",
                "SAMS · Course delivery",
                "--format",
                "json",
            )
        number = project["number"]
        gh("project", "link", number, "--owner", OWNER, "--repo", REPO)
        fields = gh("project", "field-list", number, "--owner", OWNER, "--format", "json")["fields"]
        for name, kind in [("Story points", "NUMBER"), ("Sprint", "SINGLE_SELECT")]:
            if not any(f["name"] == name for f in fields):
                extra = (
                    ["--single-select-options", ",".join(milestone_specs)]
                    if kind == "SINGLE_SELECT"
                    else []
                )
                gh(
                    "project",
                    "field-create",
                    number,
                    "--owner",
                    OWNER,
                    "--name",
                    name,
                    "--data-type",
                    kind,
                    *extra,
                    "--format",
                    "json",
                )
        fields = gh("project", "field-list", number, "--owner", OWNER, "--format", "json")["fields"]
        points = next(f for f in fields if f["name"] == "Story points")
        sprint = next(f for f in fields if f["name"] == "Sprint")
        for item in results:
            card = gh(
                "project",
                "item-add",
                number,
                "--owner",
                OWNER,
                "--url",
                item["url"],
                "--format",
                "json",
            )
            gh(
                "project",
                "item-edit",
                "--id",
                card["id"],
                "--project-id",
                project["id"],
                "--field-id",
                points["id"],
                "--number",
                item["points"],
            )
            option = next(o for o in sprint["options"] if o["name"] == item["sprint"])
            gh(
                "project",
                "item-edit",
                "--id",
                card["id"],
                "--project-id",
                project["id"],
                "--field-id",
                sprint["id"],
                "--single-select-option-id",
                option["id"],
            )
        (ROOT / "docs/github-project.json").write_text(json.dumps(project, indent=2) + "\n")
        print(project.get("url", f"https://github.com/users/{OWNER}/projects/{number}"))


if __name__ == "__main__":
    main()
