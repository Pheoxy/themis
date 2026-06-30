from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.policy import PolicyConfig
from themis.providers import AIProviderConfig, ASSISTANT_WORKFLOWS, SUPPORTED_PROVIDERS


class SchemaTests(unittest.TestCase):
    def test_schema_id_uses_project_repository(self) -> None:
        schema = load_schema()
        self.assertEqual(schema["$id"], "https://raw.githubusercontent.com/Pheoxy/themis/main/docs/schema/themis.schema.json")

    def test_schema_covers_policy_config_keys(self) -> None:
        schema = load_schema()
        schema_keys = set(schema["properties"]["policy"]["properties"])
        config_keys = set(PolicyConfig.__dataclass_fields__)  # type: ignore[attr-defined]
        self.assertEqual(schema_keys, config_keys)

    def test_schema_allows_top_level_policy_key_shorthand(self) -> None:
        schema = load_schema()
        config_keys = set(PolicyConfig.__dataclass_fields__)  # type: ignore[attr-defined]
        root_policy_keys = set(schema["properties"]) & config_keys
        self.assertEqual(root_policy_keys, config_keys)

    def test_schema_rejects_mixing_policy_table_and_shorthand(self) -> None:
        schema = load_schema()
        blocked_keys = {
            tuple(rule["not"]["required"])[1]
            for rule in schema["allOf"]
            if tuple(rule.get("not", {}).get("required", ()))[:1] == ("policy",)
        }
        self.assertEqual(blocked_keys, set(PolicyConfig.__dataclass_fields__))  # type: ignore[attr-defined]

    def test_schema_covers_ai_provider_config_keys(self) -> None:
        schema = load_schema()
        schema_keys = set(schema["properties"]["ai"]["properties"])
        config_keys = set(AIProviderConfig.__dataclass_fields__)  # type: ignore[attr-defined]
        self.assertEqual(schema_keys, config_keys)

    def test_schema_provider_and_workflow_enums_match_code(self) -> None:
        schema = load_schema()
        providers = set(schema["properties"]["ai"]["properties"]["provider"]["enum"])
        workflows = set(schema["properties"]["ai"]["properties"]["allowed_workflows"]["items"]["enum"])
        self.assertEqual(providers, SUPPORTED_PROVIDERS)
        self.assertEqual(workflows, ASSISTANT_WORKFLOWS)


def load_schema() -> dict:
    path = Path(__file__).resolve().parents[1] / "docs" / "schema" / "themis.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
