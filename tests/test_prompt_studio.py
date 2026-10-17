import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prompt_studio", ROOT / "scripts/prompt_studio.py")
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.request = {"references": ["attachment:front"], "source_reviewed": True, "identity_notes": "Visible features recorded by the operator.", "provider_processing_authorized": True}
        self.caps = {"inspect_inputs": True, "reference_edit": True, "inspect_outputs": True, "tool": "test-editor", "evidence": "Test fixture, not a real provider."}

    def test_complete_capability_matrix(self):
        for vision in (False, True):
            for editor in (False, True):
                for qa in (False, True):
                    with self.subTest(vision=vision, editor=editor, qa=qa):
                        caps = dict(self.caps, inspect_inputs=vision, reference_edit=editor, inspect_outputs=qa)
                        request = dict(self.request, source_reviewed=vision)
                        plan = studio.compose(request, caps)
                        expected = "text-template" if not vision else "prompt-studio" if not editor else "image-edit" if qa else "image-edit-unreviewed"
                        self.assertEqual(plan["mode"], expected)
                        self.assertEqual(plan["images_generated"], 0)
                        self.assertEqual(plan["execution"], "not-executed")
                        self.assertEqual(plan["visual_qa"], "not-performed")

    def test_no_reference_or_no_review_never_ready(self):
        plan = studio.compose(dict(self.request, references=[], source_reviewed=False), self.caps)
        self.assertEqual(plan["mode"], "needs-reference")
        plan = studio.compose(dict(self.request, source_reviewed=False), self.caps)
        self.assertEqual(plan["status"], "awaiting-source-review")
        self.assertEqual(plan["budget"]["initial_calls"], 0)

    def test_no_consent_never_schedules_provider_calls(self):
        plan = studio.compose(dict(self.request, provider_processing_authorized=False), self.caps)
        self.assertEqual(plan["status"], "awaiting-provider-authorization")
        self.assertEqual(plan["budget"]["initial_calls"], 0)

    def test_presets_and_adjacent_candidate(self):
        catalog = studio.load_json(ROOT / "styles/presets.json")
        self.assertEqual(len(catalog["presets"]), 5)
        for style, preset in catalog["presets"].items():
            plan = studio.compose(dict(self.request, style=style), self.caps)
            self.assertIn(preset["direction"], plan["prompt"])
            self.assertEqual([x["style"] for x in plan["candidate_variants"]], [style, style, preset["adjacent"]])
            self.assertIn(catalog["presets"][preset["adjacent"]]["direction"], plan["candidate_variants"][2]["prompt"])

    def test_budget_bounds(self):
        for candidates in (1, 2, 3):
            for maximum in (1, 2, 3, 4, 5):
                plan = studio.compose(dict(self.request, candidate_count=candidates, max_tool_calls=maximum), self.caps)
                budget = plan["budget"]
                self.assertLessEqual(budget["initial_calls"] + budget["repair_calls"], maximum)
                self.assertLessEqual(budget["repair_calls"], 2)
                self.assertEqual(len(plan["candidate_variants"]), min(candidates, maximum))

    def test_unverified_features_are_not_injected(self):
        request = dict(self.request, source_reviewed=False, identity_notes="INVENTED FACE DETAIL")
        plan = studio.compose(request, self.caps)
        self.assertNotIn("INVENTED FACE DETAIL", plan["prompt"])
        self.assertIn("NOT been visually inspected", plan["prompt"])

    def test_reject_invalid_inputs(self):
        for key, value in (("source_reviewed", "true"), ("provider_processing_authorized", 1), ("candidate_count", 4), ("max_tool_calls", 0), ("max_tool_calls", True), ("style", "unknown"), ("references", "photo")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                studio.compose(dict(self.request, **{key: value}), self.caps)
        with self.assertRaises(ValueError):
            studio.compose(self.request, dict(self.caps, inspect_inputs=False))
        with self.assertRaises(ValueError):
            studio.compose(self.request, dict(self.caps, reference_edit="true"))
        with self.assertRaises(ValueError):
            studio.compose(self.request, dict(self.caps, evidence=""))

    def test_cli_writes_utf8_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "plan.json"
            args = [sys.executable, str(ROOT / "scripts/prompt_studio.py"), "--request", str(ROOT / "examples/request.json"), "--capabilities", str(ROOT / "examples/capabilities/vision-only.json"), "--out", str(destination)]
            result = subprocess.run(args, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(studio.load_json(destination)["status"], "awaiting-source-review")
            before = destination.read_bytes()
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 2)
            self.assertEqual(destination.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
