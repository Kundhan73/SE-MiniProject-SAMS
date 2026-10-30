"""Synchronize current GitHub assignments and the linked course Project.

Run python scripts/sync_github_backlog.py [--project]. Uses gh's existing login,
updates existing issues in place and never stores credentials. docs/team.json
and docs/backlog.json define the current three-role allocation.
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
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else None


def api(path, payload=None, method=None):
    extra = ["--method", method or "POST", "--input", "-"] if payload is not None else []
    return gh("api", path, *extra, payload=payload)


def body_for(item):
    source = (
        f"Reference Jira: https://pes1ug24am327.atlassian.net/browse/{item['jira']}\n\n"
        if item["jira"]
        else ""
    )
    return f"""{item["description"]}

{source}Estimate: **{item["points"]} story points**.
Accountable owner: **{item["owner"]} (@{item["assignee"]})**.
Project role: **{item["role"]}**.
Teacher sprint: **{item["sprint"]}**.

Current team: Kundhan73 — Developer; DarkTJ7 — Tester; planetai05 — QA.
Implementation, independent testing and QA review have separate responsibilities; see docs/TEAM_ROLES.md. Assignment does not claim that a person has already performed the work or approved a release.

Implementation PR: #1. GitHub is the current assignment system; Jira is retained as a reference backlog. Tracking created on 29 October does not claim work occurred during an earlier sprint window. External validation and actual peer/QA review remain pending where documented.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", action="store_true")
    args = parser.parse_args()
    backlog = json.loads((ROOT / "docs/backlog.json").read_text())
    team = json.loads((ROOT / "docs/team.json").read_text())["members"]
    valid = {(m["github"], m["role"]) for m in team}
    if any((i["assignee"], i["role"]) not in valid for i in backlog):
        raise ValueError("Every backlog item must have a current team member and matching role")
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
    labels = {x["name"] for x in api(f"repos/{REPO}/labels?per_page=100")}
    for name in (
        ["sams-backlog", "needs-review", "validation-pending"]
        + [f"points:{p}" for p in [2, 3, 5]]
        + [f"role:{r.lower()}" for r in ["Developer", "Tester", "QA"]]
    ):
        if name not in labels:
            api(
                f"repos/{REPO}/labels",
                {
                    "name": name,
                    "color": "245845",
                    "description": "SAMS requirement or workstream tracking",
                },
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
        "number,title,url,body,assignees,labels,milestone",
    )
    by_title = {i["title"]: i for i in issues}
    results = []
    for item in backlog:
        title = (item["jira"] + ": " if item["jira"] else "") + item["title"]
        issue = by_title.get(title)
        body = body_for(item)
        managed_labels = [
            "sams-backlog",
            f"points:{item['points']}",
            f"role:{item['role'].lower()}",
            "validation-pending" if item["sprint"].startswith("Testing") else "needs-review",
        ]
        # Keep unrelated labels, while updating managed roles/estimates and actual assignees.
        keep = (
            [
                label["name"]
                for label in issue.get("labels", [])
                if not label["name"].startswith(("points:", "role:"))
                and label["name"] not in ["sams-backlog", "needs-review", "validation-pending"]
            ]
            if issue
            else []
        )
        payload = {
            "title": title,
            "body": body,
            "milestone": milestones[item["sprint"]]["number"],
            "labels": keep + managed_labels,
            "assignees": [item["assignee"]],
        }
        changed = (
            not issue
            or issue["body"] != body
            or [a["login"] for a in issue["assignees"]] != [item["assignee"]]
            or set(label["name"] for label in issue["labels"]) != set(payload["labels"])
            or (issue.get("milestone") or {}).get("title") != item["sprint"]
        )
        if changed:
            path = f"repos/{REPO}/issues" + (f"/{issue['number']}" if issue else "")
            updated = api(path, payload, method="PATCH" if issue else "POST")
            issue = {
                "number": updated["number"],
                "title": updated["title"],
                "url": updated["html_url"],
            }
        results.append({**item, **{k: issue[k] for k in ["number", "title", "url"]}})
        print(issue["url"], flush=True)
    (ROOT / "docs/github-backlog.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    )
    if not args.project:
        return
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
    for name, kind, options in [
        ("Story points", "NUMBER", None),
        ("Sprint", "SINGLE_SELECT", ",".join(milestone_specs)),
        ("Team role", "SINGLE_SELECT", "Developer,Tester,QA"),
    ]:
        if not any(f["name"] == name for f in fields):
            extra = ["--single-select-options", options] if options else []
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
    fields = {
        f["name"]: f
        for f in gh("project", "field-list", number, "--owner", OWNER, "--format", "json")["fields"]
    }
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
        base = ["project", "item-edit", "--id", card["id"], "--project-id", project["id"]]
        gh(*base, "--field-id", fields["Story points"]["id"], "--number", item["points"])
        status = (
            "Done"
            if item["status"] == "Done"
            else "In progress"
            if item["status"] == "Needs review"
            else "Todo"
        )
        for name, value in [
            ("Sprint", item["sprint"]),
            ("Team role", item["role"]),
            ("Status", status),
        ]:
            field = fields[name]
            option = next(
                o
                for o in field["options"]
                if o["name"].replace(" ", "").lower() == value.replace(" ", "").lower()
            )
            gh(*base, "--field-id", field["id"], "--single-select-option-id", option["id"])
    # Existing repository teammates need access to the private course board as well.
    collaborators = []
    for member in team:
        if member["github"] != OWNER:
            user = api(f"users/{member['github']}")
            collaborators.append({"userId": user["node_id"], "role": "WRITER"})
    gh(
        "api",
        "graphql",
        "--input",
        "-",
        payload={
            "query": "mutation($input:UpdateProjectV2CollaboratorsInput!){updateProjectV2Collaborators(input:$input){clientMutationId}}",
            "variables": {"input": {"projectId": project["id"], "collaborators": collaborators}},
        },
    )
    gh(
        "project",
        "edit",
        number,
        "--owner",
        OWNER,
        "--readme",
        (ROOT / "docs/TEAM_ROLES.md").read_text(),
        "--description",
        "SAMS: Kundhan (Developer), Tarun (Tester), Anish (QA). Requirements, story points, sprints and evidence-based review.",
    )
    project = gh("project", "view", number, "--owner", OWNER, "--format", "json")
    (ROOT / "docs/github-project.json").write_text(json.dumps(project, indent=2) + "\n")
    print(project.get("url", f"https://github.com/users/{OWNER}/projects/{number}"), flush=True)


if __name__ == "__main__":
    main()
