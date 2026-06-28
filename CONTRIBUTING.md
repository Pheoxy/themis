# Contributing

This project exists to protect upstream maintainers from low-confidence AI-assisted submissions. Contributions must therefore meet a stricter standard than ordinary local tooling.

Required for every code change:

- Run the unit tests and include exact test evidence in the PR.
- Add or update tests with behavior changes.
- Keep changes small enough for maintainers to review without reconstructing intent.
- Do not include generated, vendored, minified, binary, placeholder, debug, or speculative code unless a maintainer explicitly requested it.
- If AI assistance was used, disclose it in the PR and include a human accountability statement.
- Sign off commits with `Signed-off-by:` to document responsibility for the submitted work.

The validator must fail closed when it cannot prove a submission follows upstream rules.
