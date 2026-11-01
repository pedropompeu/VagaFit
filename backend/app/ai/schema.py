"""JSON Schema estrito a partir de um model Pydantic, aceito pelos dois provedores.

Structured outputs (Anthropic `output_config.format` e OpenAI `json_schema` estrito) exigem
`additionalProperties: false`, todos os campos em `required` e não aceitam várias restrições
(tamanho de string, mínimo e máximo). As restrições continuam valendo: o Pydantic valida a
resposta no código depois.
"""

from typing import Any

from pydantic import BaseModel

_DROP = frozenset(
    {
        "title",
        "default",
        "examples",
        "format",
        "pattern",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minItems",
        "maxItems",
        "uniqueItems",
    }
)


def _resolve(node: Any, defs: dict[str, Any]) -> Any:
    if isinstance(node, list):
        return [_resolve(item, defs) for item in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[-1]
        return _resolve(defs[name], defs)
    out = {k: _resolve(v, defs) for k, v in node.items() if k not in _DROP and k != "$defs"}
    if out.get("type") == "object" and "properties" in out:
        out["additionalProperties"] = False
        out["required"] = list(out["properties"])
    return out


def strict_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    raw = model.model_json_schema()
    resolved: dict[str, Any] = _resolve(raw, raw.get("$defs", {}))
    return resolved
