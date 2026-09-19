from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"cool-bible-tutor", "vibe-coding-designer"}


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
            self.assertEqual(item["source"]["source"], "local")
            self.assertEqual(item["policy"]["installation"], "AVAILABLE")
            self.assertIn(item["policy"]["authentication"], {"ON_INSTALL", "ON_USE"})
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
            if item["name"] != "vibe-coding-designer":
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


if __name__ == "__main__":
    unittest.main()
