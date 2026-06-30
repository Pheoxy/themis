# Security Test Fixtures

Themis includes a small number of synthetic secret-like strings in tests so redaction behavior can be verified. These values are not credentials and must not use real token formats such as GitHub, OpenAI, AWS, npm, Slack, or Stripe keys.

Approved synthetic secret fixtures:

- `generic-secret-assignment:tests/test_providers.py:122`
- `generic-secret-assignment:tests/test_providers.py:130`
- `generic-secret-assignment:tests/test_providers.py:141`

Rules for adding or changing fixtures:

- Use obviously fake values only.
- Keep values scoped to tests.
- Do not use real provider token formats.
- Add every expected scanner hit to the approved fixture list above.
- Run `nix run . -- release audit --history` before committing.

The release audit passes approved fixtures but fails on any unapproved secret-like value.
