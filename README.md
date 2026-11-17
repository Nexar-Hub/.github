# .github

Default community health files for every Nexar-Hub repository that does not define its own.

| File | Purpose |
| --- | --- |
| `.github/pull_request_template.md` | Default pull request description |
| `.github/ISSUE_TEMPLATE/task.yml` | Scoped work request |
| `.github/ISSUE_TEMPLATE/agent-guardrail.yml` | Turn an agent mistake into an automated check |

## Agent mistakes become checks, not instructions

When you correct a mistake an agent made, do not add another line to AGENTS.md. Encode it as a lint rule, test, or CI check in the affected repository, so it is fixed once and every future pull request is checked against it. Track it with an **Agent mistake → guardrail** issue.

Pull requests with UI or behavior changes include screenshots or a video of the change running, so review starts from what the change does.
