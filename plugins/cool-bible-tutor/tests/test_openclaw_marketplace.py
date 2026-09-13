import json
from pathlib import Path
import unittest


REPOSITORY = Path(__file__).parents[3]
CODEX_MARKETPLACE = REPOSITORY / ".agents" / "plugins" / "marketplace.json"
OPENCLAW_MARKETPLACE = REPOSITORY / ".claude-plugin" / "marketplace.json"
README = REPOSITORY / "README.md"


class OpenClawMarketplaceTests(unittest.TestCase):
    def test_openclaw_catalog_maps_codex_plugins_to_generated_bundle_paths(self):
        codex = json.loads(CODEX_MARKETPLACE.read_text(encoding="utf-8"))
        openclaw = json.loads(OPENCLAW_MARKETPLACE.read_text(encoding="utf-8"))

        self.assertEqual(openclaw["name"], codex["name"])
        self.assertEqual(openclaw["version"], "1.0.0")
        self.assertEqual(
            [entry["name"] for entry in openclaw["plugins"]],
            [entry["name"] for entry in codex["plugins"]],
        )

        for entry in openclaw["plugins"]:
            source = entry["source"]
            self.assertTrue(source.startswith("./openclaw/"))
            bundle = REPOSITORY / source.removeprefix("./")
            package = json.loads((bundle / "package.json").read_text(encoding="utf-8"))
            manifest = json.loads(
                (bundle / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual(entry["version"], package["version"])
            self.assertEqual(entry["version"], manifest["version"])
            self.assertEqual(entry["name"], manifest["name"])
            self.assertTrue(entry["description"].strip())

    def test_readme_documents_direct_github_marketplace_installation(self):
        source = README.read_text(encoding="utf-8")

        self.assertIn(
            "openclaw plugins marketplace list schao523/obvious-one-plugins",
            source,
        )
        self.assertIn(
            "openclaw plugins install cool-bible-tutor --marketplace schao523/obvious-one-plugins",
            source,
        )


if __name__ == "__main__":
    unittest.main()
