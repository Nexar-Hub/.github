# Contributing

How work happens in Nexar Hub repositories. A repository can replace this guide with its own
`CONTRIBUTING.md`.

## 1. Start from an issue

- New work or a change: use the **Task / work request** form. Something broken: use **Bug report**.
- One issue, one objective. If you find more to do, open another issue.
- In repositories that run the [Nexar Hub defaults](https://github.com/Nexar-Hub/.github#automation)
  workflow, the form's priority, risk, and type of work become labels. To change a label, edit the
  answer in the issue.

## 2. Work on a branch

- Never change production directly. Every change goes branch → preview → review → merge.
- Name the branch after the kind of change: `feat/…`, `fix/…`, `chore/…`, or `docs/…`.
- Keep the branch on the issue's objective. Unrelated refactors go in their own pull request.

## 3. Open a pull request

- Fill in every section of the template. Under **Linked issue**, write `Closes #123`, or `None`.
- Tick a box in **Review** only when it is true.
- Open a draft while the work is in progress. The pull request check lets drafts leave boxes
  unticked, but it fails a pull request that is ready for review while a section is empty or a box
  is unticked.

## 4. Review and merge

- A person reviews every pull request before it is merged.
- Merge only after the preview was checked.
