# .github

Default community health files for the Nexar-Hub organization, plus the decision framework that
applies to everything we ship.

## Decision architecture: Prospect Theory

| Path | What it is |
|---|---|
| [`docs/prospect-theory/PLAYBOOK.md`](docs/prospect-theory/PLAYBOOK.md) | The playbook (in Spanish): the two curves, the four levers, how to apply them surface by surface, a copy bank, a review checklist, how to turn it into experiments, and the ethical limits. |
| [`tools/copy_audit.py`](tools/copy_audit.py) | Scans any folder of copy, UI strings, templates or translations (ES/EN) and lists hypotheses to test, each tied to a lever. |
| [`tools/prospect_theory.py`](tools/prospect_theory.py) | Calculator for the value function, probability weights, hedonic editing, framing and raffles. |
| [`tools/render_curves.py`](tools/render_curves.py) | Regenerates the playbook charts from the model. |
| [`tools/tests/`](tools/tests/) | Tests for the claims the playbook makes and for every audit rule. |

```sh
python3 tools/copy_audit.py path/to/project --format md > audit.md
python3 tools/prospect_theory.py frame 300
python3 -m unittest discover -s tools/tests
```

Python 3.9+ standard library only.

## Templates

- [`.github/pull_request_template.md`](.github/pull_request_template.md): default PR template,
  including the *Decision architecture* section for user-facing changes.
- [`.github/ISSUE_TEMPLATE/task.yml`](.github/ISSUE_TEMPLATE/task.yml): scoped work request.
- [`.github/ISSUE_TEMPLATE/experiment.yml`](.github/ISSUE_TEMPLATE/experiment.yml): pre-registered
  behavioral experiment.
