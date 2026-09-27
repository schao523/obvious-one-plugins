from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "cool-bible-tutor",
    "cool-plugin-design-assistant",
    "vibe-coding-designer",
}


class MarketplaceCatalogTests(unittest.TestCase):
    def test_catalogs_resolve_every_published_plugin(self) -> None:
        codex = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
        )
        openclaw = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(codex["name"], "obvious-one")
        self.assertEqual(openclaw["name"], "obvious-one")
        self.assertEqual({item["name"] for item in codex["plugins"]}, EXPECTED)
        self.assertEqual({item["name"] for item in openclaw["plugins"]}, EXPECTED)

        for item in codex["plugins"]:
            self.assertEqual(item["source"].get("source", "local"), "local")
            if "policy" in item:
                self.assertEqual(item["policy"]["installation"], "AVAILABLE")
                self.assertIn(
                    item["policy"]["authentication"], {"ON_INSTALL", "ON_USE"}
                )
            plugin_root = ROOT / item["source"]["path"]
            manifest = json.loads(
                (plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["name"], item["name"])

        for item in openclaw["plugins"]:
            plugin_root = ROOT / item["source"]
            package = json.loads((plugin_root / "package.json").read_text(encoding="utf-8"))
            manifest = json.loads(
                (plugin_root / "CONTENT-MANIFEST.json").read_text(encoding="utf-8")
            )
            self.assertEqual(package["version"], item["version"])
            self.assertEqual(manifest["plugin_id"], item["name"])
            self.assertEqual(manifest["version"], item["version"])
            if item["name"] == "cool-bible-tutor":
                continue
            declared = {entry["path"]: entry for entry in manifest["files"]}
            actual = {
                path.relative_to(plugin_root).as_posix()
                for path in plugin_root.rglob("*")
                if path.is_file() and path.name != "CONTENT-MANIFEST.json"
            }
            self.assertEqual(actual, set(declared))
            for relative, entry in declared.items():
                payload = (plugin_root / relative).read_bytes()
                self.assertEqual(len(payload), entry["size"])
                self.assertEqual(sha256(payload).hexdigest(), entry["sha256"])

    def test_vibe_coding_designer_release_boundary(self) -> None:
        attributes = ROOT / ".gitattributes"
        self.assertTrue(attributes.is_file(), "marketplace must preserve Vibe artifact bytes")
        attribute_text = attributes.read_text(encoding="utf-8")
        self.assertIn("/plugins/vibe-coding-designer/** -text", attribute_text)
        self.assertIn("/openclaw/vibe-coding-designer/** -text", attribute_text)
        codex_root = ROOT / "plugins" / "vibe-coding-designer"
        openclaw_root = ROOT / "openclaw" / "vibe-coding-designer"
        for root in (codex_root, openclaw_root):
            self.assertEqual(len(list((root / "skills").glob("*/SKILL.md"))), 7)
            forbidden = [
                path
                for path in root.rglob("*")
                if path.is_file()
                and path.suffix.lower()
                in {".db", ".sqlite", ".sqlite3", ".faiss", ".onnx", ".pt", ".pth", ".pdf"}
            ]
            self.assertEqual(forbidden, [])

    def test_ci_is_catalog_driven_and_independent_from_product_gates(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("data = json.load(open('.obvious-one-validation.json'", workflow)
        self.assertIn("plugin: ${{ fromJson(needs.matrix.outputs.matrix).plugin }}", workflow)
        self.assertIn("tools/verify_marketplace.py --registry", workflow)
        for plugin_id in EXPECTED:
            self.assertNotIn(f"  {plugin_id}:\n", workflow)

    def test_artifact_registry_uses_portable_posix_path_order(self) -> None:
        registry = json.loads(
            (ROOT / ".obvious-one-validation.json").read_text(encoding="utf-8")
        )
        for plugin in registry["plugins"]:
            for artifact in plugin["artifacts"].values():
                paths = [record["path"] for record in artifact["files"]]
                self.assertEqual(paths, sorted(paths))

    def test_legacy_bible_smokes_match_runnable_marketplace_artifacts(self) -> None:
        registry = json.loads(
            (ROOT / ".obvious-one-validation.json").read_text(encoding="utf-8")
        )
        plugin = next(
            item for item in registry["plugins"] if item["plugin_id"] == "cool-bible-tutor"
        )

        self.assertEqual(
            [(command["id"], command["artifact"]) for command in plugin["commands"]],
            [
                ("distribution-audit-codex", "codex"),
                ("exact-passage-openclaw", "openclaw"),
                ("runtime-status-codex", "codex"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
