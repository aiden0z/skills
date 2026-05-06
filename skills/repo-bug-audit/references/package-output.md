# Package Output

## Contents

- Workspace Structure
- README Content
- Image Guidance
- Quality Scope
- Knowledge Quality

## Workspace Structure

```text
<project>-bug-audit/
├── submit/
│   ├── README.md
│   ├── audit-overview.png              # optional, compressed if included
│   ├── findings/
│   │   ├── P1/
│   │   ├── P2/
│   │   ├── P3/
│   │   └── P4/
│   ├── indexes/
│   │   ├── findings.generated.md
│   │   └── findings.generated.json
│   ├── knowledge/
│   │   ├── README.md
│   │   ├── system-overview.md
│   │   ├── architecture-design-review.md
│   │   ├── repo-relationship-map.md
│   │   ├── risk-paths.md
│   │   └── repo-profiles/
│   ├── quality/
│   │   ├── submission-scope.md
│   │   └── repository-versions.md
│   └── standards/
│       └── bug-report-standard.md
└── work/
    ├── candidates/
    ├── eval/
    ├── scanner-output/
    ├── drafts/
    └── tmp/
```

Only `submit/` should be zipped or sent as the final package. `work/` is for temporary analysis artifacts and must stay out of the submitted package.

Use platform-native archive commands when packaging: `zip` on Unix, Linux, and macOS; `Compress-Archive` on Windows PowerShell. See `cross-platform.md`.

## README Content

Include:

- One-paragraph scope summary.
- Optional embedded image: `![仓库 Bug 审计与架构风险总览](audit-overview.png)`.
- `分析信息`: date, analyst when provided, method, scope, status.
- Repository version evidence summary: branch/hash/dirty status coverage when available.
- Scope, collection standard, exclusion boundary, language.
- Summary counts by priority, confidence, category, impact domain, repo, and issue family.
- Main findings and architecture risk signals.
- File guide and reading order.
- Candidate handling and confidence threshold when applicable.
- Continuation notes when findings were downgraded, removed, merged, or promoted from candidates.
- Knowledge coverage: system overview, repo relationships, risk paths, architecture signals, and important repo profiles.
- Natural developer-facing wording without process narration, self-reference, or AI-flavored phrases.

## Image Guidance

If creating `audit-overview.png`, read `audit-overview-image.md`.

- Preferred mechanism: HTML/CSS rendered to PNG through browser screenshot.
- Infographic/design skills may guide layout and hierarchy.
- Native image generation is allowed when it produces a cleaner result, but must pass the same text, count, metadata, overlap, and clipping checks.
- Use white background, clear grid, safe margins, and no overlapping text.
- Prefer `16:10` (`1600x1000`) for audit package overview images. Use `16:9` (`1600x900` or `1920x1080`) when the primary target is PPTX, slide decks, or widescreen presentation export.
- Avoid long vertical overview images that become unreadable when previewed or embedded. If content does not fit, reduce overview content instead of increasing canvas height.
- When HTML/CSS is used, screenshot the final artboard only and make the HTML preview viewport-fit so common browser sizes show the complete artboard without scrolling or top-left cropping.
- Keep the final artboard, screenshot viewport, and submitted PNG on the same ratio. If a constrained preview such as `1600x1000` is the readable version, submit that size rather than a larger source canvas.
- Verify both the final PNG and a constrained browser preview, for example `1600x1000`; DOM overflow checks do not replace visual review.
- Show scope, counts, P1/P2 focus, risk families, architecture signals, file guide, and metadata.
- Build the image from an explicit source snapshot under `work/tmp/` or `work/drafts/`; every number and "top" ranking must trace back to indexes, README, repository version evidence, or submitted knowledge.
- Include version-evidence summary from `quality/repository-versions.md` when available.
- Use analyst only from explicit input or existing metadata; otherwise keep the README placeholder and do not infer identity.
- Use discovery wording, not command-style principles.
- Avoid AI-flavored, process-oriented, or audience-explaining wording.
- Compress PNG without hurting text legibility; target <500KB by default, and <200KB only when practical.
- Avoid unused backup images. Keep zip packages small; target <2MB when practical.
- If image generation needs intermediate prompts, source notes, or tool-specific files, keep them under `work/tmp/` or `work/drafts/`, not under `submit/`.

## Quality Scope

`quality/submission-scope.md` should state:

- `status=open`, `source=static-analysis`.
- Confidence threshold.
- Excluded low-confidence leads.
- Downgrade, removal, merge, and candidate-promotion notes from continuation runs.
- Evaluation notes: priority calibration, issue-family samples, weak high-risk areas, and unreviewed exclusions when applicable.
- Runtime validation still belongs to developers/test owners.
- No SLA fields in Bug records unless requested.

`quality/repository-versions.md` should state:

- Repository name.
- Role: target or reference.
- Branch when available.
- Commit hash when available.
- Dirty status when available.
- Notes for unknown, detached, shallow, exported, or non-Git sources.

## Knowledge Quality

Before packaging, check `knowledge-base.md`.

- `submit/knowledge/` should be complete enough for another Agent to continue analysis or start fixes without rescanning basics.
- Knowledge should reflect submitted Bugs and repeated issue families, not only initial inventory.
- Cross-repo relationship maps should explain the risk paths used by submitted findings.
- Empty, stale, or repetitive optional knowledge files should be removed.
- Run `evaluation.md` before final packaging; keep temporary eval notes in `work/eval/` unless they affect submission scope.
- For large or multi-repo packages, run `validate_bug_package.py --require-knowledge`.
- When `audit-overview.png` is expected, run `validate_bug_package.py --require-image` too.
