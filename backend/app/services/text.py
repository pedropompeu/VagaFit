"""Normalização de texto compartilhada por chunking, validação de citações e embeddings falsos."""

import re
import unicodedata

_SPACES = re.compile(r"[^\S\n]+")  # todo espaço (inclusive NBSP), menos quebra de linha
_MANY_BLANK_LINES = re.compile(r"\n{3,}")
_WHITESPACE = re.compile(r"\s+")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize_document(text: str) -> str:
    """Limpa texto colado ou extraído de PDF, preservando quebras de linha (estrutura)."""
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = _CONTROL.sub("", text)
    lines = [_SPACES.sub(" ", line).strip() for line in text.split("\n")]
    return _MANY_BLANK_LINES.sub("\n\n", "\n".join(lines)).strip()


def normalize_for_match(text: str) -> str:
    """Forma canônica para comparar citação com chunk: espaços colapsados e caixa ignorada."""
    return _WHITESPACE.sub(" ", unicodedata.normalize("NFC", text)).strip().casefold()


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def quote_in_text(quote: str, text: str) -> bool:
    """Regra de honestidade: a citação normalizada precisa ser substring do texto normalizado."""
    needle = normalize_for_match(quote)
    return bool(needle) and needle in normalize_for_match(text)
