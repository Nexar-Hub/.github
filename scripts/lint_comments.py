import argparse
import ast
import bisect
import io
import json
import re
import subprocess
import sys
import tokenize
from collections import Counter
from pathlib import Path, PurePath
from typing import NamedTuple

import yaml
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "scripts" / "comment-baseline.json"
POLICY = "docs/adr/0001-ban-code-comments.md"
HIDDEN_LINK_DESTINATIONS = {"", "#"}
MARKDOWN = MarkdownIt("commonmark", {"inline_definitions": True}).enable("table")
FRONT_MATTER = re.compile(r"---\n((?:.*\n)*?)(?:---|\.\.\.)(?:\n|\Z)")
PARSE_ERRORS = (SyntaxError, ValueError, tokenize.TokenError, yaml.YAMLError)


class Comment(NamedTuple):
    first_line: int
    last_line: int
    standalone: bool
    text: str


class Source:
    def __init__(self, text):
        self.text = text
        self.line_starts = [0] + [match.end() for match in re.finditer("\n", text)]

    def line_at(self, offset):
        return bisect.bisect_right(self.line_starts, offset)

    def line_end(self, line):
        return self.line_starts[line] - 1 if line < len(self.line_starts) else len(self.text)

    def offset(self, line, column):
        return self.line_starts[line - 1] + column

    def offset_from_utf8(self, line, byte_column):
        line_text = self.text[self.line_starts[line - 1] : self.line_end(line)]
        return self.offset(line, len(line_text.encode()[:byte_column].decode()))

    def comment(self, start, end):
        first_line, last_line = self.line_at(start), self.line_at(max(start, end - 1))
        before = self.text[self.line_starts[first_line - 1] : start]
        after = self.text[end : self.line_end(last_line)]
        standalone = not before.strip() and not after.strip()
        return Comment(first_line, last_line, standalone, self.text[start:end].strip())


def hash_comment_spans(text, start, end):
    return [(start + match.start(), start + match.end()) for match in re.finditer(r"#[^\n]*", text[start:end])]


def is_bare_string(node):
    if isinstance(node, ast.JoinedStr):
        return True
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def python_comments(text):
    source = Source(text)
    spans = [
        (source.offset(*token.start), source.offset(*token.end))
        for token in tokenize.generate_tokens(io.StringIO(text).readline)
        if token.type == tokenize.COMMENT
    ]
    spans += [
        (
            source.offset_from_utf8(node.lineno, node.col_offset),
            source.offset_from_utf8(node.end_lineno, node.end_col_offset),
        )
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.Expr) and is_bare_string(node.value)
    ]
    return [source.comment(start, end) for start, end in spans]


def yaml_comments(text):
    source = Source(text)
    spans, scanned_until = [], 0
    for token in yaml.scan(text, Loader=yaml.SafeLoader):
        start, end = token.start_mark.index, token.end_mark.index
        spans += hash_comment_spans(text, scanned_until, start)
        if isinstance(token, yaml.ScalarToken) and token.style in ("|", ">"):
            header_end = text.find("\n", start, end)
            spans += hash_comment_spans(text, start, end if header_end == -1 else header_end)
        scanned_until = max(scanned_until, end)
    spans += hash_comment_spans(text, scanned_until, len(text))
    return [source.comment(start, end) for start, end in spans]


def inline_html_comments(token):
    line = token.map[0] + 1
    for child in token.children:
        if child.type == "html_inline" and child.content.startswith("<!--"):
            yield Comment(line, line + child.content.count("\n"), False, child.content.strip())
        line += child.content.count("\n") + (child.type in ("softbreak", "hardbreak"))


def markdown_comments(text):
    comments = []
    front_matter = FRONT_MATTER.match(text)
    if front_matter:
        comments += [
            comment._replace(first_line=comment.first_line + 1, last_line=comment.last_line + 1)
            for comment in yaml_comments(front_matter.group(1))
        ]
        text = "\n" * front_matter.group(0).count("\n") + text[front_matter.end() :]
    source = Source(text)
    for token in MARKDOWN.parse(text):
        if token.type == "html_block":
            block_start, block_end = source.line_starts[token.map[0]], source.line_end(token.map[1])
            for match in re.finditer(r"<!--.*?(?:-->|\Z)", text[block_start:block_end], re.S):
                comments.append(source.comment(block_start + match.start(), block_start + match.end()))
        elif token.type == "definition" and token.meta["url"] in HIDDEN_LINK_DESTINATIONS:
            comments.append(source.comment(source.line_starts[token.map[0]], source.line_end(token.map[1])))
        elif token.type == "inline":
            comments += inline_html_comments(token)
    return comments


def pip_requirements_comments(text):
    source = Source(text)
    return [source.comment(match.start(1), match.end(1)) for match in re.finditer(r"(?:^|[ \t])(#.*)", text, re.M)]


def gitignore_comments(text):
    source = Source(text)
    return [source.comment(match.start(), match.end()) for match in re.finditer(r"^#.*", text, re.M)]


def json_comments(text):
    json.loads(text)
    return []


HANDLERS_BY_NAME = {".gitignore": gitignore_comments, "requirements.txt": pip_requirements_comments}
HANDLERS_BY_SUFFIX = {
    ".json": json_comments,
    ".md": markdown_comments,
    ".py": python_comments,
    ".yaml": yaml_comments,
    ".yml": yaml_comments,
}


def handler_for(path):
    path = PurePath(path)
    return HANDLERS_BY_NAME.get(path.name) or HANDLERS_BY_SUFFIX.get(path.suffix)


def find_comments(path, text):
    return sorted(handler_for(path)(text))


def repository_files():
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return sorted(path for path in set(listing.split("\0")) if path and (ROOT / path).is_file())


def under_any(files, scopes):
    prefixes = [Path(scope).resolve().relative_to(ROOT).as_posix() for scope in scopes]
    if not prefixes or "." in prefixes:
        return files
    return [path for path in files if any(path == prefix or path.startswith(prefix + "/") for prefix in prefixes)]


def scan(files):
    comments, problems = {}, []
    for path in files:
        if handler_for(path) is None:
            problems.append(f"{path}: no comment parser for this file type; add one to scripts/lint_comments.py")
            continue
        try:
            found = find_comments(path, (ROOT / path).read_text(encoding="utf-8"))
        except PARSE_ERRORS as error:
            problems.append(f"{path}: cannot parse: {error}")
            continue
        if found:
            comments[path] = found
    return comments, problems


def first_line_of(text):
    return (text.splitlines() or [""])[0][:100]


def lines_shed(comments):
    return sum(
        len({line for comment in found if comment.standalone for line in range(comment.first_line, comment.last_line + 1)})
        for found in comments.values()
    )


def violations(comments, baseline):
    found = []
    for path, file_comments in comments.items():
        allowed = Counter(baseline.get(path, []))
        for comment in file_comments:
            if allowed[comment.text]:
                allowed[comment.text] -= 1
            else:
                found.append(f"{path}:{comment.first_line}: comment: {first_line_of(comment.text)}")
    for path, texts in sorted(baseline.items()):
        gone = Counter(texts) - Counter(comment.text for comment in comments.get(path, []))
        if gone:
            found.append(f"{path}: baseline lists {sum(gone.values())} comment(s) that no longer exist; run --tighten")
    return found


def tightened(comments, baseline):
    result = {}
    for path, texts in baseline.items():
        kept = Counter(texts) & Counter(comment.text for comment in comments.get(path, []))
        if kept:
            result[path] = sorted(kept.elements())
    return result


def print_inventory(comments, problems):
    for path, found in comments.items():
        for comment in found:
            lines = str(comment.first_line) if comment.first_line == comment.last_line else f"{comment.first_line}-{comment.last_line}"
            placement = "standalone" if comment.standalone else "trailing"
            print(f"{path}:{lines}\t{placement}\t{first_line_of(comment.text)}")
    for problem in problems:
        print(problem, file=sys.stderr)
    total = sum(len(found) for found in comments.values())
    print(f"{total} comments in {len(comments)} files; deleting them sheds {lines_shed(comments)} lines")
    return 1 if problems else 0


def main():
    parser = argparse.ArgumentParser(description=f"Fail on any comment not listed in the ratchet baseline. Policy: {POLICY}")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", nargs="*", metavar="PATH", help="print every comment (under PATHs, if given) and the lines deleting them would shed")
    mode.add_argument("--tighten", action="store_true", help="remove baseline entries for comments that no longer exist; never adds entries")
    args = parser.parse_args()

    if args.list is not None:
        return print_inventory(*scan(under_any(repository_files(), args.list)))

    comments, problems = scan(repository_files())
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    if args.tighten:
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1
        result = tightened(comments, baseline)
        BASELINE_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        removed = sum(map(len, baseline.values())) - sum(map(len, result.values()))
        print(f"Removed {removed} baseline entries; {sum(map(len, result.values()))} remain.")
        return 0

    failures = problems + violations(comments, baseline)
    if failures:
        print("\n".join(failures), file=sys.stderr)
        print(
            f"\nComments are banned in this repository ({POLICY}). Delete the comment. "
            "If it excused a hack, file an issue; if it recorded a decision, write an ADR. "
            "The /delete-comment skill walks through it.",
            file=sys.stderr,
        )
        return 1
    print(f"No comments outside the baseline. Legacy comments left in it: {sum(map(len, baseline.values()))}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
