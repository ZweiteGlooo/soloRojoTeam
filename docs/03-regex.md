# Stage 1 — Information extraction with regular expressions

Module: `resumelens/extraction.py` · Tests: `tests/test_extraction.py`

## Scope
Stage 1 **finds** candidate data and qualification strings and keeps them **exactly as written**
(`React.js`, `NodeJS`, `Py Torch`). It does not decide that two strings are equivalent (Stage 2) and
does not decide whether a profile is satisfied (Stage 3).

**Output** (`extract(text)` → `dict`, saved as JSON with `save_json`):

| Key | Content |
|---|---|
| `name` | Candidate name |
| `contact` | `emails`, `phones`, `linkedin`, `github` |
| `experience` | list of `{years, description}` |
| `education` | list of `{degree, field}` |
| `qualifications` | `{category: [strings]}` for programming languages, frameworks/libraries, databases, tools/technologies, competencies |
| `raw_skills` | technical strings in order of appearance → **input to Stage 2** |

## Notation
Σ = the set of Unicode characters. `L(r)` = the language denoted by expression *r*.
All qualification patterns are matched case-insensitively, so for each letter *a*, `a` ≡ `(a|A)`.

## Candidate data

| Information | Regular expression | Language recognized | Example |
|---|---|---|---|
| Name | `\A\s*([A-Z][\w'-]+(?:[ \t]+[A-Z][\w'-]+){1,3})[ \t]*$` (accented capitals included) | The first line of the text when it is made of 2–4 words, each starting with a capital letter | `Mary Jane Watson` |
| Email | `[\w.%+-]+@[\w-]+(?:\.[\w-]+)+` | A non-empty local part, `@`, then a domain of one or more labels separated by `.` | `peter.parker@dailybugle.com` |
| Phone | `(?<!\d)(?:\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)` | An optional `+` country code, then 10 digits grouped 3-3-4 (area code optionally in parentheses), with optional space, `.` or `-` separators. Year ranges such as `2019 - 2022` don't match | `+57 300 123 4567` |
| LinkedIn | `(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+` | An optional scheme and `www.`, the fixed string `linkedin.com/in/`, then a username | `linkedin.com/in/peterparker` |
| GitHub | `(?:https?://)?(?:www\.)?github\.com/[\w-]+` | Same structure, with `github.com/` | `github.com/spidey-dev` |
| Experience | `(\d+)\+?\s*years?\s+of\s+experience\s*(?:in\|as\|with)?\s*([^.\n]*)` | A number, *year(s) of experience*, then a description up to the end of the sentence. Group 1 = years, group 2 = description | `3 years of experience developing web applications` |
| Education | `\b(B\.?Sc\.?\|M\.?Sc\.?\|Ph\.?D\.?\|Bachelor's\|Bachelor\|Master's\|Master)(?![a-z])\s*(?:in\|of)?\s*([^.\n]*)` | A degree from a finite set (with or without dots), optionally *in/of*, then the field up to the end of the sentence | `B.Sc. in Software Engineering` |

## Qualifications

Each category is **one alternation** of the accepted spellings of its technologies (`SKILLS` in `extraction.py`):

| Category | Excerpt | Language recognized (case-insensitive) |
|---|---|---|
| Programming language | `java[\s-]?script\|js\|…\|python(?:\s?3)?\|py\|java\|c#\|c\+\+\|…\|sql` | {javascript, java script, java-script, js, python, python3, python 3, py, java, c#, c++, …} |
| Framework / library | `react(?:\.?js)?\|node(?:\.?js)?\|scikit[\s-]?learn\|sk[\s-]?learn\|tensor[\s-]?flow\|py[\s-]?torch\|…` | {react, reactjs, react.js, node, nodejs, node.js, scikit-learn, scikit learn, sklearn, tensorflow, tensor flow, pytorch, py torch, …} |
| Database | `postgres(?:ql)?\|my[\s-]?sql\|sql[\s-]?server\|…\|no[\s-]?sql` | {postgres, postgresql, mysql, my sql, sql server, …, nosql, no sql} |
| Tool / technology | `git[\s-]?hub\|git[\s-]?lab\|git\|docker\|…\|rest(?:ful)?(?:\s+apis?)?` | {github, gitlab, git, docker, …, rest, restful, rest api(s)} |
| Competency | `machine[\s-]?learning(?:\s+models?)?\|ml\|predictive\s+models?\|…` | {machine learning (models), ml, predictive model(s), …} |

Every alternative is wrapped in boundaries that also respect the characters technology names contain:

```
LEFT  = (?<![\w#+.])   not preceded by a letter, digit, "_", "#", "+" or "."
RIGHT = (?![\w#+])     not followed by a letter, digit, "_", "#" or "+"
```

`\b` alone is not enough, because names contain `.`, `#` and `+` (`C#`, `C++`, `React.js`). Excluding
`.` on the left is what stops `js` from being taken out of `React.js`. The right boundary is why
`java` is never found inside `JavaScript` and `git` is never found inside `GitHub`: in both cases the
next character is a letter.

All categories are joined into **one scanner**:

```
SCANNER = (?P<skip> email | url) | (?P<database> …) | (?P<framework_library> …) | … | (?P<programming_language> …)
```

`finditer` reads the text left to right. At each position it takes the first alternative that matches
and resumes **after** the match. `m.lastgroup` gives the category.

## Design decisions
1. **Keep the surface form.** Stage 1 returns `React.js`, not `REACT`. Normalization is the
   transducers' job, so each formal model has exactly one responsibility.
2. **No overlaps, by construction.** Because `finditer` resumes after each match, `No SQL` is reported
   once and `SQL` is never extracted from inside it.
3. **Alternative order matters.** In a regex alternation the first alternative that matches wins, not
   the longest. So longer spellings are listed first (`git[\s-]?hub` before `git`), and categories are
   ordered so that `Py Torch` (framework) and `SQL Server` (database) are tried before `py` and `sql`
   (languages).
4. **Emails and URLs are consumed as `skip`.** This stops `github` in `github.com/user` or `python` in
   `node@python.org` from being reported as skills.
5. **Order of appearance is preserved.** `raw_skills` follows the résumé text. Canonical ordering
   comes after normalization.
6. **Short ambiguous names.** `Go` is only accepted when followed by a separator (`,` `.` `;` newline),
   so *"to go home"* is not a skill. `R` is not supported, because a one-letter name causes too many
   false positives.

## Limitations
- The name regex assumes the name is the first line and written in Title Case.
- Only technologies listed in `QUALIFICATION_PATTERNS` are detected (closed vocabulary).
- Short tokens (`js`, `ts`, `py`, `ml`) could produce false positives in unusual text.
- Phones must follow the 10-digit 3-3-4 grouping.
- Free-text experience is captured only when it follows the "*n* years of experience …" pattern.
