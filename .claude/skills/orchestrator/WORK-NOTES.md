# Work notes

The temporary memory of one feature: **one comment on its spec issue**, starting with the marker
`<!-- work-notes -->`, edited in place after every step. It lives on GitHub and closes with the spec, so it never
reaches git and any session on any machine resumes from it.

The spec issue body stays the published spec; the notes do not copy it, they track the work against it.

## Rules

- **One comment per spec.** Opened at gate 6, edited (never re-posted) after each step, final at gate 12.
- **GitHub objects are the source of truth.** The notes point at issues, commits and the PR; they never replace
  them. When they disagree, fix the notes.
- **Promote as you go.** When a line becomes durable knowledge, move it to its home (orchestrator section 4) and
  leave `-> promoted to <file>` in its place.
- **Ids, counts and paths only.** No secrets, no personal data, no record contents: the comment is visible to
  everyone with access to the repo.
- **Short.** Each session reads the whole comment; prune what no longer bears on the next step.

## Commands

Write the body to a file in the session scratchpad first, then:

```
# find it (prints the comment id and body; empty when there are no notes yet)
gh api repos/{owner}/{repo}/issues/<spec#>/comments \
  --jq '.[] | select(.body | startswith("<!-- work-notes -->")) | {id, body}'

# open it (gate 6)
gh issue comment <spec#> --body-file <file>

# edit it in place
gh api --method PATCH repos/{owner}/{repo}/issues/comments/<id> -F body=@<file>
```

## Shape

```markdown
<!-- work-notes -->
## Work notes · branch `<spec#>-<slug>`

**Now:** gate <n>, <what is in progress>. **Next:** <exact next action>.

### Spec in progress
- Seams: <agreed test seams>
- Requirements touched: F<n>, N<n>; assumptions relied on: A<n>
- Decision in flight: <question>, recommended <answer>, waiting on <who>

### Tickets
- [x] #<a> <title> - <commit sha>
- [ ] #<b> <title> - blocked by #<a>

### Found out
- <fact found during the work, with where it came from>

### Open
- <question for the human, with the recommended answer>

### Promote before merge
- [ ] <decision> -> docs/adr/
- [ ] <belief> -> context/assumptions.md
- [x] <word> -> GLOSSARY.md (promoted)
```

## Closing (gate 12)

Every line under **Promote before merge** is ticked, **Open** is empty, and nothing under **Found out** or
**Spec in progress** still matters beyond this feature. Set **Now** to `closed: everything durable promoted` and
stop editing. The comment closes with the spec issue after QA.
