# Coding Standard

These rules are judgement calls a reviewer has to apply. Anything mechanical (formatting, import order, banned APIs, unused code) belongs in the linter or CI, and this file defers to it. When a reviewer keeps flagging the same mechanical issue, turn it into a check (see `/retro`).

The reviewer also applies the Fowler smell baseline in the `code-review` skill. Where a rule here contradicts the baseline, this file wins.

## Naming

- **CODE-1** Names reveal intent and use the terms from `GLOSSARY.md`. If you can't find an honest name, the design is murky; fix the design, not the name.
- **CODE-2** Booleans read as predicates (`is_active`, `has_access`). Functions read as verbs, values as nouns.
- **CODE-3** Domain concepts get their own small types instead of bare strings or integers (`OrderId`, `Money`).

## Structure

- **CODE-4** A function does one thing at one level of abstraction. If describing it takes "and", split it.
- **CODE-5** Shapes that repeat get extracted once they appear in two places in the same change, not before.
- **CODE-6** Parameters that always travel together become one type.
- **CODE-7** Match the style of the surrounding code: comment density, naming, idiom. Consistency beats your personal preference.
- **CODE-8** Comments explain why something is done, never what. Delete commented-out code.

## Errors and edges

- **CODE-9** Validate at the system boundary (request, CLI, file, queue). Inside the boundary, trust your types.
- **CODE-10** Fail loudly and specifically: raise or return a typed error that names the problem. Never swallow an exception silently.
- **CODE-11** Error messages say what failed and what the caller can do about it, without leaking internals (`standards/security.md`).

## Configuration

- **CODE-12** Configuration comes from the environment or a config file, never from literals scattered through the code. Each setting has one place that reads it.
- **CODE-13** Every setting has a safe default, or the app fails at startup with a clear message when it is missing.

## Language defaults

- **Python**: type hints on public functions, `ruff` for lint and format, `pytest` for tests.
- **TypeScript**: `strict` mode, ESLint plus Prettier, and `/setup-ts-deep-modules` to enforce ARCH-2.
