from app.services.text import normalize_for_match, quote_in_text, strip_accents


def test_normalize_for_match() -> None:
    assert normalize_for_match("  Criei  APIs\nem FastAPI ") == "criei apis em fastapi"


def test_quote_in_text_ignores_spaces_and_case() -> None:
    chunk = "Experiência\n- Criei APIs REST em FastAPI atendendo 2 milhões de requisições."
    assert quote_in_text("criei apis   REST em fastapi", chunk)
    assert not quote_in_text("criei APIs em Go", chunk)
    assert not quote_in_text("   ", chunk)


def test_strip_accents() -> None:
    assert strip_accents("Experiência em São Paulo") == "Experiencia em Sao Paulo"
