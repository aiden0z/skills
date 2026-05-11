#!/usr/bin/env python3
"""Create a repository Bug audit workspace."""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

DOMAIN_SUMMARY = {
    "zh": {
        "infra": "重点覆盖稳定性、数据一致性、恢复能力、存储/网络性能、安全边界和跨系统状态收敛。",
        "backend": "重点覆盖核心接口、数据一致性、任务处理、外部依赖、安全边界和故障恢复。",
        "frontend": "重点覆盖核心交互、状态一致性、权限边界、数据展示、性能退化和错误恢复。",
        "sdk": "重点覆盖 API 兼容性、错误处理、边界条件、并发安全、资源释放和依赖安全。",
        "mobile": "重点覆盖核心流程、离线/弱网恢复、权限边界、数据一致性、性能和崩溃风险。",
        "generic": "重点覆盖核心流程、数据安全、错误恢复、安全边界、性能退化和可维护性风险。",
    },
    "en": {
        "infra": "stability, data consistency, recovery, storage/network performance, security boundaries, and cross-system convergence.",
        "backend": "core APIs, data consistency, job processing, external dependencies, security boundaries, and failure recovery.",
        "frontend": "core user flows, state consistency, authorization boundaries, data display, performance degradation, and error recovery.",
        "sdk": "API compatibility, error handling, edge cases, concurrency safety, resource cleanup, and dependency security.",
        "mobile": "core flows, offline/weak-network recovery, permission boundaries, data consistency, performance, and crash risk.",
        "generic": "core workflows, data safety, error recovery, security boundaries, performance degradation, and maintainability risk.",
    },
}


def write_if_missing(path: Path, content: str, force: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


def zh_readme(args, domain_summary: str, analyst_line: str) -> str:
    return f"""# {args.project} 仓库 Bug 审计包

{args.project} 仓库 Bug 审计清单。{domain_summary}

## 分析信息

- 分析时间：`{args.date}`
{analyst_line}- 分析方法：`静态分析`
- 分析范围：`{args.scope}`
- 当前状态：`{args.status}`
- 版本凭证：见 `quality/repository-versions.md`

## 范围

- 代码范围：`{args.scope}`。
- 收录标准：`status=open` 且 `confidence=high` 优先进入审计交付物，`confidence=medium/low` 留在 `../work/candidates/` 或明确标注。
- 排除范围：候选线索、低置信记录、仍需故障注入确认的问题，不进入正式审计交付物。
- 文档语言：中文。

## 总览

运行 `scripts/generate_bug_index.py` 后更新本节。

## 文件说明

- `findings/`：按 P1/P2/P3/P4 分组的 Bug 明细。
- `indexes/`：自动生成的索引和结构化摘要。
- `knowledge/`：系统概览、仓库关系、风险路径和架构风险分析。
- `quality/submission-scope.md`：收录口径、排除边界和质量门禁。
- `quality/lens-coverage.md`：已启用 lens、扫描入口、候选数、排除原因和未覆盖区域。
- `quality/issue-family-coverage.md`：首次/独立扫描的问题家族覆盖矩阵。
- `standards/bug-report-standard.md`：Bug 描述规范。
- `bug-audit-report.html`：最终交付默认生成的交互式报告，生成后用浏览器打开。

临时评估记录可放在 `../work/eval/`，不进入审计交付物。
"""


def en_readme(args, domain_summary: str, analyst_line: str) -> str:
    return f"""# {args.project} Bug Audit Package

Bug audit findings for {args.project}. Focus: {domain_summary}

## Analysis Information

- Analysis date: `{args.date}`
{analyst_line}- Method: `static-analysis`
- Scope: `{args.scope}`
- Status: `{args.status}`
- Version evidence: see `quality/repository-versions.md`

## Scope

- Code scope: `{args.scope}`.
- Inclusion: `status=open` and `confidence=high` should enter the audit output first; `confidence=medium/low` belongs in `../work/candidates/` or must be clearly marked.
- Exclusion: leads without code evidence, low-confidence records, and issues requiring fault-injection proof should not enter the final audit output.
- Language: English.

## Overview

Run `scripts/generate_bug_index.py` and update this section.

## Files

- `findings/`: Bug records grouped by P1/P2/P3/P4.
- `indexes/`: generated indexes and structured summaries.
- `knowledge/`: system overview, repository relationships, risk paths, and architecture risk review.
- `quality/submission-scope.md`: inclusion rules, exclusion boundaries, and quality gates.
- `quality/lens-coverage.md`: enabled lens, scanned entry points, candidate counts, exclusions, and uncovered areas.
- `quality/issue-family-coverage.md`: fresh-run issue-family coverage matrix.
- `standards/bug-report-standard.md`: Bug report standard.
- `bug-audit-report.html`: default interactive report for final handoff packages, openable in a browser after generation.

Temporary evaluation notes can live in `../work/eval/`; keep them out of the audit output.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a repository Bug audit workspace")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("--project", default="Project", help="Project display name")
    parser.add_argument("--scope", default="target repositories", help="Analysis scope")
    parser.add_argument("--analyst", default="", help="Analyst name; leave empty to mark it missing")
    parser.add_argument("--date", default=date.today().isoformat(), help="Analysis date")
    parser.add_argument("--status", default="待开发复核", help="Current status")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="Template language")
    parser.add_argument(
        "--domain-profile",
        choices=sorted(DOMAIN_SUMMARY["zh"]),
        default="infra",
        help="Risk profile used by the starter README",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing template docs")
    args = parser.parse_args()

    root = Path(args.output).expanduser().resolve()
    dirs = [
        "submit/findings/P1", "submit/findings/P2", "submit/findings/P3", "submit/findings/P4",
        "submit/indexes", "submit/knowledge/repo-profiles", "submit/quality", "submit/standards",
        "work/candidates", "work/eval", "work/scanner-output", "work/shards", "work/drafts", "work/tmp",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)

    domain_summary = DOMAIN_SUMMARY[args.language][args.domain_profile]
    if args.language == "zh":
        analyst_value = args.analyst if args.analyst else "待补充"
        analyst_line = f"- 分析人：`{args.analyst}`\n" if args.analyst else "- 分析人：`待补充`\n"
        readme = zh_readme(args, domain_summary, analyst_line)
        standard = """# Bug 记录标准

每条 Bug 使用一个 Markdown 文件，并在文件顶部写入元信息。不得使用单独 YAML 文件。

必需字段：`id`、`priority`、`confidence`、`status`、`source`、`repo`、`module`、`category`、`issue_family`、`infra_domains`、`fix_risk`。

必需章节：结论、影响范围、前置条件、静态复现路径、实际表现、期望表现、代码证据、误报排查、修复边界、修复建议、建议验证命令、验证标准。

不写 SLA 字段；修复周期属于后续排期，不属于静态分析发现阶段。

正文只写结论、证据、影响、误报排查、修复边界、修复建议、建议验证命令和验证标准，不写分析过程、自我说明或受众说明。
建议验证命令必须能追溯到仓库文件；找不到可信命令时写“未确认”，不要编造。
"""
        quality = f"""# {args.project} Bug 提交口径

## 审计元信息

- 分析人：`{analyst_value}`
- 分析方法：`静态分析`
- 审计深度意图：`待确认`

## 收录

- `source=static-analysis`
- `status=open`
- `confidence=high` 优先进入审计交付物。
- `confidence=medium/low` 留在 `../work/candidates/` 或在记录中明确标注。

## 排除

- 无代码证据的纯猜测。
- 无可解释触发路径的扫描器原始告警。
- 已被上层统一封装、配置或测试证明不可达的问题。

## 质量评估

- P1/P2 已按证据、优先级和误报排查重新检查：`待评估`
- 问题族抽样、风险域覆盖和浅层模式占比：`待评估`
- 重要降级、移除、合并或未覆盖高风险区域：`暂无`

## Lens 覆盖

- 默认策略：适用的 13 个架构边界 + META；不适用的边界记录原因，不强行造候选。
- 覆盖记录：见 `quality/lens-coverage.md`。

## 交互式报告

- HTML 报告：最终交付默认生成；轻量扫描或用户明确要求无 HTML 时可省略。
- 默认生成文件为 `bug-audit-report.html`，并使用 `validate_bug_package.py --require-html-report` 验证。
- audit-overview.png：`deferred-post-handoff`。启动时只提示可选；若用户未明确要求或拒绝，最终交付后再询问是否补充。

## 当前状态

`{args.status}`。

## 续跑记录

- 暂无。
"""
        versions = f"""# {args.project} 仓库版本凭证

| 仓库 | 角色 | 审计分支 | Commit | 工作区状态 | 默认分支 | 稳定候选分支 | 候选置信度 | 证据 | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| `{args.scope}` | target | `待采集` | `待采集` | `待采集` | `待采集` | `unknown` | `unknown` | `待采集` | 初始化占位，提交前更新。 |

## 口径

- 能采集则记录审计分支、commit hash、工作区状态、默认分支和稳定候选分支。
- 交互模式下，如果用户没有明确指定分支，先确认审计分支基准；自动模式不切分支，只记录假设。
- 无法采集时写 `unknown`，并在备注说明原因。
- 不猜测缺失的版本信息，也不把版本号看起来最大的分支直接当成稳定分支。
"""
        lens_coverage = """# Lens 覆盖记录

按 `references/exploration-lenses.md` 填写。边界是思考框架，不是固定 Bug checklist；无候选时记录 refuted / not-applicable / uncovered 原因。

```markdown
### Boundary: API Contract

- 已扫描：<真实路径、入口或服务间契约>
- 候选：0
- 已排除：<被 guard / sibling / shared library 排除的线索>
- 未覆盖：<真实未覆盖区域>
```
"""
        issue_family_coverage = """# 问题家族覆盖

来源：fresh-run current-source scan（首次/独立扫描），不是历史包复用。

| Family | Fresh Sources | Outcome | Evidence |
|---|---|---|---|
| `<LLM-declared-family>` | <代码理解、agent gap、补盲扫描或人工追踪来源> | <outcome> | <代码锚点、BUG ID 或 no-hit 说明> |

允许 outcome：`promoted`、`merged`、`parked`、`refuted`、`no-hit`、`not-applicable`、`out-of-scope`。
不要从模板复制固定家族；按本次仓库真实风险面和 gap analysis 填写。
"""
        candidates = """# 候选线索

候选线索用于记录暂不进入审计交付物的问题。每条线索建议单独一个 Markdown 文件。

```markdown
- C1 | P2 | outcome=parked | bug_gate=missing | missing_gate=trigger-path | `repo/path/file.ext:line` | <短疑点>
- C2 | P3 | outcome=promoted | bug_gate=complete | BUG-0017 | `repo/path/file.ext:line` | <短标题>
```

如果线索已经 `bug_gate=complete`，最终验证前必须提交为 Bug 或合并到已提交 Bug。
"""
        knowledge_capture = """# 探索知识捕获

按 `references/knowledge-capture.md` 记录探索中形成、之后可复用的仓库认知。这里是 scratch ledger，不直接进入最终交付物。

```markdown
### <repo> / <topic>

- Type: entry-point | boundary | state-owner | lifecycle | invariant | false-positive-guard | verification-source | cross-repo-contract | risk-path | uncovered-area
- Evidence: `path/to/file.ext:line` 或命令来源
- Learned: <一个可复用事实>
- Reuse Target: repo-profile | system-overview | repo-relationship-map | risk-paths | architecture-design-review | lens-coverage | candidate
- Status: promote | parked | refuted
```

最终打包前，把有证据的 atom 提升到 `submit/knowledge/`，推测性内容留在 `work/`。
"""
        knowledge = f"""# {args.project} 知识入口

## 文件

- `system-overview.md`：系统范围、模块边界和核心流程。
- `architecture-design-review.md`：架构风险信号和重复问题族。
- `repo-relationship-map.md`：仓库与外部系统关系。
- `risk-paths.md`：典型故障传播路径。
- `repo-profiles/`：核心仓库画像。

## 口径

知识库先形成最小底图，再随 Bug 证据持续补充。最终提交版本应能支持后续复核、继续分析和修复定位。
记录主要语言生态、构建文件、测试命令来源和未确认的验证命令缺口。
"""
        profile_template = """# Repo Profile Template

每个审计仓库创建一个独立 profile。`org/repo` 使用 `org__repo.md`。

```markdown
# <repo-name> Profile

## Tech Stack
## Entry Points
## Outbound Calls
## Inbound Endpoints
## Shared Events
## Shared Storage
## Shared Config
## Intent Inputs
## Verification Sources
## Risk Surfaces
## Call Graph
## Findings and Candidates
## Known Uncovered Areas
```

要求见 skill 的 `references/repo-profile.md`。所有路径、命令、入口和 Bug ID 必须真实；不确定处写 `unconfirmed` / `未确认`。
"""
    else:
        status = "pending developer review" if args.status == "待开发复核" else args.status
        args.status = status
        analyst_value = args.analyst if args.analyst else "not specified"
        analyst_line = f"- Analyst: `{args.analyst}`\n" if args.analyst else "- Analyst: `not specified`\n"
        readme = en_readme(args, domain_summary, analyst_line)
        standard = """# Bug Report Standard

Use one Markdown file per Bug and keep metadata in the file frontmatter. Do not create separate YAML files.

Required fields: `id`, `priority`, `confidence`, `status`, `source`, `repo`, `module`, `category`, `issue_family`, `infra_domains`, `fix_risk`.

Required sections: conclusion, scope, preconditions, static reproduction path, actual behavior, expected behavior, code evidence, false-positive review, fix boundary, fix suggestion, suggested verification commands, validation standard.

Do not add SLA fields. Fix timeline belongs to later planning, not static discovery.

Write conclusions, evidence, impact, false-positive review, fix boundaries, fix suggestions, suggested verification commands, and validation standards. Do not include process narration, self-reference, or audience explanation.
Suggested verification commands must trace to repository files. If no reliable command is visible, mark the command as not confirmed instead of guessing.
"""
        quality = f"""# {args.project} Bug Submission Scope

## Audit Metadata

- Analyst: `{analyst_value}`
- Method: `static-analysis`
- Audit depth intent: `pending`

## Included

- `source=static-analysis`
- `status=open`
- `confidence=high` should enter submitted findings first.
- `confidence=medium/low` belongs in `../work/candidates/` or must be clearly marked.

## Excluded

- Speculation without code evidence.
- Raw scanner alerts without an explainable trigger path.
- Findings proven unreachable by shared wrappers, configuration, or tests.

## Evaluation

- P1/P2 evidence, priority, and false-positive gates: `pending`
- Issue-family sampling, risk-domain coverage, and shallow-pattern concentration: `pending`
- Material downgrades, removals, merges, or unreviewed high-risk areas: `none`

## Lens Coverage

- Default strategy: applicable 13 architecture boundaries + META; record why non-applicable boundaries were skipped instead of inventing candidates.
- Coverage record: see `quality/lens-coverage.md`.

## Interactive Report

- HTML report: generated by default for final handoff; omit only for lightweight scans or explicit no-HTML requests.
- Default output is `bug-audit-report.html`; validate with `validate_bug_package.py --require-html-report`.
- audit-overview.png: `deferred-post-handoff`. Mention the option at kickoff without blocking; if the user has not requested or declined it, ask after the validated handoff.

## Current Status

`{args.status}`.

## Continuation Notes

- None.
"""
        versions = f"""# {args.project} Repository Version Evidence

| Repository | Role | Audit Branch | Commit | Dirty | Default Branch | Stable Candidate | Candidate Confidence | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `{args.scope}` | target | `pending` | `pending` | `pending` | `pending` | `unknown` | `unknown` | `pending` | Starter placeholder; update before final audit output. |

## Scope

- Record audit branch, commit hash, dirty status, default branch, and stable branch candidate when available.
- In interactive mode, confirm the audit branch baseline when the user did not specify branches. In automatic mode, do not switch branches; record the assumption.
- Use `unknown` when evidence is unavailable, and explain why in Notes.
- Do not guess missing version information or treat the highest-looking version as stable without evidence.
"""
        lens_coverage = """# Lens Coverage

Fill this per `references/exploration-lenses.md`. Boundaries are thinking frames, not a fixed Bug checklist; zero-candidate records should explain refuted, not-applicable, or uncovered areas.

```markdown
### Boundary: API Contract

- Scanned: <real paths, entry points, or service contracts>
- Candidates: 0
- Refuted: <lead refuted by guard / sibling / shared library>
- Uncovered: <real uncovered area>
```
"""
        issue_family_coverage = """# Issue Family Coverage

Source: fresh-run current-source scan, not historical package reuse.

| Family | Fresh Sources | Outcome | Evidence |
|---|---|---|---|
| `<LLM-declared-family>` | <code understanding, agent gap, supplemental scan, or manual trace source> | <outcome> | <code anchor, BUG id, or no-hit explanation> |

Allowed outcomes: `promoted`, `merged`, `parked`, `refuted`, `no-hit`, `not-applicable`, `out-of-scope`.
Do not copy a fixed family list from the template; choose families from this audit's real risk surfaces and gap analysis.
"""
        candidates = """# Candidate Leads

Candidate leads are plausible issues that are not ready for the audit output. Prefer one Markdown file per lead.

```markdown
- C1 | P2 | outcome=parked | bug_gate=missing | missing_gate=trigger-path | `repo/path/file.ext:line` | <short suspicion>
- C2 | P3 | outcome=promoted | bug_gate=complete | BUG-0017 | `repo/path/file.ext:line` | <short title>
```

If a lead has `bug_gate=complete`, promote it or merge it into a submitted Bug before final validation.
"""
        knowledge_capture = """# Exploration Knowledge Capture

Use this scratch ledger per `references/knowledge-capture.md` to record reusable repo cognition learned during exploration. Do not copy raw notes directly into final deliverables.

```markdown
### <repo> / <topic>

- Type: entry-point | boundary | state-owner | lifecycle | invariant | false-positive-guard | verification-source | cross-repo-contract | risk-path | uncovered-area
- Evidence: `path/to/file.ext:line` or command source
- Learned: <one reusable fact>
- Reuse Target: repo-profile | system-overview | repo-relationship-map | risk-paths | architecture-design-review | lens-coverage | candidate
- Status: promote | parked | refuted
```

Before packaging, promote evidence-backed atoms into `submit/knowledge/`; leave speculative content in `work/`.
"""
        knowledge = f"""# {args.project} Knowledge Entry

## Files

- `system-overview.md`: system scope, module boundaries, and core workflows.
- `architecture-design-review.md`: architecture risk signals and repeated issue families.
- `repo-relationship-map.md`: repository and external-system relationships.
- `risk-paths.md`: representative failure propagation paths.
- `repo-profiles/`: core repository profiles.

## Scope

Build a minimal map first, then enrich knowledge as Bug evidence accumulates. The final submitted knowledge should support later review, continued analysis, and fix planning.
Record primary language ecosystems, build files, test command sources, and unconfirmed verification command gaps.
"""
        profile_template = """# Repo Profile Template

Create one profile per audited repository. Use `org__repo.md` for `org/repo`.

```markdown
# <repo-name> Profile

## Tech Stack
## Entry Points
## Outbound Calls
## Inbound Endpoints
## Shared Events
## Shared Storage
## Shared Config
## Intent Inputs
## Verification Sources
## Risk Surfaces
## Call Graph
## Findings and Candidates
## Known Uncovered Areas
```

See `references/repo-profile.md` in the skill. Every path, command, entry point, and Bug ID must be real; mark unknowns as `unconfirmed`.
"""

    write_if_missing(root / "work/drafts/readme-draft.md", readme, args.force)
    write_if_missing(root / "submit/standards/bug-report-standard.md", standard, args.force)
    write_if_missing(root / "submit/quality/submission-scope.md", quality, args.force)
    write_if_missing(root / "submit/quality/repository-versions.md", versions, args.force)
    write_if_missing(root / "submit/quality/lens-coverage.md", lens_coverage, args.force)
    write_if_missing(root / "submit/quality/issue-family-coverage.md", issue_family_coverage, args.force)
    write_if_missing(root / "submit/knowledge/README.md", knowledge, args.force)
    write_if_missing(root / "submit/knowledge/repo-profiles/README.md", profile_template, args.force)
    write_if_missing(root / "work/candidates/README.md", candidates, args.force)
    write_if_missing(root / "work/drafts/knowledge-capture.md", knowledge_capture, args.force)

    print(f"Initialized repository Bug audit workspace: {root}")
    print(f"Audit output root: {root / 'submit'}")
    print(f"Temporary work root: {root / 'work'}")
    print("Starter README draft: work/drafts/readme-draft.md (promote to submit/README.md only after shard validation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
