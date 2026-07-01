---
name: Policy False Positive
about: Report a blocker that appears stricter than the target repository requires
title: "Policy false positive: "
labels: policy,false-positive
assignees: ""
---

## Blocker

Paste the Themis blocker code and message.

## Command And Output

```bash
themis validate ...
```

- Status:
- Exit code:
- Output format:

## Target Repository Rule

Link or quote the upstream rule Themis should follow.

## Why This Should Pass

Explain why the submission satisfies the target repository's documented process.

## Evidence

Include tests, PR body sections, signoff details, changelog decision, and relevant paths.

## Proposed Adjustment

Describe the smallest rule/config/schema change that would avoid this false positive without weakening Themis for other repositories.
