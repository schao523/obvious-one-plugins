from pathlib import Path
import unittest


REPOSITORY = Path(__file__).parents[3]
WORKFLOW = REPOSITORY / ".github" / "workflows" / "retry-clawhub.yml"


class ClawHubRetryWorkflowTests(unittest.TestCase):
    def test_retry_workflow_is_clawhub_only_and_fails_closed(self):
        source = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch:", source)
        self.assertIn('default: "2.4.6"', source)
        self.assertIn("secrets.CLAWHUB_TOKEN", source)
        self.assertIn("gh release view", source)
        self.assertIn("clawhub package validate", source)
        self.assertIn("clawhub login --token", source)
        self.assertIn("clawhub package publish", source)
        self.assertNotIn("gh release create", source)
        self.assertNotIn("gh release upload", source)
        self.assertNotIn("continue-on-error", source)


if __name__ == "__main__":
    unittest.main()
