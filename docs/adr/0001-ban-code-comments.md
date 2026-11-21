# 1. Ban code comments

- Status: Accepted
- Date: 2026-11-21

## Context

Comments come in four kinds:

- **Tautology**: repeats what the code already says.
- **Excuse**: justifies a hacky implementation instead of fixing it, so the hack gets copied.
- **Stale**: describes code or behaviour that has since changed.
- **Decision record**: explains an important, non-obvious choice.

The first three are noise or actively misleading. The fourth is worth keeping, but a comment is the wrong place for it: it can only be found by reading that file, it has no status or date, and nothing flags it when the code around it changes.

An audit on 2026-11-21 found no comments in this repository, so nothing needed deleting, filing, or moving.

## Decision

No file in this repository contains comments. What a comment would have said goes somewhere better:

| Instead of a comment that…          | Do this                                           |
| ----------------------------------- | ------------------------------------------------- |
| repeats the code, or is out of date | Delete it                                         |
| excuses a hack                      | Delete it and open an issue to fix the hack       |
| records a decision                  | Write an ADR in `docs/adr/`                       |
| explains what code does             | Rename things until it doesn't need explaining    |
| explains why a change was made      | Put it in the commit message or PR description    |

`scripts/lint_comments.py` enforces this in CI (`.github/workflows/lint-comments.yml`). It parses each file type with a real parser, so a Markdown `# Heading` or a `#` inside a YAML string is not mistaken for a comment. It fails on any file type it has no parser for, so the ban has no silent gaps.

Comments that can't be removed straight away are listed verbatim in `scripts/comment-baseline.json`, which works as a ratchet. CI fails when a file has a comment the baseline doesn't list. It also fails when the baseline lists a comment that no longer exists, so the baseline has to be tightened (`--tighten`) in the same change that deletes the comment. The tool never adds entries. Growing the baseline means editing the file by hand, which reviewers will see.

The `/delete-comment` skill (`.claude/skills/delete-comment/SKILL.md`) repeats the audit.

## Consequences

- The ban covers `#` comments, docstrings and bare string statements in Python; `#` comments in YAML (including Markdown front matter), pip requirements files and `.gitignore`; and both `<!-- -->` and `[//]: # (…)` comments in Markdown. Bare strings are included because they are the usual way around a comment ban.
- Machine directives are written as comments, so they count too: shebangs, `# noqa`, `# type: ignore`, `# yaml-language-server`, and the version notes that usually sit next to SHA-pinned actions. When one is unavoidable, add it to the baseline by hand so the exception is visible in review. This is why workflows pin actions to release tags rather than commit SHAs: a SHA with no version note beside it can't be read.
- Templates can't hide guidance inside `<!-- -->`. Prompts stay visible for the author to replace, which is what `.github/pull_request_template.md` already does.
- Before adding a new file type (a shell script, `CODEOWNERS`), add a parser and tests for it to `scripts/lint_comments.py`. CI fails until that's done.
