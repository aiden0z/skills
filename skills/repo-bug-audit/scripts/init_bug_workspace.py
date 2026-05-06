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
- 收录标准：`status=open` 且 `confidence=high` 优先进入提交包，`confidence=medium/low` 留在 `../work/candidates/` 或明确标注。
- 排除范围：候选线索、低置信记录、仍需故障注入确认的问题，不进入正式提交包。
- 文档语言：中文。

## 总览

运行 `scripts/generate_bug_index.py` 后更新本节。

## 文件说明

- `findings/`：按 P1/P2/P3/P4 分组的 Bug 明细。
- `indexes/`：自动生成的索引和结构化摘要。
- `knowledge/`：系统概览、仓库关系、风险路径和架构风险分析。
- `quality/submission-scope.md`：收录口径、排除边界和质量门禁。
- `standards/bug-report-standard.md`：Bug 描述规范。

临时评估记录可放在 `../work/eval/`，不进入提交包。
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
- Inclusion: `status=open` and `confidence=high` should enter the submission package first; `confidence=medium/low` belongs in `../work/candidates/` or must be clearly marked.
- Exclusion: leads without code evidence, low-confidence records, and issues requiring fault-injection proof should not enter the final submission package.
- Language: English.

## Overview

Run `scripts/generate_bug_index.py` and update this section.

## Files

- `findings/`: Bug records grouped by P1/P2/P3/P4.
- `indexes/`: generated indexes and structured summaries.
- `knowledge/`: system overview, repository relationships, risk paths, and architecture risk review.
- `quality/submission-scope.md`: inclusion rules, exclusion boundaries, and quality gates.
- `standards/bug-report-standard.md`: Bug report standard.

Temporary evaluation notes can live in `../work/eval/`; keep them out of the submission package.
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
        "work/candidates", "work/eval", "work/scanner-output", "work/drafts", "work/tmp",
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

必需字段：`id`、`priority`、`confidence`、`status`、`source`、`repo`、`module`、`category`、`issue_family`、`infra_domains`。

必需章节：结论、影响范围、前置条件、静态复现路径、实际表现、期望表现、代码证据、误报排查、修复建议、验证标准。

不写 SLA 字段；修复周期属于后续排期，不属于静态分析发现阶段。

正文只写结论、证据、影响、误报排查、修复建议和验证标准，不写分析过程、自我说明或受众说明。
"""
        quality = f"""# {args.project} Bug 提交口径

## 审计元信息

- 分析人：`{analyst_value}`
- 分析方法：`静态分析`

## 收录

- `source=static-analysis`
- `status=open`
- `confidence=high` 优先进入提交包。
- `confidence=medium/low` 留在 `../work/candidates/` 或在记录中明确标注。

## 排除

- 无代码证据的纯猜测。
- 无可解释触发路径的扫描器原始告警。
- 已被上层统一封装、配置或测试证明不可达的问题。

## 质量评估

- P1/P2 已按证据、优先级和误报排查重新检查：`待评估`
- 问题族抽样、风险域覆盖和浅层模式占比：`待评估`
- 重要降级、移除、合并或未覆盖高风险区域：`暂无`

## 当前状态

`{args.status}`。

## 续跑记录

- 暂无。
"""
        versions = f"""# {args.project} 仓库版本凭证

| 仓库 | 角色 | 分支 | Commit | 工作区状态 | 备注 |
|---|---|---|---|---|---|
| `{args.scope}` | target | `待采集` | `待采集` | `待采集` | 初始化占位，提交前更新。 |

## 口径

- 能采集则记录分支、commit hash 和工作区状态。
- 无法采集时写 `unknown`，并在备注说明原因。
- 不猜测缺失的版本信息。
"""
        candidates = """# 候选线索

候选线索用于记录暂不进入提交包的问题。每条线索建议单独一个 Markdown 文件。

```markdown
# <标题>

- 位置：`repo/path/file.ext:line`
- 疑点：<代码呈现出的风险>
- 未提交原因：<缺少的关键证据，或可能误报的地方>
- 升级所需证据：<需要继续确认的入口、配置、调用链、测试、日志或运行条件>
```
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
"""
    else:
        status = "pending developer review" if args.status == "待开发复核" else args.status
        args.status = status
        analyst_value = args.analyst if args.analyst else "not specified"
        analyst_line = f"- Analyst: `{args.analyst}`\n" if args.analyst else "- Analyst: `not specified`\n"
        readme = en_readme(args, domain_summary, analyst_line)
        standard = """# Bug Report Standard

Use one Markdown file per Bug and keep metadata in the file frontmatter. Do not create separate YAML files.

Required fields: `id`, `priority`, `confidence`, `status`, `source`, `repo`, `module`, `category`, `issue_family`, `infra_domains`.

Required sections: conclusion, scope, preconditions, static reproduction path, actual behavior, expected behavior, code evidence, false-positive review, fix suggestion, validation standard.

Do not add SLA fields. Fix timeline belongs to later planning, not static discovery.

Write conclusions, evidence, impact, false-positive review, fix suggestions, and validation standards. Do not include process narration, self-reference, or audience explanation.
"""
        quality = f"""# {args.project} Bug Submission Scope

## Audit Metadata

- Analyst: `{analyst_value}`
- Method: `static-analysis`

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

## Current Status

`{args.status}`.

## Continuation Notes

- None.
"""
        versions = f"""# {args.project} Repository Version Evidence

| Repository | Role | Branch | Commit | Dirty | Notes |
|---|---|---|---|---|---|
| `{args.scope}` | target | `pending` | `pending` | `pending` | Starter placeholder; update before final submission. |

## Scope

- Record branch, commit hash, and dirty status when available.
- Use `unknown` when evidence is unavailable, and explain why in Notes.
- Do not guess missing version information.
"""
        candidates = """# Candidate Leads

Candidate leads are plausible issues that are not ready for the submitted package. Prefer one Markdown file per lead.

```markdown
# <Title>

- Location: `repo/path/file.ext:line`
- Suspicion: <risk shown by code>
- Not submitted because: <missing evidence or possible false-positive reason>
- Evidence needed for promotion: <entry point, config, call chain, test, log, or runtime condition to verify>
```
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
"""

    write_if_missing(root / "submit/README.md", readme, args.force)
    write_if_missing(root / "submit/standards/bug-report-standard.md", standard, args.force)
    write_if_missing(root / "submit/quality/submission-scope.md", quality, args.force)
    write_if_missing(root / "submit/quality/repository-versions.md", versions, args.force)
    write_if_missing(root / "submit/knowledge/README.md", knowledge, args.force)
    write_if_missing(root / "work/candidates/README.md", candidates, args.force)

    print(f"Initialized repository Bug audit workspace: {root}")
    print(f"Submission package root: {root / 'submit'}")
    print(f"Temporary work root: {root / 'work'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
