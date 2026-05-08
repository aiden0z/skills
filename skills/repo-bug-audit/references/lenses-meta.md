# Meta Lenses

Meta lenses are contrast scans applied after other lenses. They do not create separate Bug categories; they add discovery paths and priority context.

### META-1 Intent vs Implementation Drift

- **Hypothesis**: README, ADRs, specs, comments, and important commit messages describe behavior that the code still implements.
- **Where to look**: `Intent Inputs` in each repo profile; docstrings; TODO/FIXME/deprecated comments; commit messages that claim a fix.
- **Evidence pattern**: README says failures retry three times but code has no retry; ADR says outbox is used but no outbox path exists; commit says a guard was fixed but code still lacks it.
- **False-positive guard**: source is explicitly outdated; spec is in an open migration PR; renamed docs are stale but runtime behavior is correct.
- **Stop / Tiebreak**: cover profile-listed intent inputs and key commits. Classify discovered Bugs under L1-L19; `META-1` is discovery metadata.
- Example: ADR says all internal APIs require auth, but an internal endpoint has no guard.
- Counterexample: comment still says TODO, but code now has the fallback.

### META-2 Failure-Path Test Coverage

- **Hypothesis**: happy paths may be covered while error, edge, timeout, cancellation, and recovery paths are not.
- **Where to look**: `tests/`, coverage reports if present, `pytest.raises`, `assertThrows`, retry tests, modules touched by Tier 2/3 Bugs.
- **Evidence pattern**: function has happy-path tests but no failure tests; exception branch has no test; retry logic only tests first-attempt success.
- **False-positive guard**: integration or contract tests cover the failure path; path is deprecated and explicitly excluded.
- **Stop / Tiebreak**: cover core modules and modules affected by promoted Tier 2/3 Bugs. Do not submit "missing tests" directly as a Bug; record it as risk amplification in the relevant lens record.
- Example: L10 retry Bug priority increases because no failure-path test covers retry exhaustion.
- Counterexample: unit tests are absent but contract tests cover duplicate-message behavior.
