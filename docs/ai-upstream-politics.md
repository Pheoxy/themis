# AI Code Upstream Politics

The validator is intentionally strict because AI-assisted upstream work is politically and socially costly in many open source communities.

Common maintainer concerns found in recent project policies and reporting:

- Maintainers report being flooded with low-quality AI-generated pull requests and bug reports, which shifts cleanup work onto unpaid reviewers.
- Several communities use terms such as "AI slop" for submissions that appear plausible but are untested, unowned, stylistically mismatched, or disconnected from project norms.
- Projects that allow AI assistance increasingly require human accountability: the contributor must own every line, test it, and fix mistakes.
- Disclosure expectations are becoming common. Some projects require explicit disclosure in commit messages or PR descriptions when generative tools were used.
- Security and bug-report programs are especially sensitive because plausible but false reports waste scarce triage time and can distort incentives.
- Some maintainers are not opposed to tools themselves; they oppose submissions that bypass learning, debugging, provenance, licensing, and project-specific review discipline.

Policy examples and public reactions used to shape this tool:

- Apache Software Foundation guidance recommends indicating generative tooling use and keeping licensing compatibility in mind.
- OpenInfra policy emphasizes that contributors must have the right to contribute AI-tool output and that signoff means responsibility for the whole commit.
- Pulp Project policy requires AI use to be indicated in commit messages and assigns full responsibility to the contributor.
- OSRF policy calls for disclosure in source-code contribution commits.
- InfluxData allows AI-assisted contributions but expects adequate tests and validation.
- Graphite permits limited AI use while rejecting undisclosed, agent-written, or "AI slop" contributions.
- Linux kernel discussions and reporting emphasize disclosure, compliance with existing contribution rules, and human accountability.
- Godot, curl, RPCS3, and other communities have publicly objected to waves of low-quality AI-generated submissions and reports.

Design implications for this validator:

- Fail closed when upstream rules are missing or cannot be evaluated.
- Require evidence, not vibes: tests, disclosure, signoff, and human accountability have to be visible. The validator checks for that evidence; it does not assume accountability on behalf of the submitter.
- Treat generated/vendor/binary churn as suspicious unless explicitly allowed.
- Prefer hard blockers over advisory warnings for anything that would predictably waste maintainer time.
- Make the validator suspicious of its own output: a clean report means only that configured checks passed, not that the patch is inherently good.
