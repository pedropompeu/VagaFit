"""Chunking estrutural do currículo (função pura, sem I/O).

Decisão [2026-10-31] (d): um chunk por experiência (empresa + período + bullets) ou por
seção curta, teto de ~250 tokens, sobreposição só quando um bloco estoura o teto. Cada
chunk leva o título da seção na primeira linha, para o chunk fazer sentido sozinho.

Heurística:
1. Título de seção: linha com `#`, nome conhecido (Experiência, Formação, Skills...) ou
   linha curta toda em maiúsculas.
2. Seção que cabe no teto vira um chunk só.
3. Seção grande: cada bloco separado por linha em branco vira um chunk. Linha solta curta
   (cargo/empresa separado dos bullets) é juntada ao bloco seguinte.
4. Bloco acima do teto: dividido por linhas, repetindo a última linha no chunk seguinte;
   linha gigante é dividida por palavras, também com sobreposição.
"""

import math
from dataclasses import dataclass, field

from app.services.text import strip_accents

MAX_CHUNK_TOKENS = 250
_WORD_OVERLAP = 20
_TITLE_LINE_MAX_CHARS = 120

_KNOWN_HEADINGS = frozenset(
    {
        "resumo",
        "resumo profissional",
        "sobre",
        "sobre mim",
        "perfil",
        "perfil profissional",
        "objetivo",
        "experiencia",
        "experiencias",
        "experiencia profissional",
        "experiencias profissionais",
        "historico profissional",
        "formacao",
        "formacao academica",
        "educacao",
        "competencias",
        "competencias tecnicas",
        "habilidades",
        "habilidades tecnicas",
        "tecnologias",
        "conhecimentos",
        "conhecimentos tecnicos",
        "skills",
        "idiomas",
        "certificacoes",
        "certificados",
        "cursos",
        "projetos",
        "projetos pessoais",
        "publicacoes",
        "premios",
        "voluntariado",
        "contato",
        "informacoes adicionais",
        "summary",
        "profile",
        "about",
        "about me",
        "objective",
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "education",
        "technical skills",
        "languages",
        "certifications",
        "courses",
        "projects",
        "publications",
        "awards",
        "volunteering",
        "contact",
    }
)


def estimate_tokens(text: str) -> int:
    """Aproximação barata (~4 caracteres por token), suficiente para o teto do chunk."""
    return math.ceil(len(text) / 4)


def is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return False
    if stripped.startswith("#"):
        return True
    key = strip_accents(stripped.rstrip(":").strip()).casefold()
    if key in _KNOWN_HEADINGS:
        return True
    letters = [ch for ch in stripped if ch.isalpha()]
    return (
        len(letters) >= 3
        and all(ch.isupper() for ch in letters)
        and len(stripped.split()) <= 5
        and not stripped.startswith(("-", "•", "*"))
    )


def _clean_heading(line: str) -> str:
    return line.strip().lstrip("#").strip().rstrip(":").strip()


@dataclass
class _Section:
    heading: str | None
    lines: list[str] = field(default_factory=list)

    def blocks(self) -> list[list[str]]:
        blocks: list[list[str]] = []
        current: list[str] = []
        for line in self.lines:
            if line.strip():
                current.append(line)
            elif current:
                blocks.append(current)
                current = []
        if current:
            blocks.append(current)
        return blocks


def _split_sections(text: str) -> list[_Section]:
    sections: list[_Section] = [_Section(heading=None)]
    for line in text.split("\n"):
        if is_heading(line):
            sections.append(_Section(heading=_clean_heading(line)))
        else:
            sections[-1].lines.append(line)
    return [s for s in sections if any(line.strip() for line in s.lines) or s.heading]


def _join(heading: str | None, lines: list[str]) -> str:
    body = "\n".join(lines).strip()
    if heading is None:
        return body
    return f"{heading}\n{body}" if body else heading


def _merge_title_lines(blocks: list[list[str]], budget: int) -> list[list[str]]:
    """Junta uma linha solta curta (ex.: "Dev Backend, Acme, 2021-2024") ao bloco seguinte."""
    merged: list[list[str]] = []
    pending: list[str] | None = None
    for block in blocks:
        if pending is not None:
            candidate = pending + block
            if estimate_tokens("\n".join(candidate)) <= budget:
                block = candidate
            else:
                merged.append(pending)
            pending = None
        if len(block) == 1 and len(block[0]) <= _TITLE_LINE_MAX_CHARS:
            pending = block
            continue
        merged.append(block)
    if pending is not None:
        merged.append(pending)
    return merged


def _split_long_line(line: str, budget: int) -> list[str]:
    words = line.split()
    pieces: list[str] = []
    current: list[str] = []
    for word in words:
        if current and estimate_tokens(" ".join([*current, word])) > budget:
            pieces.append(" ".join(current))
            overlap = current[-_WORD_OVERLAP:] if len(current) > _WORD_OVERLAP else []
            current = list(overlap)
        current.append(word)
    if current:
        pieces.append(" ".join(current))
    return pieces


def _split_block(lines: list[str], budget: int) -> list[list[str]]:
    """Divide um bloco acima do teto por linhas, repetindo a última linha (sobreposição)."""
    expanded: list[str] = []
    for line in lines:
        if estimate_tokens(line) > budget:
            expanded.extend(_split_long_line(line, budget))
        else:
            expanded.append(line)

    parts: list[list[str]] = []
    current: list[str] = []
    for line in expanded:
        if current and estimate_tokens("\n".join([*current, line])) > budget:
            parts.append(current)
            last = current[-1]
            current = [last] if estimate_tokens(f"{last}\n{line}") <= budget else []
        current.append(line)
    if current:
        parts.append(current)
    return parts


def chunk_resume(text: str, *, max_tokens: int = MAX_CHUNK_TOKENS) -> list[str]:
    """Divide o texto normalizado do currículo em chunks, na ordem do documento."""
    chunks: list[str] = []
    for section in _split_sections(text):
        whole = _join(section.heading, section.lines)
        if not whole:
            continue
        if estimate_tokens(whole) <= max_tokens:
            chunks.append(whole)
            continue
        heading_tokens = estimate_tokens(section.heading + "\n") if section.heading else 0
        budget = max(max_tokens - heading_tokens, 1)
        for block in _merge_title_lines(section.blocks(), budget):
            parts = [block] if estimate_tokens("\n".join(block)) <= budget else None
            for part in parts or _split_block(block, budget):
                chunks.append(_join(section.heading, part))
    return [c for c in chunks if c.strip()]
