#!/usr/bin/env python3
"""Validate portable skill eval case JSON files."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


VALID_TYPES = {
    "happy-path",
    "ambiguous-scope",
    "edge-case",
    "negative",
    "regression",
    "trigger",
}
VALID_SCOPES = {
    "agent-level",
    "component-level",
    "reference-retrieval",
    "artifact-review",
}
VALID_TRIGGER_EXPECTATIONS = {
    "explicit",
    "implicit",
    "contextual",
    "negative",
    "not-applicable",
}
VALID_GRADER_MODES = {
    "deterministic",
    "model-assisted",
    "human",
    "hybrid",
}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
LEAKY_PROMPT_RE = re.compile(
    r"check that|verify that|make sure it|ensure it|test whether|should not|must not|expected|regression",
    re.IGNORECASE,
)


def as_nonempty_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def validate_assertions(value, field: str, prefix: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if value is None:
        return errors, warnings
    if not isinstance(value, list):
        errors.append(f"{prefix}: {field} must be a list")
        return errors, warnings
    for assertion_index, assertion in enumerate(value, 1):
        assertion_prefix = f"{prefix}.{field}[{assertion_index}]"
        if not isinstance(assertion, dict):
            errors.append(f"{assertion_prefix}: assertion must be an object")
            continue
        assertion_type = str(assertion.get("type", "")).strip()
        if not assertion_type:
            errors.append(f"{assertion_prefix}: missing type")
        if field == "artifact_assertions" and assertion_type == "exists":
            if not str(assertion.get("path", "")).strip():
                errors.append(f"{assertion_prefix}: exists assertion requires path")
        if field == "trace_assertions" and assertion_type in {"skill_invoked", "command_contains", "tool_called"}:
            if not str(assertion.get("value", "")).strip():
                warnings.append(f"{assertion_prefix}: {assertion_type} usually needs value")
    return errors, warnings


def validate_grader(value, prefix: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if value is None:
        return errors, warnings
    if not isinstance(value, dict):
        errors.append(f"{prefix}: grader must be an object")
        return errors, warnings
    mode = str(value.get("mode", "")).strip()
    if mode not in VALID_GRADER_MODES:
        errors.append(f"{prefix}: grader.mode must be one of {', '.join(sorted(VALID_GRADER_MODES))}")
    threshold = value.get("threshold")
    if threshold is not None:
        if not isinstance(threshold, (int, float)):
            errors.append(f"{prefix}: grader.threshold must be a number from 0 to 1")
        elif threshold < 0 or threshold > 1:
            errors.append(f"{prefix}: grader.threshold must be from 0 to 1")
    if mode in {"model-assisted", "hybrid"} and not str(value.get("rubric", "")).strip():
        warnings.append(f"{prefix}: model-assisted graders should include rubric")
    return errors, warnings


def validate_eval_file(path: Path, strict_portable: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"Cannot read {path}: {exc}"], warnings
    except json.JSONDecodeError as exc:
        return [f"{path} is not valid JSON: {exc}"], warnings

    if not isinstance(payload, dict):
        return ["Top-level JSON must be an object"], warnings
    skill_name = str(payload.get("skill_name", "")).strip()
    if not skill_name:
        errors.append("Missing skill_name")
    evals = payload.get("evals")
    if not isinstance(evals, list) or not evals:
        errors.append("evals must be a non-empty list")
        return errors, warnings

    seen_ids: set[str] = set()
    has_regression = False
    for index, case in enumerate(evals, 1):
        prefix = f"evals[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object")
            continue
        case_id = str(case.get("id", "")).strip()
        if not case_id:
            errors.append(f"{prefix}: missing id")
        elif not ID_RE.match(case_id):
            errors.append(f"{prefix}: id must use lowercase letters, digits, '.', '_' or '-'")
        elif case_id in seen_ids:
            errors.append(f"{prefix}: duplicate id {case_id}")
        seen_ids.add(case_id)

        legacy_expectations = as_nonempty_list(case.get("expectations"))
        legacy_expected_output = str(case.get("expected_output", "")).strip()
        legacy_case = bool(legacy_expectations or legacy_expected_output)

        case_type = str(case.get("type", "")).strip()
        if case_type not in VALID_TYPES:
            if strict_portable or not legacy_case:
                errors.append(f"{prefix}: type must be one of {', '.join(sorted(VALID_TYPES))}")
            else:
                warnings.append(f"{prefix}: missing portable type; legacy eval assumed happy-path")
        if case_type == "regression":
            has_regression = True

        scope = str(case.get("scope", "")).strip()
        if scope and scope not in VALID_SCOPES:
            errors.append(f"{prefix}: scope must be one of {', '.join(sorted(VALID_SCOPES))}")
        elif strict_portable and not scope:
            errors.append(f"{prefix}: scope is required in strict portable mode")

        trigger_expectation = str(case.get("trigger_expectation", "")).strip()
        if trigger_expectation and trigger_expectation not in VALID_TRIGGER_EXPECTATIONS:
            errors.append(f"{prefix}: trigger_expectation must be one of {', '.join(sorted(VALID_TRIGGER_EXPECTATIONS))}")
        elif strict_portable and not trigger_expectation:
            errors.append(f"{prefix}: trigger_expectation is required in strict portable mode")

        tags = as_nonempty_list(case.get("tags"))
        if strict_portable and not tags:
            errors.append(f"{prefix}: tags must be a non-empty list in strict portable mode")

        prompt = str(case.get("prompt", "")).strip()
        if len(prompt) < 20:
            errors.append(f"{prefix}: prompt is too short to be realistic")
        if LEAKY_PROMPT_RE.search(prompt):
            warnings.append(f"{prefix}: prompt may leak evaluation intent; move expectations into must_do/must_not_do")

        must_do = as_nonempty_list(case.get("must_do"))
        must_not_do = as_nonempty_list(case.get("must_not_do"))
        success_evidence = as_nonempty_list(case.get("success_evidence"))
        if legacy_case and not must_do:
            must_do = legacy_expectations or ([legacy_expected_output] if legacy_expected_output else [])
            warnings.append(f"{prefix}: legacy expectations should be migrated to must_do assertions")
        if legacy_case and not success_evidence:
            success_evidence = legacy_expectations or ([legacy_expected_output] if legacy_expected_output else [])
            warnings.append(f"{prefix}: add explicit success_evidence for transcript/artifact checks")
        if not must_do:
            errors.append(f"{prefix}: must_do must be a non-empty list")
        if not must_not_do and (strict_portable or not legacy_case):
            errors.append(f"{prefix}: must_not_do must be a non-empty list")
        elif not must_not_do:
            warnings.append(f"{prefix}: add must_not_do assertions to catch shortcuts")
        if not success_evidence:
            errors.append(f"{prefix}: success_evidence must be a non-empty list")
        if not as_nonempty_list(case.get("required_artifacts")) and case_type not in {"trigger", "negative"}:
            warnings.append(f"{prefix}: required_artifacts is empty; ensure transcript-only evidence is intentional")

        assertion_errors, assertion_warnings = validate_assertions(case.get("trace_assertions"), "trace_assertions", prefix)
        errors.extend(assertion_errors)
        warnings.extend(assertion_warnings)
        assertion_errors, assertion_warnings = validate_assertions(case.get("artifact_assertions"), "artifact_assertions", prefix)
        errors.extend(assertion_errors)
        warnings.extend(assertion_warnings)

        grader = case.get("grader")
        grader_errors, grader_warnings = validate_grader(grader, prefix)
        errors.extend(grader_errors)
        warnings.extend(grader_warnings)
        if strict_portable and grader is None:
            errors.append(f"{prefix}: grader is required in strict portable mode")

        failure_categories = as_nonempty_list(case.get("failure_categories"))
        if strict_portable and not failure_categories:
            errors.append(f"{prefix}: failure_categories must be a non-empty list in strict portable mode")

    if not has_regression:
        warnings.append("No regression case found; add one when this eval set comes from a real failure")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill eval case JSON")
    parser.add_argument("eval_json", nargs="+", help="Eval case JSON file(s)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--strict-portable", action="store_true", help="Require the portable must_do/must_not_do/success_evidence schema")
    args = parser.parse_args()

    all_errors: list[str] = []
    all_warnings: list[str] = []
    results = []
    for raw_path in args.eval_json:
        path = Path(raw_path).expanduser().resolve()
        errors, warnings = validate_eval_file(path, strict_portable=args.strict_portable)
        all_errors.extend(f"{path}: {error}" for error in errors)
        all_warnings.extend(f"{path}: {warning}" for warning in warnings)
        results.append({"path": str(path), "errors": errors, "warnings": warnings})

    if args.json:
        print(json.dumps({"status": "fail" if all_errors else "pass", "results": results}, indent=2, ensure_ascii=False))
    else:
        print("Eval case check")
        print(f"Status: {'fail' if all_errors else 'pass'}")
        print(f"Errors: {len(all_errors)}")
        for error in all_errors:
            print(f"ERROR: {error}")
        print(f"Warnings: {len(all_warnings)}")
        for warning in all_warnings:
            print(f"WARN: {warning}")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
