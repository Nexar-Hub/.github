"""Runs the reusable workflows' scripts against issues and pull requests built from the real forms and template."""

import re
import unittest

from helpers import (
    ROOT,
    WORKFLOWS_DIR,
    form_by_name,
    github_script,
    load_yaml,
    render_issue_body,
    run_script,
    triggers,
)

REPO = {"owner": "Nexar-Hub", "repo": "example"}
TASK = form_by_name("Task / work request")
BUG = form_by_name("Bug report")
LABEL_NAME = re.compile(r"^[a-z0-9: -]{1,50}$")
COLOR = re.compile(r"^[0-9a-f]{6}$")


def issue_event(body, labels=(), action="opened"):
    return {
        "eventName": "issues",
        "repo": REPO,
        "payload": {
            "action": action,
            "issue": {"number": 7, "body": body, "labels": [{"name": name} for name in labels]},
        },
    }


def labels_added(result):
    return [label for call in result["calls"] if call[0] == "addLabels" for label in call[1:]]


def labels_removed(result):
    return [call[1] for call in result["calls"] if call[0] == "removeLabel"]


class IssueTriage(unittest.TestCase):
    script, _ = github_script("issue-triage.yml")

    def triage(self, body, labels=(), existing=()):
        result = run_script(self.script, issue_event(body, labels), existing_labels=existing)
        self.assertIsNone(result["failed"])
        return result

    def test_new_task_gets_labels_created_and_applied(self):
        body = render_issue_body(TASK, {"Priority": "High", "Risk": "Low", "Type of work": "Design / UI"})
        result = self.triage(body)
        expected = ["task", "priority: high", "risk: low", "work: design-ui"]
        self.assertCountEqual(labels_added(result), expected)
        created = [call[1] for call in result["calls"] if call[0] == "createLabel"]
        self.assertCountEqual(created, expected)

    def test_existing_labels_are_not_recreated(self):
        body = render_issue_body(TASK, {"Priority": "Low", "Risk": "Low", "Type of work": "SEO"})
        result = self.triage(body, existing=["task", "priority: low", "risk: low", "work: seo"])
        self.assertFalse([call for call in result["calls"] if call[0] == "createLabel"])
        self.assertCountEqual(labels_added(result), ["task", "priority: low", "risk: low", "work: seo"])

    def test_editing_an_answer_swaps_the_label_and_keeps_others(self):
        body = render_issue_body(TASK, {"Priority": "Low", "Risk": "Low", "Type of work": "Content"})
        labels = ["task", "priority: high", "risk: low", "work: content", "client: acme"]
        result = self.triage(body, labels=labels, existing=labels)
        self.assertEqual(labels_added(result), ["priority: low"])
        self.assertEqual(labels_removed(result), ["priority: high"])

    def test_bug_report(self):
        body = render_issue_body(BUG, {"Priority": "Medium"})
        result = self.triage(body)
        self.assertCountEqual(labels_added(result), ["bug", "priority: medium"])
        self.assertEqual(labels_removed(result), [])

    def test_bug_report_leaves_risk_and_work_labels_alone(self):
        body = render_issue_body(BUG, {"Priority": "Medium"})
        result = self.triage(body, labels=["bug", "priority: medium", "risk: high"])
        self.assertEqual(result["calls"], [])

    def test_issue_without_form_is_left_alone(self):
        result = self.triage("Just a note.", labels=["priority: high"])
        self.assertEqual(result["calls"], [])

    def test_other_events_are_ignored(self):
        context = issue_event("x")
        context["eventName"] = "pull_request"
        result = run_script(self.script, context)
        self.assertEqual(result["calls"], [])
        self.assertIsNone(result["failed"])

    def test_every_dropdown_answer_makes_a_valid_label(self):
        # Adding a dropdown option must never produce a label GitHub would reject.
        for form in (TASK, BUG):
            for item in form["body"]:
                if item["type"] != "dropdown":
                    continue
                label = item["attributes"]["label"]
                for option in item["attributes"]["options"]:
                    with self.subTest(form=form["name"], field=label, option=option):
                        result = self.triage(render_issue_body(form, {label: option}))
                        for call in result["calls"]:
                            if call[0] == "createLabel":
                                _, name, color, description = call
                                self.assertRegex(name, LABEL_NAME)
                                self.assertRegex(color, COLOR)
                                self.assertLessEqual(len(description), 100)


def pull_request_event(body, draft=False, user_type="User"):
    return {
        "eventName": "pull_request",
        "repo": REPO,
        "payload": {
            "pull_request": {
                "number": 3,
                "body": body,
                "draft": draft,
                "user": {"login": "someone", "type": user_type},
            }
        },
    }


TEMPLATE = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
ANSWERS = {
    "Objective": "Make the contact form send email.",
    "Linked issue": "Closes #12",
    "Scope": "Contact form action and its test.",
    "Out of scope": "Page layout.",
    "Verification": "Sent a test message on the preview.",
}


def filled_template(answers=ANSWERS, tick=True):
    body = TEMPLATE
    for heading, answer in answers.items():
        body = re.sub(rf"(## {re.escape(heading)}\n\n<!--.*?-->)", rf"\1\n\n{answer}", body)
    return body.replace("- [ ]", "- [x]") if tick else body


class PullRequestCheck(unittest.TestCase):
    script, env = github_script("pr-check.yml")
    inputs = load_yaml(WORKFLOWS_DIR / "pr-check.yml")
    inputs = triggers(inputs)["workflow_call"]["inputs"]
    defaults = {
        "REQUIRED_SECTIONS": inputs["required-sections"]["default"],
        "REQUIRE_CHECKLIST": str(inputs["require-checklist"]["default"]).lower(),
    }

    def check(self, body, env=None, **event):
        return run_script(self.script, pull_request_event(body, **event), env={**self.defaults, **(env or {})})

    def test_inputs_reach_the_script(self):
        self.assertEqual(
            self.env,
            {
                "REQUIRED_SECTIONS": "${{ inputs.required-sections }}",
                "REQUIRE_CHECKLIST": "${{ inputs.require-checklist }}",
            },
        )

    def test_required_sections_exist_in_the_template(self):
        headings = re.findall(r"^## (.+)$", TEMPLATE, re.M)
        for name in self.defaults["REQUIRED_SECTIONS"].split(","):
            self.assertIn(name.strip(), headings)

    def test_untouched_template_fails_on_every_section(self):
        result = self.check(TEMPLATE)
        for name in ANSWERS:
            self.assertIn(f'"## {name}" is empty', result["failed"])
        self.assertIn("Unticked", result["failed"])

    def test_filled_template_passes(self):
        self.assertIsNone(self.check(filled_template())["failed"])

    def test_windows_line_endings_pass(self):
        self.assertIsNone(self.check(filled_template().replace("\n", "\r\n"))["failed"])

    def test_unticked_box_fails_when_ready_for_review(self):
        body = filled_template().replace("- [x] Ready for human review", "- [ ] Ready for human review")
        result = self.check(body)
        self.assertIn('"Ready for human review"', result["failed"])
        self.assertNotIn("is empty", result["failed"])

    def test_draft_may_leave_boxes_unticked(self):
        self.assertIsNone(self.check(filled_template(tick=False), draft=True)["failed"])

    def test_draft_still_needs_the_sections(self):
        self.assertIn('"## Objective" is empty', self.check(TEMPLATE, draft=True)["failed"])

    def test_checklist_can_be_optional(self):
        result = self.check(filled_template(tick=False), env={"REQUIRE_CHECKLIST": "false"})
        self.assertIsNone(result["failed"])

    def test_deleted_section_is_reported_as_missing(self):
        body = filled_template().replace("## Out of scope", "## Notes")
        self.assertIn('"## Out of scope" is missing', self.check(body)["failed"])

    def test_empty_description_fails(self):
        self.assertIn("is missing", self.check(None)["failed"])

    def test_bots_are_skipped(self):
        self.assertIsNone(self.check("Bump x from 1 to 2", user_type="Bot")["failed"])


class CallerWorkflows(unittest.TestCase):
    def test_this_repo_runs_the_same_workflow_it_offers(self):
        template = load_yaml(ROOT / "workflow-templates" / "nexar-hub-defaults.yml")
        local = load_yaml(WORKFLOWS_DIR / "defaults.yml")
        self.assertEqual(triggers(template), triggers(local))
        self.assertEqual(template.get("permissions"), local.get("permissions"))
        self.assertEqual(template["jobs"].keys(), local["jobs"].keys())
        for name, job in template["jobs"].items():
            remote = job["uses"]
            self.assertRegex(remote, r"^Nexar-Hub/\.github/\.github/workflows/[a-z-]+\.yml@")
            path = remote.split("Nexar-Hub/.github/", 1)[1].split("@", 1)[0]
            self.assertTrue((ROOT / path).exists(), f"{remote} points to a missing file")
            self.assertEqual(local["jobs"][name]["uses"], f"./{path}")
            self.assertEqual({k: v for k, v in job.items() if k != "uses"},
                             {k: v for k, v in local["jobs"][name].items() if k != "uses"})


if __name__ == "__main__":
    unittest.main()
