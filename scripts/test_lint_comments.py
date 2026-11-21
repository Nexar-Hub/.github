import unittest

from lint_comments import Comment, find_comments, handler_for, tightened, violations

CASES = [
    ("x.py", "x = 1  # trailing\n", [(1, 1, False)]),
    ("x.py", "# standalone\nx = 1\n", [(1, 1, True)]),
    ("x.py", 's = "# inside a string"\n', []),
    ("x.py", 'def f():\n    """Docstring."""\n    return 1\n', [(2, 2, True)]),
    ("x.py", '"""Module\ndocstring."""\n', [(1, 2, True)]),
    ("x.py", 'f"{x}"\n', [(1, 1, True)]),
    ("x.py", '"ééé"; x = 1\n', [(1, 1, False)]),
    ("x.yml", 'a: "x # y"  # trailing\n', [(1, 1, False)]),
    ("x.yml", "b: |  # header\n  # content\n  more\n# after\n", [(1, 1, False), (4, 4, True)]),
    ("x.yml", "c: plain#text #trailing\n", [(1, 1, False)]),
    ("x.yml", "{a: 1, # flow\n b: 2}\n", [(1, 1, False)]),
    ("x.yml", 'title: "[Task] "\nlist:\n  - "#1"\n', []),
    ("x.md", "# Heading\n\n## Subheading\n", []),
    ("x.md", "<!-- block -->\n", [(1, 1, True)]),
    ("x.md", "<!--\nmulti\n-->\n", [(1, 3, True)]),
    ("x.md", "text <!-- inline -->\n", [(1, 1, False)]),
    ("x.md", "a\nb <!-- second line -->\n", [(2, 2, False)]),
    ("x.md", "| a | b <!-- cell --> |\n|---|---|\n", [(1, 1, False)]),
    ("x.md", "`<!-- code -->` and `[//]: # (code)`\n", []),
    ("x.md", "```\n<!-- fenced -->\n# not a heading\n```\n", []),
    ("x.md", "[//]: # (one)\n[//]: # (two)\n[real]: https://example.com\n", [(1, 1, True), (2, 2, True)]),
    ("x.md", "---\nname: x  # front matter\n---\n# Heading\n", [(2, 2, False)]),
    ("requirements.txt", "# header\nPyYAML==6.0.3  # pin\nfoo @ https://e.com/a#egg=foo\n", [(1, 1, True), (2, 2, False)]),
    ("x.json", '{"a": "# not a comment"}\n', []),
    (".gitignore", "# header\n\\#literal\nbuild/ # not a comment\n", [(1, 1, True)]),
]


def comment(text):
    return Comment(1, 1, True, text)


class FindCommentsTest(unittest.TestCase):
    def test_cases(self):
        for path, text, expected in CASES:
            with self.subTest(path=path, text=text):
                found = [(c.first_line, c.last_line, c.standalone) for c in find_comments(path, text)]
                self.assertEqual(found, expected)

    def test_reports_comment_text_using_character_offsets(self):
        self.assertEqual(find_comments("x.py", '"ééé"; x = 1\n')[0].text, '"ééé"')

    def test_rejects_json_with_comments(self):
        with self.assertRaises(ValueError):
            find_comments("x.json", "{// no\n}\n")

    def test_has_no_parser_for_unknown_file_types(self):
        self.assertIsNone(handler_for("script.sh"))


class RatchetTest(unittest.TestCase):
    def test_comment_missing_from_baseline_fails(self):
        self.assertEqual(len(violations({"a.py": [comment("# new")]}, {})), 1)

    def test_comment_in_baseline_passes(self):
        self.assertEqual(violations({"a.py": [comment("# old")]}, {"a.py": ["# old"]}), [])

    def test_edited_legacy_comment_fails_as_new_and_gone(self):
        self.assertEqual(len(violations({"a.py": [comment("# edited")]}, {"a.py": ["# old"]})), 2)

    def test_deleted_comment_still_in_baseline_fails(self):
        self.assertEqual(len(violations({}, {"a.py": ["# old"]})), 1)

    def test_tighten_drops_deleted_comments_and_never_adds(self):
        comments = {"a.py": [comment("# kept"), comment("# new")]}
        baseline = {"a.py": ["# kept", "# deleted"], "gone.py": ["# deleted"]}
        self.assertEqual(tightened(comments, baseline), {"a.py": ["# kept"]})


if __name__ == "__main__":
    unittest.main()
