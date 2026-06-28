# Themis Mission

Themis is named for the Greek goddess of divine law, order, custom, and proper procedure.

The project exists to let upstream work continue while protecting the people who keep projects healthy. It is strict because maintainers, reviewers, and long-term contributors pay the cost when low-confidence code reaches review.

Themis should act like an assistant in the goddess's domains: law, order, custom, and proper procedure. It should help contributors discover rules, organize evidence, prepare pull request text, run checks, and draft PRs when the gate passes. Those assistant workflows still serve the pass/fail gate. The assistant role supports the contributor; it does not replace their responsibility.

Themis is not meant to punish new contributors. It is meant to make the expected standard explicit before a maintainer has to spend time discovering missing tests, unclear ownership, hidden AI assistance, ignored contribution rules, or one-off feature work that leaves the project with long-term maintenance debt.

Themis does not take accountability for contributors, AI tools, maintainers, or projects. It is an AI-assisted pull request blocker and evidence checker. A pass means only that Themis did not find configured hard blockers; it is not proof that the code is correct, safe, maintainable, legally clean, or acceptable upstream.

Themis especially protects against:

- AI slop that looks plausible but is untested, unowned, or disconnected from project norms.
- One-and-done pull requests that add a wanted feature but ignore maintainability, tests, documentation, or upstream process.
- Submissions from contributors, human or AI-assisted, who have not read the target project's rules.
- Review burden shifted onto maintainers by vague claims, missing evidence, or generated/vendor churn.
- False confidence from the validator itself. Themis must stay suspicious of its own output and treat a pass as only a gate result, not proof of quality or transferred accountability.

The intended outcome is not fewer contributors. The intended outcome is better-prepared contributors, less wasted review time, and projects that can accept useful work without lowering their standards.
