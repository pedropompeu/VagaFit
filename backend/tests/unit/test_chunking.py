from itertools import pairwise

from app.services.chunking import MAX_CHUNK_TOKENS, chunk_resume, estimate_tokens, is_heading
from app.services.text import normalize_document

RESUME = """Ana Exemplo
ana@exemplo.com

RESUMO
Desenvolvedora backend com foco em Python e APIs.

EXPERIÊNCIA

Desenvolvedora Backend, Acme Ltda, 2021-2024

- Criei APIs REST em FastAPI atendendo 2 milhões de requisições por dia.
- Migrei filas de RabbitMQ para Celery com Redis.
- Reduzi o tempo de resposta do checkout em 40% com cache.
- Escrevi testes com pytest e mantive cobertura acima de 85%.
- Mentorei duas pessoas desenvolvedoras júnior.

Desenvolvedora Python, Beta S.A., 2018-2021
- Mantive ETL em Airflow carregando dados no PostgreSQL.
- Criei dashboards internos com Django.
- Automatizei relatórios mensais que antes eram manuais.
- Participei da migração do monólito para containers Docker.

Formação
Bacharelado em Ciência da Computação, Universidade Exemplo, 2017

Skills: Python, FastAPI, Django, PostgreSQL, Redis, Docker
"""


def test_headings() -> None:
    assert is_heading("EXPERIÊNCIA")
    assert is_heading("Experiência profissional:")
    assert is_heading("## Projetos")
    assert is_heading("Skills")
    assert not is_heading("Desenvolvedora Backend, Acme Ltda, 2021-2024")
    assert not is_heading("- PYTHON E SQL")
    assert not is_heading("")
    assert not is_heading("AB")


def test_one_chunk_per_experience_and_short_sections() -> None:
    chunks = chunk_resume(normalize_document(RESUME), max_tokens=120)

    assert chunks[0].startswith("Ana Exemplo")
    assert chunks[1].startswith("RESUMO\nDesenvolvedora backend")
    acme = [c for c in chunks if "Acme Ltda" in c]
    beta = [c for c in chunks if "Beta S.A." in c]
    assert len(acme) == 1
    assert len(beta) == 1
    # Linha de cargo separada por linha em branco foi juntada aos bullets dela.
    assert "Criei APIs REST" in acme[0]
    assert acme[0].startswith("EXPERIÊNCIA\n")
    assert "Airflow" not in acme[0]
    assert any(c.startswith("Formação\nBacharelado") for c in chunks)
    assert all(estimate_tokens(c) <= 120 for c in chunks)


def test_small_section_stays_whole() -> None:
    text = "Experiência\nDev Python, Acme, 2020-2024\n\n- Fiz APIs.\n\nDev Java, Beta, 2018-2020"
    assert chunk_resume(text) == [text]


def test_oversized_block_splits_with_overlap() -> None:
    bullets = [f"- Item {i} com bastante texto para ocupar espaço no orçamento." for i in range(40)]
    text = "Experiência\nCargo X, Empresa Y, 2020-2024\n" + "\n".join(bullets)

    chunks = chunk_resume(text, max_tokens=100)

    assert len(chunks) > 1
    assert all(c.startswith("Experiência\n") for c in chunks)
    assert all(estimate_tokens(c) <= 100 for c in chunks)
    for previous, current in pairwise(chunks):
        assert previous.split("\n")[-1] == current.split("\n")[1]  # última linha repetida
    joined = "\n".join(chunks)
    assert all(b in joined for b in bullets)


def test_giant_line_splits_by_words() -> None:
    line = " ".join(f"palavra{i}" for i in range(600))
    chunks = chunk_resume(line, max_tokens=MAX_CHUNK_TOKENS)

    assert len(chunks) > 1
    assert all(estimate_tokens(c) <= MAX_CHUNK_TOKENS for c in chunks)
    first_tail = chunks[0].split()[-1]
    assert first_tail in chunks[1].split()[:25]  # sobreposição de palavras


def test_empty_text() -> None:
    assert chunk_resume("") == []
    assert chunk_resume("\n\n  \n") == []


def test_heading_without_body_is_kept() -> None:
    assert chunk_resume("PROJETOS") == ["PROJETOS"]


def test_normalize_document() -> None:
    raw = "Linha  um\r\n\r\n\r\n\r\nLinha" + chr(0xA0) + "\tdois \x00\n"
    assert normalize_document(raw) == "Linha um\n\nLinha dois"
