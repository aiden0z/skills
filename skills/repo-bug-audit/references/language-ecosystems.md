# Language Ecosystems

Use this after choosing the domain profile. This is an evidence checklist, not a language tutorial.

## Rules

- Inspect files and build metadata before deciding the language/framework.
- Prefer repository-declared commands over generic commands.
- Suggested verification commands must trace to real files: build config, package scripts, CI config, test files, Makefile, or existing scripts.
- If no trustworthy command is visible, write `未确认` / `not confirmed`; do not guess.
- Mixed repositories may use multiple rows. Record the ecosystem only when it changes evidence, fix boundary, or verification.

## Evidence Map

| Ecosystem | Evidence files | Entry points | Command sources | Extra risk signals |
|---|---|---|---|---|
| Python | `pyproject.toml`, `tox.ini`, `pytest.ini`, `requirements*.txt`, `manage.py` | views, services, tasks, CLIs, migrations | tox/pytest config, Makefile, CI, `tests/` | transaction gaps, broad exception swallowing, async retry drift |
| Node.js / TypeScript | `package.json`, lockfiles, `tsconfig.json`, framework config | routes, controllers, services, workers, API clients | package scripts, Jest/Vitest/Playwright config, CI | stale cache, missing auth gate, unbounded fetch/axios, SSR/client leaks |
| Java / Kotlin | `pom.xml`, `build.gradle`, `settings.gradle` | controllers, services, repositories, schedulers, consumers | Maven/Gradle tasks, JUnit config, CI | transaction propagation, executor leaks, missing timeout, auth annotation gaps |
| Go | `go.mod`, `go.work`, Makefile, CI | HTTP/gRPC handlers, services, stores, goroutines, CLIs | Makefile/CI `go test`, package tests | context gaps, goroutine/channel leaks, ignored errors, race/check-then-act |
| Rust | `Cargo.toml`, workspace manifests | handlers, services, async tasks, storage adapters | cargo tasks, CI | unsafe/unwrap on external data, lock across await, cancellation gaps |
| C / C++ | `CMakeLists.txt`, Makefile, build scripts | exported APIs, daemons, drivers, command handlers | CMake/Make targets, CI, test binaries | bounds errors, ownership/lifetime bugs, lock ordering, unchecked returns |
| C# / .NET | `.sln`, `.csproj`, `Directory.Build.props` | controllers, services, hosted workers, repositories | `dotnet test` targets, test projects, CI | cancellation ignored, disposal leaks, transaction scope drift |
| PHP / Ruby | `composer.json`, `Gemfile`, `Rakefile`, test config | controllers, services, jobs, commands, middleware | Composer/Rake/PHPUnit/RSpec/Minitest config, CI | auth middleware gaps, unsafe file/path handling, job idempotency |
| Frontend | `package.json`, framework/router/store files | routes, stores, mutation hooks, API clients, forms | package scripts, component/e2e configs, CI | permission display mismatch, stale server state, rollback gaps, client data leaks |
| Mobile | Gradle/Xcode project files, manifests | screens, view models, background jobs, sync workers, permission handlers | Gradle/Xcode test tasks, CI | weak-network recovery, duplicate submit, permission drift, lifecycle crashes |

## Command Rule

Use the most specific confirmed command: module test, package test, full CI/build test, lint/typecheck. A generic command such as `npm test`, `pytest`, `go test ./...`, `mvn test`, or `cargo test` is acceptable only when repository files make it credible; cite or name the evidence file in the Bug record.
