# .github

Organization-wide defaults for Nexar-Hub. Some files reach every repository automatically. The
automation is a workflow each repository turns on once.

## Inherited automatically

A repository that has no file of its own in the same place uses these:

| File | What it does |
|------|--------------|
| [`ISSUE_TEMPLATE/task.yml`](.github/ISSUE_TEMPLATE/task.yml) | "Task / work request" form |
| [`ISSUE_TEMPLATE/bug.yml`](.github/ISSUE_TEMPLATE/bug.yml) | "Bug report" form |
| [`ISSUE_TEMPLATE/config.yml`](.github/ISSUE_TEMPLATE/config.yml) | Turns off blank issues and links to nexarhub.com for anything else |
| [`pull_request_template.md`](.github/pull_request_template.md) | Default pull request description |
| [`CONTRIBUTING.md`](.github/CONTRIBUTING.md) | How work goes from issue to merge |
| [`SECURITY.md`](.github/SECURITY.md) | How to report a vulnerability privately |

This only works while this repository is public. A repository that adds its own
`.github/ISSUE_TEMPLATE/` folder stops inheriting all the forms and `config.yml`, so copy any you
want to keep.

## Automation

To turn it on in a repository, go to **Actions → New workflow → By Nexar Hub → Nexar Hub defaults**
and commit the file. It calls two reusable workflows from this repository:

- **Issue triage** ([`issue-triage.yml`](.github/workflows/issue-triage.yml)) labels Task and Bug
  issues from their form answers. It creates any label the repository is missing, and editing an
  answer swaps the label. Other labels are left alone.
- **Pull request check** ([`pr-check.yml`](.github/workflows/pr-check.yml)) fails until the template
  is filled in. Every section except Review needs content, and pull requests that are ready for
  review need every box ticked. Drafts may leave boxes unticked, and bots are skipped. The inputs
  `required-sections` and `require-checklist` change these rules.

| Label | Comes from |
|-------|------------|
| `task`, `bug` | The form used |
| `priority: low`, `priority: medium`, `priority: high` | Priority |
| `risk: low`, `risk: medium`, `risk: high` | Risk (Task form) |
| `work: feature`, `work: design-ui`, … | Type of work (Task form) |

To block merging until the template is filled in, require the status check
`pr-check / Template filled in` in a ruleset.

The workflow calls `@main`, so a change merged here reaches every repository at once. The
[Validate](.github/workflows/validate.yml) workflow tests every pull request to this repository.

## Settings to finish the setup

These live in GitHub settings, not in files:

1. **Organization settings → Code security**: turn on private vulnerability reporting for public
   repositories. The "Report a vulnerability" button in `SECURITY.md` depends on it.
2. Optional: require `pr-check / Template filled in` in a ruleset, per repository or for the whole
   organization if the plan allows it.

## Not inherited

GitHub never copies `CODEOWNERS`, `dependabot.yml`, labels, or workflows from this repository. The
issue triage workflow creates the labels it needs. The [`dependabot.yml`](.github/dependabot.yml)
here only keeps this repository's own actions up to date.

## Working on this repository

- `python3 -m unittest discover -s tests` checks the forms against GitHub's rules. It then runs both
  workflow scripts against issues and pull requests built from the real forms and template. It needs
  Python 3 with PyYAML, and Node.js.
- [`defaults.yml`](.github/workflows/defaults.yml) is this repository's own copy of the workflow
  template, pointed at the current commit. A test keeps the two in sync.
- CI also runs [actionlint](https://github.com/rhysd/actionlint) on every workflow.
