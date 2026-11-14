"""Shared helpers: load the repo's YAML files and run github-script steps through tests/harness.mjs."""

import json
import pathlib
import subprocess

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"
HARNESS = ROOT / "tests" / "harness.mjs"


def load_yaml(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def triggers(workflow):
    # PyYAML (YAML 1.1) reads the bare key `on` as True.
    return workflow.get("on", workflow.get(True))


def form_paths():
    return sorted(p for p in FORMS_DIR.glob("*.yml") if p.name != "config.yml")


def form_by_name(name):
    for path in form_paths():
        form = load_yaml(path)
        if form["name"] == name:
            return form
    raise KeyError(name)


def render_issue_body(form, answers):
    """Build an issue body the way GitHub renders a submitted issue form."""
    parts = []
    for item in form["body"]:
        if item["type"] == "markdown":
            continue
        label = item["attributes"]["label"]
        if item["type"] == "checkboxes":
            value = "\n".join(f"- [X] {option['label']}" for option in item["attributes"]["options"])
        else:
            value = answers.get(label) or "_No response_"
        parts.append(f"### {label}\n\n{value}")
    return "\n\n".join(parts)


def github_script(workflow_file):
    """Return (script, env) of the single actions/github-script step in a workflow."""
    workflow = load_yaml(WORKFLOWS_DIR / workflow_file)
    steps = [
        step
        for job in workflow["jobs"].values()
        for step in job.get("steps", [])
        if step.get("uses", "").startswith("actions/github-script@")
    ]
    assert len(steps) == 1, f"{workflow_file}: expected one github-script step, found {len(steps)}"
    return steps[0]["with"]["script"], steps[0].get("env", {})


def run_script(script, context, env=None, existing_labels=()):
    payload = {
        "script": script,
        "context": context,
        "env": env or {},
        "existingLabels": list(existing_labels),
    }
    completed = subprocess.run(
        ["node", str(HARNESS)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(f"script crashed:\n{completed.stderr}")
    return json.loads(completed.stdout)
