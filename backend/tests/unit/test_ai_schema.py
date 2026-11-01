from typing import Any

from app.ai.schema import strict_json_schema
from app.schemas.extraction import LLMJobExtraction


def _objects(node: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(node, dict):
        if node.get("type") == "object":
            found.append(node)
        for value in node.values():
            found.extend(_objects(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_objects(value))
    return found


def test_strict_schema_inlines_refs_and_closes_objects() -> None:
    schema = strict_json_schema(LLMJobExtraction)
    text = str(schema)

    assert "$ref" not in text
    assert "$defs" not in text
    assert "maxLength" not in text
    assert "maxItems" not in text
    objects = _objects(schema)
    assert len(objects) == 2  # extração + requisito
    for obj in objects:
        assert obj["additionalProperties"] is False
        assert set(obj["required"]) == set(obj["properties"])


def test_strict_schema_keeps_enums_and_descriptions() -> None:
    schema = strict_json_schema(LLMJobExtraction)
    item = schema["properties"]["requirements"]["items"]
    assert item["properties"]["kind"]["enum"] == ["required", "nice_to_have"]
    assert "description" in item["properties"]["text"]
