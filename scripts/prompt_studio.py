#!/usr/bin/env python3
"""Offline prompt composer and capability router. No image I/O or provider calls."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAP_KEYS = ("inspect_inputs", "reference_edit", "inspect_outputs")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def checked_bool(data, key):
    value = data.get(key, False)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a JSON boolean, not a string or number")
    return value


def positive_int(data, key, default, maximum):
    value = data.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValueError(f"{key} must be an integer from 1 to {maximum}")
    return value


def optional_text(data, key, default):
    value = data.get(key, default)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value.strip()


def compose(request, capabilities):
    if not isinstance(request, dict) or not isinstance(capabilities, dict):
        raise ValueError("request and capabilities must be JSON objects")
    catalog = load_json(ROOT / "styles/presets.json")
    style_id = request.get("style", catalog["default"])
    if not isinstance(style_id, str) or style_id not in catalog["presets"]:
        raise ValueError("Unknown style; use --list-styles")
    flags = {key: checked_bool(capabilities, key) for key in CAP_KEYS}
    if any(flags.values()):
        optional_text(capabilities, "evidence", "")
    if flags["reference_edit"]:
        optional_text(capabilities, "tool", "")
    reviewed = checked_bool(request, "source_reviewed")
    consent = checked_bool(request, "provider_processing_authorized")
    references = request.get("references", [])
    if not isinstance(references, list) or any(not isinstance(x, str) or not x.strip() for x in references):
        raise ValueError("references must be a list of nonempty attachment labels")
    if reviewed and (not references or not flags["inspect_inputs"]):
        raise ValueError("source_reviewed requires accessible references and input vision capability")
    candidates = positive_int(request, "candidate_count", 3, 3)
    max_calls = positive_int(request, "max_tool_calls", 5, 5)
    initial_calls = min(candidates, max_calls)
    repair_calls = min(2, max_calls - initial_calls)
    if not references:
        mode, status = "needs-reference", "no-reference-attached"
    elif not flags["inspect_inputs"]:
        mode, status = "text-template", "source-not-visually-inspected"
    elif not reviewed:
        mode, status = "prompt-studio", "awaiting-source-review"
    elif not flags["reference_edit"]:
        mode, status = "prompt-studio", "prompt-only"
    elif not consent:
        mode, status = "prompt-studio", "awaiting-provider-authorization"
    elif not flags["inspect_outputs"]:
        mode, status = "image-edit-unreviewed", "plan-only-output-review-unavailable"
    else:
        mode, status = "image-edit", "plan-only"
    identity = (
        optional_text(request, "identity_notes", "")
        if reviewed else
        "The source has NOT been visually inspected. The image editor must use the attached original as the identity reference. Do not treat this template as an analysis of the person."
    )
    preferences = optional_text(request, "preferences", "Use the selected preset; preserve requested identity features and clothing accommodations.")
    preset = catalog["presets"][style_id]
    negative = (ROOT / "prompts/negative.txt").read_text(encoding="utf-8").strip()
    template = (ROOT / "prompts/edit-template.txt").read_text(encoding="utf-8")
    prompt = template.format(identity_notes=identity, style_direction=preset["direction"], preferences=preferences, negative_constraints=negative).strip()
    styles = [style_id] * min(2, candidates)
    if candidates == 3:
        styles.append(preset["adjacent"])
    variants = []
    for index, candidate_style in enumerate(styles[:initial_calls]):
        direction = catalog["presets"][candidate_style]["direction"]
        variation = "Keep the requested expression and a relaxed near-frontal pose."
        if index == 1:
            variation = "Use a slightly different shoulder angle with the same natural expression; keep the face directed toward the lens."
        variants.append({"candidate": index + 1, "style": candidate_style, "prompt": template.format(identity_notes=identity, style_direction=direction + " " + variation, preferences=preferences, negative_constraints=negative).strip()})
    executable = mode.startswith("image-edit")
    return {
        "mode": mode,
        "status": status,
        "execution": "not-executed",
        "images_generated": 0,
        "visual_qa": "not-performed",
        "style": style_id,
        "style_name": preset["name"],
        "references": references,
        "source_reviewed": reviewed,
        "capabilities": flags,
        "tool": capabilities.get("tool") if flags["reference_edit"] else None,
        "budget": {"max_tool_calls": max_calls, "initial_calls": initial_calls if executable else 0, "repair_calls": repair_calls if executable else 0, "failures_count_toward_limit": True},
        "candidate_variants": variants,
        "prompt": prompt,
        "negative_constraints": negative,
        "notice_zh": "仅生成提示词与计划；脚本不看图、不调用生图服务，也不进行视觉质检。图片须由具备参考图编辑能力的环境生成，本人终审。",
        "next_step_zh": "上传原图到参考图编辑入口，确认图片已附上；使用主提示词或对应候选提示词。没有独立负面字段时，主提示词已经包含负面约束。",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--capabilities", type=Path)
    parser.add_argument("--format", choices=("json", "prompt"), default="json")
    parser.add_argument("--out", type=Path, help="New file only; existing files are never overwritten")
    parser.add_argument("--list-styles", action="store_true")
    args = parser.parse_args()
    try:
        if args.list_styles:
            result = json.dumps(load_json(ROOT / "styles/presets.json"), ensure_ascii=False, indent=2)
        else:
            if args.request is None or args.capabilities is None:
                parser.error("--request and --capabilities are required unless --list-styles is used")
            plan = compose(load_json(args.request), load_json(args.capabilities))
            result = plan["prompt"] if args.format == "prompt" else json.dumps(plan, ensure_ascii=False, indent=2)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("x", encoding="utf-8", newline="\n") as output:
                output.write(result + "\n")
        else:
            print(result)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
