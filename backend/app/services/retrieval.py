"""Contexto recuperado do currículo, compartilhado por análise, triagem e pelo grafo."""

from dataclasses import dataclass

from app.models.resume import ResumeChunk


@dataclass(frozen=True)
class RetrievedContext:
    """O que foi mandado ao LLM: alias -> chunk, e candidatos por item (requisito ou pergunta)."""

    chunks: dict[str, ResumeChunk]
    candidates: dict[str, list[str]]
