# Security Static Analysis

Use this lens for security and control-plane safety. Scanner output is only a lead; submit only triaged Bugs.

## Checks

- AuthN/AuthZ: missing policy, tenant boundary bypass, role confusion.
- Injection: SQL/NoSQL/command/template/expression injection.
- Path/file: traversal, unsafe archive extraction, arbitrary read/write.
- Deserialization: `pickle`, `yaml.load`, `jsonpickle`, unsafe object decoding.
- TLS/crypto: `verify=False`, disabled cert checks, weak crypto, hardcoded secrets.
- SSRF/network: user-controlled URL, internal metadata access, unbounded outbound call.
- Secrets: tokens/passwords in repo, logs, config defaults, generated reports.
- Shell/process: `shell=True`, string command construction, temp shell files, unconsumed pipes.
- Resource abuse: unbounded payload, file read without size limit, QGA/QMP/libvirt unsafe operations.

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
