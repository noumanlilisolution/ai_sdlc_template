# Technical architecture

One page: how the parts fit. Each detail has one home, linked from here.

## Flow

```
<the main path through the system, as a small text diagram>
```

## Shape of the code

- <how the code is organised: deep modules, layers, ports; link the code map>
- <where configuration and environment are read>

## Infrastructure

- <where it runs, what it talks to; link the README section that lists hosts and URLs>
- CI: `.github/workflows/` (`check` runs `scripts/check.py`; `agent-review` runs the three-axis review).
