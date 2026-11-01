"""LLM falso e determinístico. Usado em teste e no ambiente local sem chave.

Cada tarefa tem um handler que monta a resposta a partir de `request.payload` com
heurísticas simples. Testes também podem roteirizar respostas cruas (`scripted`) para
exercitar JSON inválido, citação inventada e a segunda tentativa.
"""

import json
import re
from collections.abc import Callable
from typing import Any

from app.ai.llm import LLMRequest
from app.services.text import strip_accents

Handler = Callable[[LLMRequest], dict[str, Any]]

_BULLET = re.compile(r"^\s*(?:[-•*▪◦·]|\d+[.)])\s+")
_NICE = ("diferencia", "desejave", "nice to have", "plus", "bonus", "seria um")
_REQUIRED = ("requisito", "obrigator", "requirement", "must have", "qualifica", "exigi")

KNOWN_TECH = (
    "Python",
    "FastAPI",
    "Django",
    "Flask",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "Celery",
    "RabbitMQ",
    "Kafka",
    "Docker",
    "Kubernetes",
    "AWS",
    "GCP",
    "Azure",
    "Terraform",
    "Git",
    "Linux",
    "SQL",
    "REST",
    "GraphQL",
    "TypeScript",
    "JavaScript",
    "React",
    "Node.js",
    "Java",
    "Go",
    "pytest",
    "CI/CD",
)


def _key(text: str) -> str:
    return strip_accents(text).casefold()


def _find_tech(text: str) -> list[str]:
    found = []
    for tech in KNOWN_TECH:
        if re.search(rf"(?<![\w.]){re.escape(tech)}(?![\w])", text, flags=re.IGNORECASE):
            found.append(tech)
    return found


def _seniority(text: str) -> str:
    key = _key(text)
    for word, value in (
        ("estagi", "intern"),
        ("intern", "intern"),
        ("tech lead", "lead"),
        ("lider", "lead"),
        ("senior", "senior"),
        ("pleno", "mid"),
        ("junior", "junior"),
    ):
        if word in key:
            return value
    return "unspecified"


def _work_model(text: str) -> str:
    key = _key(text)
    for word, value in (
        ("hibrid", "hybrid"),
        ("hybrid", "hybrid"),
        ("remot", "remote"),
        ("presencial", "onsite"),
        ("on-site", "onsite"),
    ):
        if word in key:
            return value
    return "unspecified"


def extract_requirements(request: LLMRequest) -> dict[str, Any]:
    text: str = request.payload["job_text"]
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    requirements: list[dict[str, str]] = []
    kind = "required"
    for line in lines:
        key = _key(line)
        if not _BULLET.match(line):
            if any(word in key for word in _NICE):
                kind = "nice_to_have"
            elif any(word in key for word in _REQUIRED):
                kind = "required"
            continue
        requirements.append({"text": _BULLET.sub("", line)[:300], "kind": kind})
    if not requirements:
        requirements = [{"text": line[:300], "kind": "required"} for line in lines[1:11]]
    company = next(
        (line.split(":", 1)[1].strip() for line in lines if _key(line).startswith("empresa:")),
        None,
    )
    return {
        "title": lines[0][:120] if lines else None,
        "company": company or None,
        "seniority": _seniority(text),
        "work_model": _work_model(text),
        "location": None,
        "stack": _find_tech(text),
        "requirements": requirements[:40],
    }


DEFAULT_HANDLERS: dict[str, Handler] = {"extract_requirements": extract_requirements}


class FakeLLMProvider:
    model = "fake-llm"

    def __init__(
        self,
        *,
        scripted: list[str] | None = None,
        handlers: dict[str, Handler] | None = None,
    ) -> None:
        self._scripted = list(scripted or [])
        self._handlers = DEFAULT_HANDLERS | (handlers or {})
        self.requests: list[LLMRequest] = []

    async def complete_json(self, request: LLMRequest) -> str:
        self.requests.append(request)
        if self._scripted:
            return self._scripted.pop(0)
        return json.dumps(self._handlers[request.task](request), ensure_ascii=False)

    async def aclose(self) -> None:
        return None
