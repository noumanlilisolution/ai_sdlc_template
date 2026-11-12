<!-- One PR per spec. Body follows the `pr` skill. Use GLOSSARY.md words. -->
<!-- Add exactly one label: door:one-way or door:two-way (see docs/github.md). -->

Closes #<ticket> #<ticket>  (the spec and the request issue are closed by hand after QA)

## Summary

<diagram, diff-sketch, call tree or file tree: the smallest view that makes the point>

## Evidence

- **Before:** <failing test, log lines, counts>
  **After:** <passing test, log lines, counts>

`python scripts/check.py` -> green

<!-- Delete this section unless the docs check (orchestrator gate 10) left findings the human agreed to leave. -->
## Docs waivers

- `<path>`: <the finding>. Waived because <reason>; follow-up #<issue> (or "none needed").

## Merge Danger

**Door:** <one-way or two-way>

**Blast Radius:** <one word>

<what a bad merge could break, and how to walk it back>
