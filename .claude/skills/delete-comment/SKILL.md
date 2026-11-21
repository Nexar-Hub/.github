---
name: delete-comment
description: Audit the comments in this repository (or under the given paths), classify each as tautology, excuse, stale, or decision record, then delete it, file an issue for it, or move it into an ADR, and tighten the comment ratchet. Use when asked to remove, audit, or clean up comments, or when the comment lint fails.
argument-hint: "[path ...]"
---

# Delete comments

Comments are banned here; read `docs/adr/0001-ban-code-comments.md` first. This skill clears out existing comments, whether they are legacy ones listed in `scripts/comment-baseline.json` or new ones the lint is rejecting.

## 1. Inventory

```sh
pip install -r scripts/requirements.txt
python3 scripts/lint_comments.py --list $ARGUMENTS
```

The output has one line per comment: `path:line`, whether it is `standalone` (it has the line to itself) or `trailing`, and its first line of text. The last line gives the total, including how many lines deleting the comments sheds: every standalone comment line goes, and trailing comments shed nothing. Tell the user that estimate before changing anything.

If the lint reports a file type with no parser, add a handler and test cases to `scripts/lint_comments.py` first. Never skip the file.

## 2. Classify

Read the code around each comment. Use `git log -L <start>,<end>:<path>` to see when the comment was written and what changed since. Then give it exactly one category:

- **Tautology**: says what the next line visibly does, such as a heading over a block or a restated name or type.
- **Stale**: refers to code, behaviour, tickets, people, or versions that no longer match the repository. Check that whatever it mentions still exists.
- **Excuse**: admits or justifies a shortcut. Look for `TODO`, `FIXME`, `HACK`, `XXX`, "temporary", "workaround", "for now", "should really", "don't touch", or a suppressed check (`noqa`, `type: ignore`, `eslint-disable`).
- **Decision record**: explains a non-obvious choice that a careful maintainer would otherwise reverse, such as a constraint from outside the code, a rejected alternative, or a bug that odd-looking code avoids.

When a comment seems to fit more than one:

- An excuse that also explains its reasoning is an excuse. Put the reasoning in the issue.
- A decision record that is no longer true is stale.
- If deleting the comment would lead someone to "fix" correct code, it is a decision record.

## 3. Act

- **Tautology or stale**: delete the comment. If the code is unclear without it, rename variables or functions until it reads clearly. Rename only; don't change behaviour.
- **Excuse**: delete the comment, then file an issue in this repository. Search open issues first, and comment on an existing one rather than opening a duplicate. Follow the issue form in `.github/ISSUE_TEMPLATE/task.yml`:
  - Title: `[Task] Fix <the shortcut>`.
  - Objective: what a proper implementation looks like.
  - Affected area: `path:line` at the current commit.
  - Type of work: Refactor or Bug.
  - Context: the deleted comment, quoted verbatim, and the shortcut it excused.
  - Acceptance criteria, Out of scope, Priority, Risk.
- **Decision record**: write `docs/adr/NNNN-kebab-case-title.md` with the next free number, using the structure of ADR 0001: Status, Date, Context, Decision, Consequences. Several comments about the same decision become one ADR. If an accepted ADR already covers the decision, just delete the comment. If the comment contradicts an ADR, write a new ADR that supersedes it rather than editing the old one. Then delete the comment.

A comment that has to stay for now (for example a directive a tool needs) remains in the baseline. Say why in the PR description.

## 4. Ratchet

```sh
python3 scripts/lint_comments.py --tighten
python3 -m unittest discover -s scripts
python3 scripts/lint_comments.py
```

`--tighten` removes baseline entries for comments that are gone. The last command has to pass. Never add baseline entries to get it to pass.

## 5. Report

Give the user a table with each comment's location, category, and the action taken (deleted, issue #N, or ADR NNNN), then the totals: comments removed, lines shed, issues filed, ADRs written, and how many comments are left in the baseline.
