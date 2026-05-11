# Security Static Analysis

Use this lens for security and control-plane safety. Scanner output is only a lead; submit only triaged Bugs.

## Checks

- Authentication and authorization enforcement across all entry points
- Injection vectors where external input reaches interpreters
- Path and file operations where user input constructs filesystem locations
- Deserialization and data format parsing at trust boundaries
- TLS configuration and certificate validation on all outbound connections
- Secrets handling: storage, exposure in logs/configs, encryption key management
- Network call construction where URLs or hosts come from external input
- Process and command execution boundaries
- Resource limits on uploads, payloads, and external data ingestion

## Tool Ideas

Use available tools when present:

- Semgrep for pattern-based checks.
- CodeQL for language-aware dataflow queries.
- Gitleaks/trufflehog for secrets.
- Bandit for Python security anti-patterns.
- npm/pip/audit tools for dependency risks.

Do not force-install tools unless the user allows it.

## False-positive Gates

Before submitting a security Bug, check:

- Is the input attacker/user-controlled?
- Is there a trust boundary crossing?
- Is the code reachable in production or privileged ops?
- Does another layer sanitize, authorize, or constrain it?
- What is the realistic impact: data exposure, tenant escape, command execution, control-plane compromise, DoS?

If reachability is unclear, mark confidence `medium` or keep as candidate.
