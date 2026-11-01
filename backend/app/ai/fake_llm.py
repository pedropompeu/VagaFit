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


_STOPWORDS = frozenset(
    {
        "anos",
        "experiencia",
        "conhecimento",
        "conhecimentos",
        "com",
        "para",
        "sobre",
        "em",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "e",
        "ou",
        "um",
        "uma",
        "boa",
        "bom",
        "pratica",
        "solida",
        "avancado",
        "desejavel",
        "dominio",
        "uso",
        "nivel",
        "qual",
        "quais",
        "quantos",
        "quanto",
        "voce",
        "tem",
        "sua",
        "seu",
        "suas",
        "seus",
        "como",
        "por",
        "que",
    }
)


def _keywords(text: str) -> list[str]:
    tech = [_key(t) for t in _find_tech(text)]
    if tech:
        return tech
    words = re.findall(r"[\w+#./-]+", _key(text))
    return [w for w in words if len(w) >= 3 and w not in _STOPWORDS][:4]


def _hits(keywords: list[str], line: str) -> int:
    key = _key(line)
    return sum(1 for k in keywords if re.search(rf"(?<![\w.]){re.escape(k)}(?![\w])", key))


def analyze_fit(request: LLMRequest) -> dict[str, Any]:
    """Veredito por casamento de palavras-chave: todas na mesma linha = met; parte = partial.

    A citação é a própria linha do trecho, então sempre passa na validação literal.
    """
    chunks: dict[str, str] = request.payload["chunks"]
    verdicts: list[dict[str, Any]] = []
    suggestions: list[dict[str, str]] = []
    for req in request.payload["requirements"]:
        keywords = _keywords(req["text"])
        best = _best_line(keywords, chunks, req["candidates"])
        if best is None:
            verdicts.append(
                {
                    "requirement_id": req["id"],
                    "verdict": "not_met",
                    "evidence": [],
                    "rationale": "Nenhum trecho recebido menciona o requisito.",
                }
            )
            continue
        hits, alias, line = best
        verdict = "met" if hits == len(keywords) else "partial"
        verdicts.append(
            {
                "requirement_id": req["id"],
                "verdict": verdict,
                "evidence": [{"chunk": alias, "quote": line}],
                "rationale": "O trecho citado menciona o requisito.",
            }
        )
        if verdict == "met" and len(suggestions) < 2:
            suggestions.append(
                {
                    "chunk": alias,
                    "original": line,
                    "suggestion": f"Leve para o início do bloco: {line.lstrip('-•* ')}",
                }
            )
    return {"verdicts": verdicts, "suggestions": suggestions}


def _best_line(
    keywords: list[str], chunks: dict[str, str], aliases: list[str]
) -> tuple[int, str, str] | None:
    best: tuple[int, str, str] | None = None
    for alias in aliases:
        for line in chunks[alias].split("\n"):
            hits = _hits(keywords, line) if keywords else 0
            if hits and (best is None or hits > best[0]):
                best = (hits, alias, line.strip())
    return best


def screening(request: LLMRequest) -> dict[str, Any]:
    """Responde com a linha que menciona a pergunta; sem menção, pede input do usuário."""
    chunks: dict[str, str] = request.payload["chunks"]
    answers: list[dict[str, Any]] = []
    for q in request.payload["questions"]:
        best = _best_line(_keywords(q["text"]), chunks, q["candidates"])
        if best is None:
            answers.append(
                {
                    "question_id": q["id"],
                    "answer": "",
                    "evidence": [],
                    "needs_user_input": True,
                    "user_question": "O currículo não traz isso. Como você responderia?",
                }
            )
            continue
        _, alias, line = best
        answers.append(
            {
                "question_id": q["id"],
                "answer": f"Sim. No meu currículo: {line.lstrip('-•* ')}",
                "evidence": [{"chunk": alias, "quote": line}],
                "needs_user_input": False,
                "user_question": None,
            }
        )
    return {"answers": answers}


DEFAULT_HANDLERS: dict[str, Handler] = {
    "extract_requirements": extract_requirements,
    "analyze_fit": analyze_fit,
    "screening": screening,
}


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
