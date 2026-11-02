# VagaFit — Brand Identity System
> Versão 1.3.1 · 2026-11-02 · Status: Review (pendências na seção 14.4)

Conceito de marca: **Laudo**. Tagline: **Cada ponto, com prova.** Linha de apoio: **Sem prova, é lacuna.**

---

## 00. Guia do documento

**Para que serve.** Este arquivo é a fonte única da identidade do VagaFit. Quem implementa a interface, escreve o README ou monta o social preview deve conseguir fazer isso sem perguntar a um designer. Se algo não está aqui, não existe.

**Onde ficam os arquivos de marca:**

| Arquivo | O que é |
|---|---|
| `BRAND.md` | Este documento (regras, specs, copy, governança) |
| `brand/design-tokens.css` | 385 variáveis CSS em 3 camadas (primitivo, semântico, componente), claro e escuro |
| `brand/tailwind.config.ts` | Config do Tailwind 3.4 que lê os tokens via `var()` |
| `brand/logo/vagafit-mark.svg` | Símbolo isolado (mark only) |
| `brand/logo/vagafit-favicon.svg` | Símbolo no quadrado petróleo (favicon, ícone de app) |
| `brand/logo/vagafit-light.svg` | Símbolo + wordmark para fundo claro |
| `brand/logo/vagafit-dark.svg` | Símbolo + wordmark para fundo escuro |
| `brand/logo/vagafit-mono.svg` | Símbolo + wordmark em uma cor (`currentColor`) |

**Regra de segurança deste repositório.** `BRAND.md` e `brand/` são versionados no repositório público. Nada sensível entra aqui: sem e-mail, sem chave, sem dado real de currículo. Todos os exemplos usam a persona fictícia **Ana Exemplo**.

**Como ler, por papel:** front-end: 03, 05, 08, 13; texto (README, UI, social): 01, 12; logo, favicon e social preview: 02, 11; revisão e aprovação de mudança: 14.

**Donos de cada seção:** ver 14.1.

**Convenção de procedência.** `(d)` = dito por Pedro Pompeu. `(i)` = inferido pelo orquestrador ou por um agente (pode ser revertido). `(e)` = externo (código, norma, documentação).

**Referências cruzadas.** As seções 01 a 12 terminam com "Veja também" (referência cruzada). Tokens são sempre citados pelo nome da variável CSS; o valor vive em `brand/design-tokens.css`.

## 01. Visão geral da marca

**Declaração de identidade.** O VagaFit diz onde vale a pena se candidatar e o que destacar, sem inventar nada. Compara a vaga com o currículo requisito por requisito e mostra a prova de cada ponto, tirada do próprio currículo. Missão: trocar o chute pela evidência na hora de decidir uma candidatura, e nunca inflar a experiência de ninguém.

**Posicionamento.**
- Categoria: análise de aderência vaga × currículo com evidência verificável.
- Para quem: devs plenos e sêniores em busca ativa que preferem saber a verdade sobre o próprio fit. Usuário secundário: recrutador técnico que avalia o repositório e a demo.
- Diferencial: toda afirmação aponta para um trecho do currículo, verificado no código. O que não tem prova aparece como lacuna, nunca como "atende".
- Contra quem: "ATS checkers" de score opaco; geradores de resposta com IA que inventam experiência. (Na comunicação, os contrapontos ficam genéricos; sem comparação nominal.)

**Personalidade (4 traços de voz).** Direto · Honesto · Técnico · Específico. Detalhe na seção 12.

**Conceito visual: Laudo.** A tela parece um relatório técnico que se confere linha a linha: papel claro e frio, tipografia técnica, linhas finas de 1px, muito respiro. Referências: Linear (densidade e precisão) e Stripe Docs (leitura técnica clara). Palavras-guia: documental, preciso, arejado.

**A regra que organiza tudo.** A hierarquia visual repete a regra do produto: "Atende" só existe com citação ao lado. Por isso:

| Papel | Cor | Regra |
|---|---|---|
| Identidade e ação | Petróleo | Botões, links, foco, logo, score, barras |
| Prova | Âmbar marca-texto | **Exclusivo** da evidência citada (trecho do currículo) |
| Veredito | Floresta, terracota, tijolo, grafite | Sempre com ícone e texto, nunca só cor |
| Estrutura | Grafite | Papel, tinta, linhas |

**Conceito descartado.** "Marca-texto" (âmbar como cor dominante): fazia o âmbar perder a função de apontar a evidência. Também descartado o território "Radar" (escuro, verde-neon, painel de monitoramento).

**Decisão de produto fechada.** Modo claro é o padrão (leitura longa de evidência). O escuro existe como tema derivado, definido nos tokens e implementado depois.

**Não fazemos.** Gauge, velocímetro, anel de progresso, "%" gigante; gradiente, glow, glassmorphism; confete, troféu, estrela, foguete, alvo, aperto de mão; emoji na interface; selo ou carimbo de "aprovado". O produto não certifica ninguém.

Veja também: 02 (símbolo), 03 (cores), 12 (voz).

## 02. Sistema de logo

### 2.1 Símbolo: "Infinito com duas pessoas" (desenho da rodada 3)

[2026-11-01] (d) Escolhido por Pedro Pompeu na prancha visual: opção 1a, "Infinito com duas pessoas". O desenho é o da rodada 3, refeito a partir da imagem de referência que ele mandou. O desenho de traço fino da rodada 2 (cor única, dois arcos) fica `~superseded 2026-11-01` por este. O "Visto sublinhado" da v1.0 já estava superado.

Uma fita grossa em infinito forma os corpos de duas figuras, com uma cabeça sobre cada laço. No cruzamento, o traço que sobe da esquerda para a direita passa **por cima**, com um vão que separa as duas camadas. Um arco aberto à direita envolve o conjunto pela esquerda: é mais grosso no meio e afina nas pontas.

**As duas cores dizem quem é quem.** A figura e o laço da esquerda são **você** (neutro). A figura e o laço da direita, junto com o arco, são **a vaga** (petróleo). A fita passa de uma cor para a outra no cruzamento, que é onde as duas se encontram. Esse degradê só existe dentro da fita, e é a única transição de cor da marca. O símbolo não tem âmbar: o âmbar do logo é só o grifo do wordmark.

Geometria (grade 48×48), gerada pelo mesmo código da prancha:
- infinito: `M26.2 26.6C20.6 20 11.2 20 11.2 26.6C11.2 33.2 20.6 33.2 26.2 26.6C31.8 20 41.4 20 41.4 26.6C41.4 33.2 31.8 33.2 26.2 26.6Z`, traço 5,2, junta arredondada, sem preenchimento;
- trecho que passa por cima: `M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16`, traço 5,2. O vão de 1,1 de cada lado é uma máscara de 7,4 sobre o infinito, e não um traço da cor do fundo, por isso o SVG funciona sobre qualquer fundo;
- degradê da fita: linear e horizontal, de x=21,2 ("você") a x=31,2 ("a vaga");
- cabeças: r=3,5 em (18,6; 14,2) "você" e (35; 14,2) "a vaga";
- arco: `M37.05 11.33A19.6 19.6 0 1 0 28.3 41.82A19.05 19.05 0 1 1 37.05 11.33Z`, preenchido, na cor "a vaga".

**Ícone de app e favicon.** É o mesmo símbolo, sem simplificar, sobre um quadrado petróleo `#0F4753` com `rx=11`, em escala 0,77. Nele, "você" fica branco e "a vaga" fica `#7FD8E1`. Na prancha, a 16 px o arco vira um risco fino, mas a forma ainda lê. Se o favicon ficar fraco no uso real, a alternativa já desenhada é a 1c da prancha, sem o arco e com cabeças maiores. Ela não foi escolhida.

### 2.2 Wordmark

[2026-11-01] (d) **"vagafit" em IBM Plex Mono Medium (500), tudo minúsculo, letter-spacing -0.01em, com o "fit" grifado a marca-texto.** O grifo é uma faixa âmbar-300 `#FFD45C` que começa em 56% da altura da caixa do texto e desce até o pé dela (no escuro, `#8A6A12`). O texto fica em tinta. Pedro escolheu o híbrido "e", que junta a fonte mono da finalista c com o grifo da b.

- **No texto, o nome continua VagaFit**, com V e F maiúsculos, em README, interface e copy. O minúsculo vale só no logotipo.
- O grifo é a única exceção à regra "âmbar só na evidência" (3.4), e repete o marca-texto da citação. Ele nunca vai para "vaga".
- **Proporção do lockup, igual à da prancha:** o símbolo tem cerca de 1,5 vez o corpo do texto, com um respiro de 0,4 corpo entre os dois. No SVG, o símbolo tem 32 de altura e o texto 21.

### 2.3 Variantes

| Variante | Arquivo | Fundo | Cores |
|---|---|---|---|
| Light | `vagafit-light.svg` | Claro (canvas e surface Sálvia) | "Você" `#13262B`, "a vaga" `#1D7F8C`, texto `#151C17`, grifo `#FFD45C` |
| Dark | `vagafit-dark.svg` | Escuro (grafite-800 e 900) | "Você" `#EEF5F5`, "a vaga" `#4FC1CC`, texto `#E6F0F1`, grifo `#8A6A12` |
| Mono | `vagafit-mono.svg` | Qualquer, em uma cor | Tudo em `currentColor`. O vão do cruzamento continua (máscara), e o grifo vira um sublinhado de 2,5 unidades |
| Mark only | `vagafit-mark.svg` | Claro | Símbolo isolado, nas cores da light |
| Favicon / app | `vagafit-favicon.svg` | Qualquer | Símbolo no quadrado `#0F4753`: "você" `#FFFFFF`, "a vaga" `#7FD8E1` |

Tokens: `--color-logo-you` e `--color-logo-job` (claro `#13262B` / `#1D7F8C`, escuro `#EEF5F5` / `#4FC1CC`) e `--color-logo-grifo` (claro âmbar-300 `#FFD45C`, escuro `#8A6A12`); no Tailwind, `logo-you`, `logo-job` e `logo-grifo`. O componente React do logo (`frontend/src/components/brand/Logo.tsx`) usa os três e troca com o tema.

Contrastes verificados (WCAG 2.x; o mínimo para elemento gráfico é 3:1):
- "você" `#13262B`: 12,03:1 sobre canvas Sálvia e 13,83:1 sobre surface;
- "a vaga" `#1D7F8C`: 3,61:1 sobre canvas e 4,15:1 sobre surface. Passa, mas com pouca folga: não use a light sobre fundo mais escuro que o canvas;
- escuro, "você" `#EEF5F5`: 15,88:1 sobre grafite-900 e 12,85:1 sobre grafite-800;
- escuro, "a vaga" `#4FC1CC`: 8,21:1 sobre grafite-900 e 6,65:1 sobre grafite-800;
- ícone de app: branco sobre `#0F4753` dá 10,26:1, e `#7FD8E1` dá 6,26:1;
- tinta sobre o grifo: 12,25:1. O texto do escuro sobre o grifo escuro dá 4,36:1, um par de logotipo, fora da exigência de texto.

A variante light não funciona sobre fundo escuro: nele, use a dark.

### 2.4 Código SVG

Os arquivos abaixo são idênticos aos de `brand/logo/`. O wordmark usa `<text>` com fallback para `ui-monospace` (ver 2.7). Os `id` de degradê e de máscara têm prefixo por arquivo (`vf-mark-`, `vf-light-` etc.) para não colidirem quando dois SVGs estão inline na mesma página.

**Mark only** (`vagafit-mark.svg`)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" role="img" aria-labelledby="vf-mark-title">
  <title id="vf-mark-title">VagaFit</title>
  <defs>
    <linearGradient id="vf-mark-g" gradientUnits="userSpaceOnUse" x1="21.2" y1="0" x2="31.2" y2="0"><stop offset="0" stop-color="#13262B"/><stop offset="1" stop-color="#1D7F8C"/></linearGradient>
    <mask id="vf-mark-m" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48"><rect width="48" height="48" fill="#fff"/><path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="#000" stroke-width="7.4"/></mask>
  </defs>
  <path d="M37.05 11.33A19.6 19.6 0 1 0 28.3 41.82A19.05 19.05 0 1 1 37.05 11.33Z" fill="#1D7F8C"/>
  <path d="M26.2 26.6C20.6 20 11.2 20 11.2 26.6C11.2 33.2 20.6 33.2 26.2 26.6C31.8 20 41.4 20 41.4 26.6C41.4 33.2 31.8 33.2 26.2 26.6Z" fill="none" stroke="url(#vf-mark-g)" stroke-width="5.2" stroke-linejoin="round" mask="url(#vf-mark-m)"/>
  <path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="url(#vf-mark-g)" stroke-width="5.2"/>
  <circle cx="18.6" cy="14.2" r="3.5" fill="#13262B"/>
  <circle cx="35" cy="14.2" r="3.5" fill="#1D7F8C"/>
</svg>
```

**Favicon / ícone de app** (`vagafit-favicon.svg`)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" role="img" aria-labelledby="vf-fav-title">
  <title id="vf-fav-title">VagaFit</title>
  <rect width="48" height="48" rx="11" fill="#0F4753"/>
  <g transform="translate(5.5 5.5) scale(0.77)">
  <defs>
    <linearGradient id="vf-fav-g" gradientUnits="userSpaceOnUse" x1="21.2" y1="0" x2="31.2" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#7FD8E1"/></linearGradient>
    <mask id="vf-fav-m" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48"><rect width="48" height="48" fill="#fff"/><path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="#000" stroke-width="7.4"/></mask>
  </defs>
  <path d="M37.05 11.33A19.6 19.6 0 1 0 28.3 41.82A19.05 19.05 0 1 1 37.05 11.33Z" fill="#7FD8E1"/>
  <path d="M26.2 26.6C20.6 20 11.2 20 11.2 26.6C11.2 33.2 20.6 33.2 26.2 26.6C31.8 20 41.4 20 41.4 26.6C41.4 33.2 31.8 33.2 26.2 26.6Z" fill="none" stroke="url(#vf-fav-g)" stroke-width="5.2" stroke-linejoin="round" mask="url(#vf-fav-m)"/>
  <path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="url(#vf-fav-g)" stroke-width="5.2"/>
  <circle cx="18.6" cy="14.2" r="3.5" fill="#FFFFFF"/>
  <circle cx="35" cy="14.2" r="3.5" fill="#7FD8E1"/>
  </g>
</svg>
```

**Light** (`vagafit-light.svg`)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130 32" width="130" height="32" role="img" aria-labelledby="vf-light-title">
  <title id="vf-light-title">VagaFit</title>
  <g transform="scale(0.6667)">
  <defs>
    <linearGradient id="vf-light-g" gradientUnits="userSpaceOnUse" x1="21.2" y1="0" x2="31.2" y2="0"><stop offset="0" stop-color="#13262B"/><stop offset="1" stop-color="#1D7F8C"/></linearGradient>
    <mask id="vf-light-m" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48"><rect width="48" height="48" fill="#fff"/><path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="#000" stroke-width="7.4"/></mask>
  </defs>
  <path d="M37.05 11.33A19.6 19.6 0 1 0 28.3 41.82A19.05 19.05 0 1 1 37.05 11.33Z" fill="#1D7F8C"/>
  <path d="M26.2 26.6C20.6 20 11.2 20 11.2 26.6C11.2 33.2 20.6 33.2 26.2 26.6C31.8 20 41.4 20 41.4 26.6C41.4 33.2 31.8 33.2 26.2 26.6Z" fill="none" stroke="url(#vf-light-g)" stroke-width="5.2" stroke-linejoin="round" mask="url(#vf-light-m)"/>
  <path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="url(#vf-light-g)" stroke-width="5.2"/>
  <circle cx="18.6" cy="14.2" r="3.5" fill="#13262B"/>
  <circle cx="35" cy="14.2" r="3.5" fill="#1D7F8C"/>
  </g>
  <rect x="90.06" y="16.56" width="38.85" height="12.02" fill="#FFD45C"/>
  <text x="40.5" y="22.8" fill="#151C17" font-family="'IBM Plex Mono', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace" font-size="21" font-weight="500" letter-spacing="-0.21">vaga<tspan dx="0.84">fit</tspan></text>
</svg>
```

**Dark** (`vagafit-dark.svg`)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130 32" width="130" height="32" role="img" aria-labelledby="vf-dark-title">
  <title id="vf-dark-title">VagaFit</title>
  <g transform="scale(0.6667)">
  <defs>
    <linearGradient id="vf-dark-g" gradientUnits="userSpaceOnUse" x1="21.2" y1="0" x2="31.2" y2="0"><stop offset="0" stop-color="#EEF5F5"/><stop offset="1" stop-color="#4FC1CC"/></linearGradient>
    <mask id="vf-dark-m" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48"><rect width="48" height="48" fill="#fff"/><path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="#000" stroke-width="7.4"/></mask>
  </defs>
  <path d="M37.05 11.33A19.6 19.6 0 1 0 28.3 41.82A19.05 19.05 0 1 1 37.05 11.33Z" fill="#4FC1CC"/>
  <path d="M26.2 26.6C20.6 20 11.2 20 11.2 26.6C11.2 33.2 20.6 33.2 26.2 26.6C31.8 20 41.4 20 41.4 26.6C41.4 33.2 31.8 33.2 26.2 26.6Z" fill="none" stroke="url(#vf-dark-g)" stroke-width="5.2" stroke-linejoin="round" mask="url(#vf-dark-m)"/>
  <path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="url(#vf-dark-g)" stroke-width="5.2"/>
  <circle cx="18.6" cy="14.2" r="3.5" fill="#EEF5F5"/>
  <circle cx="35" cy="14.2" r="3.5" fill="#4FC1CC"/>
  </g>
  <rect x="90.06" y="16.56" width="38.85" height="12.02" fill="#8A6A12"/>
  <text x="40.5" y="22.8" fill="#E6F0F1" font-family="'IBM Plex Mono', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace" font-size="21" font-weight="500" letter-spacing="-0.21">vaga<tspan dx="0.84">fit</tspan></text>
</svg>
```

**Mono** (`vagafit-mono.svg`). A cor vem de `currentColor`, e o atributo `color` do arquivo define o padrão (tinta). Para a versão branca, use o SVG inline com `color: #FFFFFF`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130 32" width="130" height="32" color="#151C17" role="img" aria-labelledby="vf-mono-title">
  <title id="vf-mono-title">VagaFit</title>
  <g transform="scale(0.6667)">
  <defs>
    <linearGradient id="vf-mono-g" gradientUnits="userSpaceOnUse" x1="21.2" y1="0" x2="31.2" y2="0"><stop offset="0" stop-color="currentColor"/><stop offset="1" stop-color="currentColor"/></linearGradient>
    <mask id="vf-mono-m" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48"><rect width="48" height="48" fill="#fff"/><path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="#000" stroke-width="7.4"/></mask>
  </defs>
  <path d="M37.05 11.33A19.6 19.6 0 1 0 28.3 41.82A19.05 19.05 0 1 1 37.05 11.33Z" fill="currentColor"/>
  <path d="M26.2 26.6C20.6 20 11.2 20 11.2 26.6C11.2 33.2 20.6 33.2 26.2 26.6C31.8 20 41.4 20 41.4 26.6C41.4 33.2 31.8 33.2 26.2 26.6Z" fill="none" stroke="url(#vf-mono-g)" stroke-width="5.2" stroke-linejoin="round" mask="url(#vf-mono-m)"/>
  <path d="M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16" fill="none" stroke="url(#vf-mono-g)" stroke-width="5.2"/>
  <circle cx="18.6" cy="14.2" r="3.5" fill="currentColor"/>
  <circle cx="35" cy="14.2" r="3.5" fill="currentColor"/>
  </g>
  <rect x="90.06" y="25.8" width="38.85" height="2.5" rx="1" fill="currentColor"/>
  <text x="40.5" y="22.8" fill="currentColor" font-family="'IBM Plex Mono', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace" font-size="21" font-weight="500" letter-spacing="-0.21">vaga<tspan dx="0.84">fit</tspan></text>
</svg>
```

### 2.5 Área de respeito e tamanho mínimo

- **Área de respeito:** `x` = 1/4 da largura do símbolo (12 unidades na grade 48), livre em todos os lados do símbolo e do lockup.
- **Tamanho mínimo:**
  - símbolo solto: 24 px. Abaixo disso, use o ícone de app (favicon de 16 px);
  - lockup: altura mínima de 24 px.

### 2.6 Usos proibidos

| Faça | Não faça |
|---|---|
| Use a variante que combina com o fundo (light no claro, dark no escuro) | Colocar a light sobre fundo escuro |
| Mantenha "você" à esquerda em neutro e "a vaga" à direita em petróleo | Inverter as cores, pintar as duas figuras da mesma cor na versão colorida ou trocar o lado delas |
| Use as cores exatas dos arquivos | Recolorir, pôr âmbar no símbolo ou preencher os laços do infinito |
| Mantenha o cruzamento por cima com o vão | Tirar o vão ou inverter qual traço passa por cima |
| Escale proporcionalmente | Esticar, rotacionar, espelhar, inclinar ou distorcer |
| Use fundo liso | Aplicar outro degradê, sombra, glow, contorno, 3D ou efeito de vidro (o único degradê é o da fita) |
| Mantenha o wordmark em Plex Mono 500, minúsculo, com "fit" grifado | Trocar a fonte ou o peso, usar caixa alta, escrever "VagaFit" no logotipo, tirar o grifo ou grifar "vaga" |
| Use a mono quando houver uma cor só | Usar a mono onde a colorida cabe |
| Use sobre fundo com contraste | Colocar sobre foto ou textura que prejudique a leitura |
| Use o símbolo sozinho como assinatura quando faltar espaço | Dar rosto, expressão, mãos ou acessórios às figuras; adicionar selo, estrela ou troféu |

### 2.7 Nota técnica do wordmark

Os SVGs usam texto vivo (`<text>`). Dentro de `<img>`, o navegador não usa a fonte da página e cai para `ui-monospace`. Como fontes mono têm larguras parecidas (cerca de 0,6 em), o grifo continua alinhado ao "fit", mas o desenho das letras muda. Por isso:
- **no app,** use o componente React com o SVG inline (o símbolo) e o wordmark em HTML com a classe de fonte mono, como na prévia da prancha;
- **em materiais estáticos** (social preview e impressos), exporte o lockup com o texto convertido em curvas.

### 2.8 Registro

[2026-11-01] (e) A prancha da rodada 3 avisa que as imagens de referência "têm cara de logo pronto (ou gerado por IA a partir de logos existentes)". O desenho daqui é próprio, mas a composição ficou próxima da referência de propósito. Antes de registrar a marca ou usá-la comercialmente, faça uma busca de anterioridade no INPI, classe 42 no mínimo (ver 14.4).

## 03. Sistema de cor

Os valores completos estão em `brand/design-tokens.css`. Aqui estão as famílias, os papéis e as regras. Arquitetura em três camadas:

```
Primitivo (--color-petroleo-600)  valor bruto; nunca usado direto em componente
   ↓
Semântico (--color-brand)         intenção; é a única camada que muda no escuro
   ↓
Componente (--btn-primary-bg)     escopo por componente; só var(), nenhum literal
```

### 3.1 Tokens primitivos (resumo)

| Família | Passos | Papel |
|---|---|---|
| **Petróleo** | 50 `#EEF6F7` · 100 `#D5E9EC` · 200 `#A9D2D8` · 300 `#74B4BE` · 400 `#3F8F9C` · 500 `#1F6F7D` · 600 `#155A67` · 700 `#0F4753` · 800 `#0B3740` · 900 `#072830` | Ação e identidade |
| **Sálvia** (neutros com cor, modo claro) | 50 `#EDF2EE` · 100 `#DAE4DC` · 200 `#C4D3C7` · 300 `#A9BFAF` · 500 `#6E8574` · 600 `#46544A` · 900 `#151C17` | Papel, tinta e linhas do modo claro. Pedro vetou fundo branco `(d)` |
| **Grafite** (neutros frios) | 0 `#FFFFFF` · 25 `#FAFBFB` · 50 `#F3F5F6` · 100 `#E6EAEC` · 200 `#D2D8DB` · 300 `#B0B9BE` · 400 `#869299` · 500 `#63707A` · 600 `#4A5660` · 700 `#36414A` · 800 `#232C33` · 900 `#141A1F` | Modo escuro, veredito "Sem evidência"; o branco não é superfície |
| **Âmbar marca-texto** | 100 `#FFF4CC` · 200 `#FFE699` · 300 `#FFD45C` · 400 `#F5B82E` · 700 `#7A5502` (+ `ambar-mark-dark` 20% e `ambar-block-dark` 8% para o escuro) | **Só** evidência citada |
| **Floresta** | 50 `#E3F2EA` · 300 `#A8D5BC` · 400 `#6FBF93` · 700 `#1E6B46` · 900 `#12291D` | Atende, sucesso |
| **Terracota** | 50 `#FCEBDD` · 300 `#EBB894` · 400 `#E49A62` · 700 `#9A4A12` · 900 `#2D1A0D` | Atende em parte, aviso |
| **Tijolo** | 50 `#FBE9E9` · 300 `#E8B1B3` · 400 `#E07A7E` · 700 `#A3262A` · 800 `#7D1D21` · 900 `#2E1214` | Não atende, erro, ação destrutiva |

Os passos 400 e 900 de floresta, terracota e tijolo (e o 800 do tijolo) foram derivados para o modo escuro e aceitos pela ARIA `(i)`. O grafite-25 e o grafite-500 estão reservados (sem uso hoje).

### 3.2 Tokens semânticos (claro e escuro)

| Token | Claro | Escuro | Uso |
|---|---|---|---|
| `--color-canvas` | sálvia-100 | grafite-900 | Fundo da página |
| `--color-surface` | sálvia-50 | grafite-800 | Cards, cabeçalho, campos |
| `--color-sunken` | sálvia-100 | grafite-900 | Área rebaixada (leitura do currículo, desabilitado) |
| `--color-ink` | sálvia-900 | grafite-50 | Texto principal |
| `--color-muted` | sálvia-600 | grafite-300 | Texto secundário |
| `--color-line` | sálvia-300 | grafite-700 | Divisores e bordas de card (decorativos) |
| `--color-line-strong` | sálvia-500 | grafite-400 | **Borda de controle** (≥ 3:1) |
| `--color-brand` | petróleo-600 | petróleo-300 | Ação, links, foco |
| `--color-brand-hover` / `-active` | petróleo-700 / 800 | petróleo-200 / 100 | Hover e pressionado |
| `--color-brand-contrast` | branco | petróleo-900 | Texto sobre a ação |
| `--color-brand-soft` | petróleo-50 | petróleo-800 | Item atual, alerta info |
| `--color-danger` | tijolo-700 | tijolo-400 | Erro, ação destrutiva |
| `--color-success` | floresta-700 | floresta-400 | Sucesso |
| `--color-warning` | terracota-700 | terracota-400 | Aviso (**não** é âmbar) |
| `--color-evidence-bg` / `-bg-soft` | âmbar-200 / 100 | âmbar 20% / 8% | Marca-texto / bloco da citação |
| `--color-evidence-border` | âmbar-400 | âmbar-400 | Faixa lateral (decorativa) |
| `--color-evidence-meta` | âmbar-700 | âmbar-300 | ID do trecho (mono) |
| `--color-score-bg/-text/-border` | petróleo-50 / 800 / 100 | petróleo-900 / 100 / 700 | Badge de score (neutro) |
| `--focus-ring-color` | petróleo-500 | petróleo-300 | Anel de foco |
| `--color-dataviz-fill-1/-2/-3` | petróleo-600 / 400 / 800 | petróleo-300 / 500 / 100 | Barras |

`--color-brand` usa petróleo-600 e não o 700 do logo `(i)`: a cor de ação também é cor de texto e link, e o 600 separa melhor da tinta e dá hover visível. O logo continua em 700 pelo primitivo.

### 3.3 Cores de veredito

Sempre com ícone **e** texto. Nunca só cor.

| Veredito (código) | Rótulo na UI | Texto | Fundo | Borda | Ícone |
|---|---|---|---|---|---|
| `met` com citação | Atende | `#1E6B46` | `#E3F2EA` | `#A8D5BC` sólida | `circle-check` |
| `partial` | Atende em parte | `#9A4A12` | `#FCEBDD` | `#EBB894` sólida | `circle-minus` |
| `not_met` | Não atende | `#A3262A` | `#FBE9E9` | `#E8B1B3` sólida | `circle-x` |
| `met` sem citação | Sem evidência | `#4A5660` | `#F3F5F6` | `#869299` **tracejada** | `circle-dashed` |

Tokens: `--color-verdict-{met|partial|not-met|no-evidence}-{text|bg|border}`; a borda tracejada usa `--verdict-no-evidence-border-style: dashed`.

**Decisão `(i)`, fechada:** "Sem evidência" = veredito `met` sem citação (regra que o front já aplica). `not_met` = lacuna, rótulo "Não atende".

### 3.4 Regras de uso

1. **Âmbar só na evidência citada.** Nada de âmbar em botão, aviso, gráfico, logo (além da faixa) ou decoração.
2. **Petróleo é ação.** Botão primário, link, foco, barra, score.
3. **Status nunca só por cor.** Rótulo textual obrigatório; ícone acompanha.
4. **Score é neutro.** Badge petróleo-50 com texto petróleo-800. Sem semáforo, sem faixa de cor.
5. **Sem gradiente**, em nenhuma superfície.
6. **Terracota é compartilhado** entre "Atende em parte" e o aviso do sistema `(i)`. Aceito porque os dois sempre levam ícone e texto distintos.
7. **A faixa lateral da evidência é decorativa** `(i)`: o significado está na marca-texto, no texto e no rótulo. Contraste 1,62:1 no claro; se algum dia precisar passar 3:1, use âmbar-500 `#D99A0B`.
8. **A borda tracejada de "Sem evidência" é decorativa** `(i)`: o rótulo textual porta o significado.
9. Divisores usam `--color-line`; **qualquer borda que identifica um controle** usa `--color-line-strong` (1,44:1 contra branco não basta; 3,19:1 passa WCAG 1.4.11).
10. Modificadores de opacidade do Tailwind (`bg-brand/50`) não funcionam, porque as cores são `var()` de cor cheia. Use os tokens `*-soft`.

### 3.5 Contraste (resumo, WCAG 2.x, AA)

Todos os pares de texto passam 4,5:1 nos dois modos (menor valor: 4,79:1, texto secundário sobre o painel de marca). Pares de UI passam 3:1. Principais:

| Par | Claro | Escuro |
|---|---|---|
| Tinta sobre canvas | 13,31 | 16,04 |
| Secundário (muted) sobre surface | 7,05 | 7,12 |
| Botão primário (texto/fundo) | 7,81 | 6,65 |
| Veredito Atende / Em parte / Não atende / Sem evidência | 5,59 / 5,37 / 6,25 / 6,64 | 9,49 / 9,34 / 9,38 / 8,79 |
| Score (texto/fundo) | 11,72 | 12,32 |
| Citação (texto/bloco) | 15,92 | 11,03 |
| Borda de campo vs surface | 3,52 | 4,45 |
| Anel de foco vs surface | 5,11 | 6,09 |

### 3.6 Como usar (Tailwind)

```tsx
// Classes do Tailwind leem os tokens; o tema claro/escuro vive só no CSS.
<button className="bg-brand text-brand-contrast hover:bg-brand-hover active:bg-brand-active rounded-md px-md py-sm">
  Analisar vaga
</button>
<input className="border border-line-strong bg-surface text-ink rounded-md" />
<span className="bg-verdict-no-evidence-bg text-verdict-no-evidence-text border border-dashed border-verdict-no-evidence-border">Sem evidência</span>
```

Veja também: 04 (superfícies), 08 (componentes), 10 (barras).

## 04. Sistema de fundos e superfícies

O Laudo é plano: **a separação é feita por linha de 1px, nunca por sombra pesada.** Sombra só em popover e diálogo. **Sem branco** `(d)`: nenhuma superfície do modo claro é branca; o papel é Sálvia (canvas `#DAE4DC`, surface `#EDF2EE`). **Proibido** em qualquer fundo: gradiente (inclui padrões e shimmer), `backdrop-filter`/blur, glow, imagem decorativa, âmbar fora da evidência.

| # | Superfície | Quando usar | Tokens principais |
|---|---|---|---|
| 1 | Canvas | Fundo da página | `--color-canvas` |
| 2 | Card | Bloco de conteúdo padrão | `--card-*` |
| 3 | Sunken | Leitura do currículo, campo desabilitado, trecho expandido | `--color-sunken`, `--color-line` |
| 4 | Evidence | Citação do currículo (única superfície quente) | `--evidence-quote-*` |
| 5 | Brand | Painel de marca do `AuthShell` | `--color-brand`, `--color-brand-contrast` |
| 6 | Bar | Cabeçalho e rodapé | `--color-surface`, `--color-line` |
| 7 | Scrim | Atrás do diálogo | `--color-overlay` |
| 8 | Dialog | Diálogo modal | `--dialog-*`, `--shadow-dialog` |
| 9 | Popover | Menu ou tooltip (futuro) | `--color-surface`, `--shadow-popover` |
| 10 | Brand soft | Item selecionado, nav atual, alerta info | `--color-brand-soft` |
| 11 | Skeleton | Carregamento (pulso de opacidade, sem shimmer) | `--color-line` |

```css
.surface-card    { background: var(--card-bg); border: var(--border-width-thin) solid var(--card-border);
                   border-radius: var(--card-radius); box-shadow: var(--card-shadow); padding: var(--card-padding); }
.surface-evidence { background: var(--evidence-quote-bg); color: var(--evidence-quote-text);
                   border-left: var(--evidence-quote-border-width) solid var(--evidence-quote-border);
                   border-radius: 0 var(--evidence-quote-radius) var(--evidence-quote-radius) 0;
                   padding: var(--evidence-quote-padding); }
.mark-evidence   { background: var(--evidence-quote-mark); color: inherit; padding: 0 var(--space-2xs);
                   border-radius: var(--radius-sm); box-decoration-break: clone; -webkit-box-decoration-break: clone;
                   font-family: var(--font-mono); }
.surface-dialog  { background: var(--dialog-bg); border: var(--border-width-thin) solid var(--dialog-border);
                   border-radius: var(--dialog-radius); box-shadow: var(--dialog-shadow); max-width: var(--dialog-max-width); }
.surface-skeleton { background: var(--color-line); border-radius: var(--radius-sm);
                   animation: surface-skeleton-pulse calc(var(--duration-slow) * 5) var(--ease-standard) infinite; }
@keyframes surface-skeleton-pulse { 50% { opacity: var(--opacity-disabled); } }
@media (prefers-reduced-motion: reduce) { .surface-skeleton { animation: none; } }
/* Canvas, sunken, brand, bar, scrim, popover e brand-soft seguem o mesmo padrão: ver os tokens da tabela. */
```

| Faça | Não faça |
|---|---|
| Separar blocos com `border: 1px solid var(--color-line)` | Sombra grande em card ou "card flutuando" |
| Cor chapada no painel de marca | Gradiente, mesh, padrão repetido |
| Skeleton com pulso de opacidade | Shimmer (é gradiente) |
| Diálogo com `--shadow-dialog` | Diálogo sem elevação (o `shadow-card` agora é um filete) |

**Dark mode.** As mesmas classes funcionam no escuro: só a camada semântica muda. Seletores: `[data-theme="dark"]`, ou `prefers-color-scheme: dark` quando não há `data-theme="light"` (blocos idênticos).

**Tema oficial: claro** `(d)`. O `index.html` fixa `data-theme="light"`, então o app abre claro mesmo com o sistema no escuro. Os tokens escuros ficam guardados para um seletor de tema futuro. No painel de marca do login (petróleo), o logo usa a variante dark (2.3).

`::backdrop` herda variáveis do `<dialog>` só em navegadores atuais (Chrome 122+, Firefox 120+, Safari 17.4+); risco baixo.

Veja também: 03, 08 (Card, Dialog), 09 (skeleton).

## 05. Sistema tipográfico

**Decisão `(d)` Pedro Pompeu:** IBM Plex Sans + IBM Plex Mono, self-hosted via `@fontsource` (aprovado; a instalação vem depois). Sem chamada ao Google Fonts, por privacidade. Licença OFL. Os tokens já apontam para Plex primeiro, então ativar a fonte não exige mudar token algum.

| Papel | Família | Pesos | Token |
|---|---|---|---|
| Display e corpo | IBM Plex Sans | 400, 500, 600 | `--font-sans`, `--font-display` |
| Mono (trecho citado, ID do trecho, score, números de barra) | IBM Plex Mono | 400, 500 | `--font-mono` |

Fallback obrigatório até a fonte estar instalada: `ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif` e `ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace` (já incluídos em `--font-family-plex-sans` e `--font-family-plex-mono`).

### 5.1 Escala (12 níveis)

Cada nível tem quatro tokens: `--text-{nível}-size`, `-lh`, `-weight`, `-tracking`. No Tailwind: `text-h1`, `text-body-sm` etc. (tamanho + line-height + peso + tracking).

| Nível (Tailwind) | Tamanho | Line-height | Peso | Tracking | Uso |
|---|---|---|---|---|---|
| `display` | 2.25rem | 1.15 | 600 | -0.02em | Herói de página (raro) |
| `h1` | 1.875rem | 1.25 | 600 | -0.02em | Título de página |
| `h2` | 1.5rem | 1.25 | 600 | -0.01em | Título de seção |
| `h3` | 1.25rem | 1.4 | 600 | -0.01em | Título de card |
| `h4` | 1.125rem | 1.4 | 600 | 0 | Título de diálogo |
| `body` | 1rem | 1.6 | 400 | 0 | Leitura longa (currículo, justificativa) |
| `body-sm` | 0.875rem | 1.5 | 400 | 0 | UI padrão |
| `label` | 0.875rem | 1.4 | 500 | 0 | Rótulos, botões, nav |
| `caption` | 0.8125rem | 1.5 | 400 | 0 | Legendas e ajuda |
| `micro` | 0.75rem | 1.5 | 500 | 0.02em | Badges |
| `mono` | 0.875rem | 1.6 | 400 | 0 | Trecho citado |
| `mono-sm` | 0.8125rem | 1.5 | 500 | 0 | ID do trecho, score, valores de barra |

As chaves padrão do Tailwind (`text-xs` a `text-4xl`) viram alias da escala (só tamanho e line-height), então os componentes atuais não quebram. Efeito sutil: `text-sm` passa a line-height 1,5 (antes 1,43).

### 5.2 Regras

1. **Mono só para** trecho citado, ID do trecho, número do score e valores de barra. Nunca texto corrido.
2. **Números tabulares** (`font-variant-numeric: tabular-nums`) em score e valores.
3. Display sempre peso 600 com tracking negativo; **nunca** 700+ nem serifa.
4. **Sentence case** em botões, títulos, labels e menus. Sem CAIXA ALTA (prejudica a leitura de pt-BR com acentos). Evitar `uppercase` em CSS.
5. Leitura longa: `body` com medida máxima de 68ch (`--size-measure`).
6. Acentuação completa sempre; nunca ASCII-izar ("analise", "curriculo").
7. Fontes decorativas, display condensada, serifa de fantasia e script são proibidas.

### 5.3 Instalação (fase seguinte, fora desta entrega)

```bash
npm i @fontsource/ibm-plex-sans @fontsource/ibm-plex-mono
```

```ts
// main.tsx
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-sans/500.css";
import "@fontsource/ibm-plex-sans/600.css";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";
```

**Faça:** `font-mono` na citação e em `72/100`; "Score de aderência" em sentence case; `text-h2` para título de seção. **Não faça:** mono em parágrafo explicativo; "ADERÊNCIA" em caixa alta; `text-[17px]`.

Veja também: 06 (espaçamento), 08 (componentes), 12 (estilo de texto).

## 06. Espaçamento e grid

Base de 4px. Os nomes legados do Tailwind (`p-md`, `gap-lg`) foram mantidos.

| Token | Valor | px |
|---|---|---|
| `--space-2xs` | 0.25rem | 4 |
| `--space-xs` | 0.5rem | 8 |
| `--space-sm` | 0.75rem | 12 |
| `--space-md` | 1rem | 16 |
| `--space-lg` | 1.5rem | 24 |
| `--space-xl` | 2rem | 32 |
| `--space-2xl` | 3rem | 48 |
| `--space-gutter` | 1.5rem | 24 (margem lateral da página) |
| `--space-section` | 2rem | 32 (respiro vertical entre blocos) |

**Forma.** Raios: `--radius-sm` 4px (campos pequenos, tags, barras), `--radius-md` 6px (botões, inputs, alertas), `--radius-lg` 10px (cards, diálogos), `--radius-full` (badges em pílula). Bordas: `--border-width-thin` 1px (padrão do Laudo), `--border-width-accent` 3px (faixa da citação), `--border-width-ring` 2px (foco).

**Layout.**
- Largura máxima do conteúdo: `--size-container-max` 64rem (`max-w-container`).
- Medida de leitura longa: `--size-measure` 68ch (`max-w-measure`).
- Diálogo: `--size-dialog-max` 32rem.
- Padding interno de card e diálogo: `--space-lg`.
- Camadas (z-index): sticky 10, dropdown 20, overlay 30, dialog 40, toast 50.
- Densidade: linear e arejada. Muito respiro entre blocos (`--space-section`), linhas finas em vez de caixas pesadas.

**Faça:** `gap-md` entre campos, `gap-section` entre blocos, card com `p-lg` e `rounded-lg`. **Não faça:** espaços em `px` soltos (`mt-[13px]`), raios acima de 10px ou cantos totalmente redondos fora de badge.

Veja também: 04, 08.

## 07. Iconografia

**Biblioteca: Heroicons** `(d)`, pacote `@heroicons/react` (MIT), conjunto `24/outline`. Pedro escolheu entre Lucide, Tabler, Phosphor, Heroicons e Material Symbols.
- **Estilo:** linha com traço **1,5** (o padrão do Heroicons), cantos e pontas arredondados, `stroke="currentColor"`. Nada de ícone preenchido decorativo.
- **Não misture conjuntos:** `20/solid` e `16/solid` ficam fora.

**Tamanhos.**
- `--size-icon-sm` 16 px: badges, botões `sm`, campos.
- `--size-icon-md` 20 px: botões `md`, alertas, nav.
- `--size-icon-lg` 24 px: estados vazios.

Com texto ao lado, use `aria-hidden="true"`.

```tsx
import { CheckCircleIcon, MinusCircleIcon, XCircleIcon } from "@heroicons/react/24/outline";

<CheckCircleIcon className="size-4" aria-hidden="true" />
```

**Três ícones próprios** `(i)`. O Heroicons não tem "sem evidência", "citação" e "grifo", e os substitutos dele (interrogação, balão de chat e lápis) dizem outra coisa. Os três foram desenhados no mesmo grid de 24 e com traço 1,5, e ficam em `frontend/src/components/icons.tsx`:

```tsx
const base = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.5,
               strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true } as const;

export const NoEvidenceIcon = (p: React.SVGProps<SVGSVGElement>) => <svg {...base} {...p}><circle cx="12" cy="12" r="9" strokeDasharray="1.6 3.1" /><path d="M9 12h6" /></svg>;
export const QuoteIcon = (p: React.SVGProps<SVGSVGElement>) => <svg {...base} {...p}><path d="M6.75 8.25h3.5v3.5h-3.5zM10.25 11.75c0 2.5-1.25 3.75-3.5 4.25M14.25 8.25h3.5v3.5h-3.5zM17.75 11.75c0 2.5-1.25 3.75-3.5 4.25" /></svg>;
export const HighlightIcon = (p: React.SVGProps<SVGSVGElement>) => <svg {...base} {...p}><path d="M4.5 6h15M4.5 18h9" /><rect x="3.75" y="9.25" width="16.5" height="5.5" rx="1.25" /><path d="M6.75 12h10.5" /></svg>;
```

**Mapa de ícones.** Cada status tem uma forma diferente, para não depender de cor:

| Uso | Ícone | Observação |
|---|---|---|
| Atende | `CheckCircleIcon` | |
| Atende em parte | `MinusCircleIcon` | |
| Não atende | `XCircleIcon` | |
| Sem evidência | `NoEvidenceIcon` (próprio) | Repete a borda tracejada |
| Alerta: erro / aviso / sucesso / info | `ExclamationCircleIcon` / `ExclamationTriangleIcon` / `CheckCircleIcon` / `InformationCircleIcon` | Ícone obrigatório |
| Citação | `QuoteIcon` (próprio) | Opcional, ao lado do ID do trecho |
| Legenda de marca-texto | `HighlightIcon` (próprio) | Só em ajuda ou legenda, nunca em botão |
| Currículos / Vagas / Análises / Candidaturas | `DocumentTextIcon` / `BriefcaseIcon` / `DocumentMagnifyingGlassIcon` / `ViewColumnsIcon` | Navegação |
| Analisar vaga | `DocumentMagnifyingGlassIcon` | Botão primário |
| Enviar PDF | `ArrowUpTrayIcon` | |
| Apagar | `TrashIcon` | Só em ação destrutiva |
| Expandir trecho | `ChevronDownIcon` | Gira 180° |
| Voltar | `ArrowLeftIcon` | Substitui o "←" em texto |
| Fechar | `XMarkIcon` | |

**Domínio.** O símbolo da marca não vem do Heroicons: é o SVG da seção 02 e fica fora do mapa. As figuras do símbolo são abstratas e não têm rosto. Isso não libera "pessoa sorrindo" em ícone ou ilustração.

**Proibido como ícone ou ilustração:** troféu, estrela, foguete, alvo ou mira, aperto de mão, pessoa sorrindo, selo ou carimbo, emoji.

| Faça | Não faça |
|---|---|
| Ícone + rótulo "Sem evidência" | Só um círculo cinza |
| `XCircleIcon` para "Não atende" | Ícone de lixeira ou caveira para lacuna |

Veja também: 03 (vereditos), 08 (VerdictBadge, Alert).

## 08. Especificação de componentes

Convenção: nomes de token sem o prefixo `--`. `n/a` = o estado não existe para o componente, com o motivo. Anel de foco (`focus-ring`): `--focus-ring-width` 2px, offset `--focus-ring-offset`, cor `--focus-ring-color`; aplicado por `*:focus-visible`, nunca `outline: none`. "Existe" = já está no código; "alvo" = classe nova a aplicar na fase de implementação (seção 13.3).

### 8.1 Button (primary, secondary, danger, ghost, dangerGhost)

Base: `btn-radius`, `btn-gap`, texto `label` (14px/500), padding `btn-px-md` × `btn-py-md` (sm: `btn-px-sm` × `btn-py-sm`), transição `btn-transition-duration` + `btn-transition-ease`.

| Estado | Primary | Secondary | Danger | Ghost |
|---|---|---|---|---|
| default | `btn-primary-bg` / `btn-primary-text` | `btn-secondary-bg`, borda 1px `btn-secondary-border` (line-strong), `btn-secondary-text` | `btn-danger-bg` / `btn-danger-text` | transparente, `btn-ghost-text` |
| hover | `btn-primary-bg-hover` | borda `btn-secondary-border-hover`, texto `btn-secondary-text-hover` | `btn-danger-bg-hover` | `btn-ghost-bg-hover`, `btn-ghost-text-hover` |
| active | `btn-primary-bg-active` (alvo) | `btn-secondary-bg-active` (alvo) | `btn-danger-bg-active` (alvo) | `btn-ghost-bg-active`, `btn-ghost-text-active` (alvo) |
| focus | anel de foco | anel de foco | anel petróleo (não vermelho) | anel de foco |
| disabled | `btn-disabled-opacity`, `cursor-not-allowed` | idem | idem | idem |
| loading | Spinner 16px + rótulo, `aria-busy` | idem | idem (usado no `ConfirmDialog tone="danger"`) | idem |
| error | n/a: a falha vira `Alert` error acima do formulário | n/a | n/a | n/a |
| success | n/a: sem estado persistente; confirmação por `Alert` success ou navegação | n/a | n/a | n/a |

`dangerGhost` (variante do código): `btn-danger-ghost-text`, hover `btn-danger-ghost-bg-hover`, pressionado `btn-danger-ghost-text-active`. Foco, disabled e loading como o ghost. Alvo no loading: manter 100% de opacidade com `cursor-progress`.

### 8.2 Input, Textarea e Select

Base: `field-bg`, borda 1px, `field-radius`, padding `field-px` × `field-py`, texto `body-sm`. Textarea: `resize-y`, 10 linhas. Select: chevron `chevron-down` 16px em `muted`.

- **default:** `field-bg`, borda `field-border` (= line-strong, 3,19:1), texto `field-text`, placeholder `field-placeholder`. Alvo: `border-line-strong` (hoje `border-line`).
- **hover:** borda `field-border-hover`.
- **active (digitando):** igual ao foco; sem estado "pressionado" distinto.
- **focus:** borda `field-border-focus` + anel de foco.
- **disabled:** `field-bg-disabled`, texto `field-text-disabled`, `cursor-not-allowed`.
- **loading:** só Select com opções assíncronas: `aria-busy`, texto "Carregando…", Spinner 16px.
- **error:** borda `field-border-error`, ícone `circle-alert` e mensagem em `caption` (`field-error-text`) abaixo, ligada por `aria-describedby`; `aria-invalid`.
- **success:** borda `field-border-success`, ícone `circle-check`. Raro: só validação assíncrona concluída.

### 8.3 Badge (tons genéricos)

Pílula (`badge-radius`), `micro` (12px/500), padding `badge-px` × `badge-py`. Tons: neutral, brand, success, warning (terracota), danger. Pares `badge-{tom}-bg` / `badge-{tom}-text`.
- **default:** o tom escolhido. **hover/active/focus:** n/a, não interativo (para filtro ou chip use Button ghost; se envolvido em link, o foco é do envolvente).
- **disabled:** tom atual com `opacity-disabled`; uso raro.
- **loading:** pílula `surface-skeleton` do mesmo tamanho.
- **error:** tom danger. **success:** tom success.

### 8.4 VerdictBadge (novo)

Veredito do requisito. **Sempre ícone + texto.** Raio `verdict-badge-radius` (4px, para se distinguir da pílula), borda 1px, ícone `verdict-badge-icon-size` 16px.

- **default:** quatro formas (cores e ícones na seção 3.3). `no-evidence` tem borda tracejada.
- **hover/active/focus:** n/a, não interativo; se virar filtro, `aria-pressed`. O foco é do contêiner.
- **disabled:** n/a, veredito não se desabilita.
- **loading:** pílula `surface-skeleton` com `aria-busy` na lista (análise `pending` ou `running`).
- **error:** n/a. Falha da análise vira `ErrorState` ou `Alert`; `not_met` não é "erro".
- **success:** n/a. `met` é o resultado, não um estado de UI.
- **Regra de dados:** o componente recebe `hasEvidence`; `met` sem `evidence[]` renderiza `no-evidence`. Quem decide é o dado, não a cor.

### 8.5 ScoreBadge (novo)

Texto `72/100` em `mono-sm` (500, `tabular-nums`). **Nunca** semáforo, anel, gauge ou % gigante. Fundo `color-score-bg`, borda 1px `color-score-border`, texto `color-score-text` (petróleo-800). Rótulo visível "Score de aderência" acima, em `caption`; rótulo acessível "Score de aderência: 72 de 100".

- **default:** como acima. **hover/active/focus/disabled:** n/a (não interativo; o foco é do contêiner).
- **loading:** `surface-skeleton` com a largura de "00/100" em mono.
- **error:** score `null`: mostra "—/100" na forma `no-evidence` (neutra, tracejada), sem cor de falha.
- **success:** n/a. O score **não muda de cor por faixa**.

### 8.6 EvidenceQuote (novo)

O núcleo do produto. Anatomia: bloco `evidence-quote-bg` com faixa lateral de 3px `evidence-quote-border`; citação em mono entre aspas curvas com marca-texto `evidence-quote-mark` (só no texto, `box-decoration-break: clone`); legenda com o ID do trecho em `mono-sm` (`evidence-quote-meta`); `summary` "Ver trecho N completo" com `chevron-down` que gira 180° em `evidence-quote-expand-duration`. Medida de leitura `evidence-quote-measure` (68ch). Estrutura: `<blockquote>` + `<details>`.

**ID do trecho `(i)`:** a legenda é "Currículo · trecho N" (ordinal + 1). Nunca o UUID; o ID bruto só em tooltip técnico.

- **default (recolhido):** bloco, faixa, citação com marca-texto, legenda.
- **hover/active:** só o `summary` reage (`btn-ghost-text-hover`, sublinhado; pressionado `btn-ghost-text-active`). O bloco não é link.
- **focus:** anel de foco no `summary`.
- **expandido:** trecho completo em `color-sunken` com borda `color-line`, texto `body-sm`/`mono-sm` em `color-muted`; a citação mantém a marca-texto; duração `motion-duration-base`.
- **disabled:** n/a, evidência é leitura.
- **loading:** 2 linhas `surface-skeleton`, `aria-busy`, sem shimmer.
- **error (trecho não encontrado):** forma `no-evidence` (neutra, tracejada), "Trecho indisponível". **Nunca vermelho.**
- **success:** n/a. A citação encontrada é o estado normal.

Escuro: marca-texto vira âmbar a 20% de opacidade sobre bloco a 8%, texto grafite-50, ID âmbar-300.

### 8.7 Card

`card-bg`, borda 1px `card-border`, `card-radius` (10px), `card-shadow` (filete), `card-padding`.
- **default:** como acima. **hover:** `card-border-hover`; só card clicável, sem elevação nem translate. **active:** fundo `color-sunken`. **focus:** anel no elemento focável (`:focus-within`).
- **disabled:** `opacity-disabled`, texto muted (raro). **loading:** blocos `surface-skeleton`, `aria-busy`.
- **error:** borda `field-border-error`; prefira `ErrorState` ou `Alert` dentro do card. **success:** borda `field-border-success` (raro; prefira `Alert`).

### 8.8 Alert

`role="alert"` para erro, `role="status"` para os demais. Raio `alert-radius`, padding `alert-px` × `alert-py`. **Ícone obrigatório:** error `circle-alert`, success `circle-check`, info `info`, warning `triangle-alert`.
- **default (4 tons):** `alert-{error|success|info|warning}-{bg|border|text}`. Warning é terracota, nunca âmbar. Info usa petróleo.
- **hover/active/disabled:** n/a, não interativo. **focus:** anel nos controles internos (botão fechar, link).
- **loading:** `color-sunken` + Spinner, tom info ("analisando…"), não esqueleto.
- **error/success:** são os próprios tons.

### 8.9 Dialog (`ConfirmDialog`)

`<dialog>` nativo: `dialog-bg`, borda `dialog-border`, `dialog-radius`, sombra `dialog-shadow`, largura `dialog-max-width`, padding `dialog-padding`, fundo `dialog-backdrop`. Título `h4`, descrição `body-sm` em muted. Ações: secondary (cancelar) + primary ou danger (confirmar).
- **default:** entrada com `motion-duration-slow` + `motion-ease-enter` (alvo); instantânea em reduced motion.
- **hover/active:** n/a no contêiner; os botões reagem. **focus:** foco inicial no primeiro controle ou `initialFocusRef`; Esc fecha (bloqueado durante `isConfirming`).
- **disabled:** durante `isConfirming`, Cancelar fica `disabled` e clique no fundo não fecha. **loading:** botão de confirmar com Spinner.
- **error:** `Alert` error dentro do corpo; o diálogo não fecha em falha. **success:** fecha e confirma fora (Alert ou navegação).

### 8.10 Nav link (`NavLink`)

`label` (14px/500), `nav-link-radius`, padding `nav-link-px` × `nav-link-py`; página atual por `aria-current="page"`.
- **default:** `nav-link-text`. **hover:** `nav-link-bg-hover` + `nav-link-text-hover`. **active (página atual):** `nav-link-bg-current` + `nav-link-text-current`, **sem depender só de cor** (manter peso 500 e, no alvo, sublinhado de 2px em brand).
- **focus:** anel de foco. **disabled:** `aria-disabled` com `opacity-disabled` (raro).
- **loading/error/success:** n/a. A navegação não tem loading no link; o carregamento fica na página.

### 8.11 Exemplo: VerdictBadge

```tsx
export function VerdictBadge({ verdict, hasEvidence }: { verdict: "met" | "partial" | "not_met"; hasEvidence: boolean }) {
  const key = verdict === "met" && !hasEvidence ? "no-evidence" : verdict.replace("_", "-");  // "Atende" só com citação
  const { label, Icon } = VIEW[key];            // VIEW mapeia rótulo e ícone (seção 07)
  return (
    <span className={`inline-flex items-center gap-2xs rounded-sm border px-xs py-2xs text-micro
      bg-verdict-${key}-bg text-verdict-${key}-text border-verdict-${key}-border ${key === "no-evidence" ? "border-dashed" : ""}`}>
      <Icon className="size-4" /> {label}
    </span>
  );
}
```

Nota: classes montadas por template não são detectadas pelo Tailwind; no código real liste as quatro classes completas (safelist ou mapa de strings).

Veja também: 03, 07, 09, 12 (rótulos).

## 09. Motion e animação

**Princípios.** Movimento só para indicar mudança de estado ou atividade. Curto, funcional, sem decoração. Nada de confete, bounce, parallax ou shimmer (gradiente é proibido). Tudo respeita `prefers-reduced-motion`.

| Grupo | Tokens | Valores |
|---|---|---|
| Duração | `--motion-duration-fast / base / slow` | 120 / 200 / 320 ms |
| Easing | `--motion-ease-standard / enter / exit / linear` | `cubic-bezier(0.2,0,0,1)` / `(0,0,0,1)` / `(0.3,0,1,1)` / `linear` |
| Spinner | `--motion-duration-spin` | 1s |
| Reduced motion | as três durações | 0.01ms (spinner passa a 2,4s: lento, mas indica atividade) |

**Animações definidas:**

| Nome | Onde | Duração / curva |
|---|---|---|
| Transição de estado | hover, foco, cor | `fast` + `standard` (o `transition-*` do Tailwind já usa os tokens) |
| Expandir trecho | chevron 180° e `<details>` | `base` + `standard` |
| Preencher barra | largura de 0 até o valor | `slow` + `enter` |
| Entrada do diálogo | `<dialog>` | `slow` + `enter` |
| Spinner | `animate-spin` | `spin` + `linear` |
| Skeleton | pulso de opacidade (não shimmer) | `duration-slow × 5` + `standard`; estático em reduced motion |

Exemplo: `<div className="transition-colors duration-fast ease-standard hover:bg-brand-soft" />`.

**Faça:** animar `width` da barra uma vez, ao montar; manter o spinner lento em reduced motion. **Não faça:** animar números contando até o score; parar o spinner (some o sinal de atividade).

Veja também: 08, 10.

## 10. Visualização de dados

**Escopo.** O produto tem uma visualização: as barras do `breakdown` do score. Dados: `breakdown = { required: number | null; nice_to_have: number | null }`, fração de 0 a 1; `null` quando a vaga não tem requisitos daquele tipo. No máximo **2 barras**: "Obrigatórios" e "Diferenciais".

**Regras do Laudo:**
1. **Só petróleo.** Sem âmbar (é evidência), sem verde ou vermelho (é veredito), sem gradiente, sem semáforo por faixa. As duas barras usam o mesmo `--bar-fill`; o rótulo as diferencia.
2. Sem gauge, anel, velocímetro ou % gigante. O valor fica pequeno, em mono, à direita.
3. Escala fixa de 0 a 100% em todas as linhas. Sem eixos nem grade; só o trilho.
4. O valor numérico sempre aparece (a barra não é o único portador do dado).
5. Valor escrito: **"4 de 6 com evidência"** (contado em `requirements[]` por `kind`). O percentual só define o comprimento.
6. `null`: trilho tracejado (`--bar-empty-border`), sem preenchimento, texto "A vaga não lista" em muted.
7. Tiers extras (se o produto crescer): `--bar-fill-secondary`, `--bar-fill-emphasis`; no máximo 3 tons, sempre com rótulo.

**Cores:** claro: trilho grafite-100, fill petróleo-600 (6,45:1 contra o trilho), tier 2 petróleo-400 (3,09:1), tier 3 petróleo-800. Escuro: trilho grafite-900, fill petróleo-300 (7,53:1), tier 2 petróleo-500 (3,03:1), tier 3 petróleo-100.

```html
<ul class="breakdown">
  <li class="breakdown__row">
    <span class="breakdown__label">Obrigatórios</span>
    <span class="breakdown__track" role="img" aria-label="Obrigatórios: 4 de 6 com evidência">
      <span class="breakdown__fill" style="--value: 0.67"></span>
    </span>
    <span class="breakdown__value">4 de 6 com evidência</span>
  </li>
  <li class="breakdown__row breakdown__row--empty">
    <span class="breakdown__label">Diferenciais</span>
    <span class="breakdown__track" role="img" aria-label="Diferenciais: a vaga não lista"></span>
    <span class="breakdown__value">A vaga não lista</span>
  </li>
</ul>
```

```css
.breakdown { display: grid; gap: var(--space-sm); list-style: none; margin: 0; padding: 0; }
.breakdown__row { display: grid; grid-template-columns: minmax(0, 8rem) minmax(0, 1fr) auto;
                  align-items: center; gap: var(--space-md); }
.breakdown__label { font: var(--text-label-weight) var(--text-label-size)/var(--text-label-lh) var(--font-sans); color: var(--bar-label-text); }
.breakdown__track { height: var(--bar-height); border-radius: var(--bar-radius); background: var(--bar-track); overflow: hidden; }
.breakdown__fill { display: block; height: 100%; width: calc(var(--value) * 100%); background: var(--bar-fill);
                   border-radius: var(--bar-radius); transition: width var(--bar-grow-duration) var(--bar-grow-ease); }
.breakdown__value { font: var(--text-mono-sm-weight) var(--text-mono-sm-size)/var(--text-mono-sm-lh) var(--bar-value-font);
                    font-variant-numeric: tabular-nums; color: var(--bar-value-text); text-align: right; }
.breakdown__row--empty .breakdown__track { background: transparent; border: var(--border-width-thin) dashed var(--bar-empty-border); }
```

Nota: `8rem` (coluna do rótulo) e o ponto de quebra mobile (`40rem`, trilho em linha própria abaixo disso) são valores de layout deste exemplo e não têm token; veja a sugestão em 14.4.

**Faça:** "Obrigatórios: 4 de 6 com evidência", barras na mesma cor com rótulo. **Não faça:** "67%" gigante sozinho; verde para alto e vermelho para baixo.

Veja também: 03, 08 (ScoreBadge), 09.

## 11. Imagens e fotografia

O VagaFit não usa fotografia. Esta seção deriva das proibições da ARIA e das restrições da ECHO; não há direção própria de imagem na fundação. É uma **sugestão (i) da NOVA**, aguardando confirmação (ver 14.4).

**Estilo.** O visual do produto é a própria interface: capturas de tela do app, diagramas e dados. Imagens sempre claras, planas, com linhas de 1px, nas cores da marca.

**Material permitido:**
- Capturas de tela do app com dados fictícios (persona **Ana Exemplo**), no tema claro por padrão.
- Diagrama Mermaid do fluxo e GIF curto da análise no README.
- Social preview do GitHub (1280×640 px, requisito do GitHub `(e)`): fundo canvas Sálvia `#DAE4DC`, lockup light, a tagline "Cada ponto, com prova." em Plex Sans 600 e, abaixo e menor, "Vaga × currículo, requisito por requisito. Sem prova, é lacuna.". Sem foto, sem ilustração, sem gradiente.

**Privacidade.** Currículo é dado pessoal. Nunca use currículo real em captura, GIF, README ou social preview. Marque o exemplo como fictício.

**Proibido** (e nenhum overlay colorido, blur ou gradiente sobre imagem): foto de banco de imagem; pessoa sorrindo; aperto de mão; troféu, estrela, foguete, alvo; ilustração decorativa; mockup de laptop com brilho; emoji; glow; glassmorphism; fundo escuro como padrão.

| Faça | Não faça |
|---|---|
| Captura do resultado da Ana Exemplo | Captura com currículo ou e-mail reais |
| Âmbar só no trecho citado | Âmbar como destaque genérico do print |

Veja também: 02 (lockup), 12 (texto do preview).

## 12. Voz e mensagens da marca

### 12.1 Perfil de voz

**Direto · Honesto · Técnico · Específico.**

| Traço | Em uma frase | Na prática |
|---|---|---|
| Direto | Diz o resultado antes da explicação | Frase curta, sujeito claro, verbo ativo. Sem preâmbulo |
| Honesto | Nunca promete o que não pode provar e nunca suaviza lacuna | "Sem evidência" e "Não atende" sempre com as mesmas palavras. Admite o limite: lê o currículo, não a pessoa |
| Técnico | Fala de dev para dev | Termo certo (trecho, requisito, citação, stack, score), sem didatismo nem jargão de marketing |
| Específico | Apontar vale mais que adjetivar | Número, nome do requisito, trecho citado, causa do erro |

Estilo: frases de 8 a 18 palavras; uma ideia por frase; sem metáfora; sem exclamação; voz ativa; "você" para a pessoa; o produto como sujeito quando precisar de agente.

### 12.2 Tom por contexto

| Contexto | Tom |
|---|---|
| Marketing (README, social) | Confiante por demonstração, não por adjetivo. Mostra o mecanismo (trecho real, diagrama, decisão de engenharia). A tagline abre; a segunda linha explica; a stack vem por último, como lista seca |
| Produto (UI) | Preciso e neutro, como documentação. Rótulos curtos, números exatos, nenhuma celebração; aponta o próximo passo quando existe |
| Erros e suporte | Calmo e concreto: **o que aconteceu + o que fazer**. Não culpa, não pede desculpas em série. Se repetir não adianta, diz isso |
| Resultado de análise | Como um bom comentário de code review: fala do artefato, não da pessoa |

**Como dizer "Não atende" e "Sem evidência":**
1. O sujeito é o currículo (ou a análise), nunca a pessoa: "O currículo não cobre este requisito."
2. Mesmo rótulo sempre. Os quatro vereditos têm um nome só. Sem "Quase lá" nem "Oportunidade".
3. Zero amortecedores ("infelizmente", "ainda", "parece que", "quase", "talvez") e zero adjetivo de valor (não é "fraco" nem "forte"; é o fato).
4. Próximo passo permitido, consolo não. Sempre "Se você tem essa experiência, adicione ao currículo e refaça a análise." Nunca sugerir inventar.
5. Lacuna tem o mesmo peso tipográfico dos outros itens: nem grito vermelho, nem cinza escondido.

**Vereditos (rótulo + frase de apoio):**

| Veredito | Rótulo | Frase de apoio |
|---|---|---|
| `met` com citação | **Atende** | A citação vem logo abaixo. |
| `partial` | **Atende em parte** | Parte do requisito tem citação. O que falta: {resto do requisito}. |
| `not_met` | **Não atende** | O currículo não cobre este requisito. |
| `met` sem citação | **Sem evidência** | Nenhum trecho do currículo comprova este item. |

Frase opcional para `Sem evidência`: "A análise marcou como atendido, mas não achamos citação no currículo. Não contamos como atendido."

### 12.3 Anti-patterns (15)

Evite, com o exemplo ruim entre parênteses: 1 linguagem de garantia ("Match garantido de 92%"); 2 elogio vazio ("Seu perfil é incrível!"); 3 lacuna suavizada ("Quase lá!"); 4 lacuna dramatizada ("Você não tem experiência em Kubernetes."); 5 score como nota de valor ("Excelente aderência"); 6 erro genérico ("Algo deu errado.", "Ops!"); 7 retry onde retry não ajuda (cota esgotada com "Tente de novo"); 8 hype de IA ("Nossa IA mágica"); 9 exclamação e emoji; 10 cor sem texto ("Verde = bom"); 11 verbos diferentes para a mesma ação ("Cadastrar currículo" × "Novo currículo"); 12 sugerir que a pessoa invente ("Adicione essa skill para subir o score"); 13 "nós" corporativo ("Estamos trabalhando para melhorar sua experiência"); 14 hedge no veredito ("Parece que talvez atenda"); 15 celebrar no vazio ("Boa sorte na entrevista!").

### 12.4 Nunca diga / sempre diga

**Nunca:** "garantido", "match perfeito" (banidas pelo brief) e a família "100% compatível", "perfeito", "ideal"; promessa de resultado ("aumente suas chances", "passe no ATS", "seja contratado", "garanta a entrevista"); elogio vazio ("parabéns!", "ótimo currículo"); atenuador ("infelizmente", "ainda não", "quase atende", "ponto de atenção"); hype ("revolucionário", "mágica", "turbine"); culpa ou drama ("Ops", "Algo deu errado", "Erro fatal"); "match" sozinho, "nota" do candidato, "pontuação do seu perfil"; "Excluir", "Deletar" ou "Remover" para apagar dados; qualquer previsão sobre o futuro do candidato.

**Sempre:** o requisito pelo texto da vaga e a evidência pelo trecho do currículo, entre aspas; "Sem evidência" e "Não atende" pelo nome; "Rascunho. Revise antes de enviar."; o número exato (72/100, 3 de 8, 5 MB); causa e ação em erros; o limite do produto quando importa ("O VagaFit lê o seu currículo, não a sua carreira.").

### 12.5 Hierarquia de mensagem

| Nível | Mensagem |
|---|---|
| 1 Categoria | Aderência entre vaga e currículo, com evidência. |
| 2 Promessa | Saiba onde vale se candidatar e o que destacar, sem inventar nada. |
| 3 Prova | A vaga é comparada ao currículo requisito por requisito. Cada "Atende" cita o trecho do currículo que o sustenta; o que não tem prova aparece como lacuna. Os rascunhos de triagem usam só fatos do currículo e marcam o que precisa de você. As candidaturas ficam num funil, do envio à proposta. |
| 4 CTA | Analisar uma vaga. (Para o recrutador técnico: Ver como a evidência é verificada.) |

Superfícies: o social preview lidera com a tagline e o nível 1 ("Vaga × currículo, requisito por requisito."); o README abre com os níveis 2 e 3 e detalha o nível 3 na seção técnica; a lateral do login usa a tagline e o nível 3 curto ("Compare a vaga com o currículo, requisito por requisito. O que não tem prova vira lacuna."); o rodapé do app usa o nível 1 ("VagaFit · aderência entre vaga e currículo, com evidência").

### 12.6 Taglines

**Tagline principal `(d)`: "Cada ponto, com prova."** Linha de apoio `(d)`: **"Sem prova, é lacuna."** Use a principal sempre acompanhada de um descritor que fecha a ambiguidade de "ponto" (ex.: "Compare a vaga com o currículo, requisito por requisito. O que não tem prova vira lacuna.").

Alternativas avaliadas pela ECHO (registro; não são oficiais): "Sem prova, é lacuna." (7,5/10, abre pelo negativo; virou linha de apoio), "Atende só com citação." (7/10, boa na seção técnica do README), "Decida a candidatura pela evidência, não pelo chute." (6,5/10, longa) e "Onde aplicar, sem chute." (6/10, não carrega a diferenciação). "Cada ponto, com prova." recebeu 8/10; o limite é a ambiguidade de "ponto", resolvida pelo descritor.

### 12.7 Biblioteca de microcopy (resumo)

Convenções completas em 12.8. Aqui, o par "ruim → bom" dos casos principais.

**CTAs**

| Contexto | Ruim | Bom |
|---|---|---|
| Botão do formulário de análise | Analisar | **Analisar vaga** |
| Entrada de análise | Fazer primeira análise | **Nova análise** (cabeçalho) · **Criar primeira análise** (vazio) |
| Currículo | Novo currículo / Cadastrar currículo | **Adicionar currículo** (submit: **Salvar currículo**) |
| Vaga | Nova vaga / Cadastrar vaga | **Colar vaga** |
| Triagem | Gerar rascunhos | **Gerar rascunho de triagem** (1) · **Gerar rascunhos de triagem** (2+) |
| Candidatura | Nova candidatura | **Registrar candidatura** (em todo lugar) |
| Retry | Tentar novamente | **Tentar de novo** (forma única) |
| Conta | Apagar conta | **Apagar minha conta** (gatilho) · **Apagar conta e todos os dados** (confirmação) |

**Estados vazios** (título ≤ 5 palavras; texto; botão)

| Tela | Título | Texto | Botão |
|---|---|---|---|
| Currículos | Nenhum currículo ainda. | A análise cita trechos do seu currículo como prova. Cole o texto ou envie um PDF. | Adicionar currículo |
| Vagas | Nenhuma vaga ainda. | Cole o texto de uma vaga. O VagaFit extrai os requisitos e você confere a lista antes de analisar. | Colar vaga |
| Análises | Nenhuma análise ainda. | Escolha um currículo e uma vaga. Cada requisito volta com o trecho do currículo que o comprova, ou como lacuna. | Criar primeira análise |
| Candidaturas | Nenhuma candidatura registrada. | Registre as vagas em que você se candidatou e acompanhe cada etapa, do envio à proposta. | Registrar candidatura |

**Erros** (o que aconteceu + o que fazer)

| Contexto | Texto |
|---|---|
| Login inválido | E-mail ou senha incorretos. |
| Cota de IA esgotada | A cota de IA acabou. Tentar de novo agora repete o erro. A análise volta a funcionar quando a cota renovar. |
| IA indisponível | O provedor de IA não respondeu. Nada foi salvo. Tente de novo em alguns minutos. |
| IA citou o que não existe | A resposta da IA citou trechos que não estão no currículo e foi descartada duas vezes. Nenhuma análise foi gerada. Tente de novo. |
| PDF ilegível | Não foi possível extrair texto deste PDF. Ele pode estar protegido por senha ou corrompido. Cole o texto do currículo no lugar. |
| PDF escaneado (sem texto selecionável) | O PDF não tem texto selecionável (talvez seja escaneado). Cole o texto do currículo. `(e)` `backend/app/services/pdf.py`, 2026-11-02 |
| Sessão expirada (tela de login) | Sua sessão expirou. Entre de novo para continuar. `(d)` 2026-11-02; só quando o refresh falha, nunca no logout |
| Aviso ao adicionar currículo (LGPD) | O VagaFit guarda o título, o texto e os trechos do currículo; o arquivo PDF não fica salvo. Para dividir e analisar, o texto é enviado a um provedor de IA externo. Apagar a conta remove currículos, vagas, análises e candidaturas. `(d)` 2026-11-02 |
| PDF acima do limite | O arquivo tem 7,2 MB e o limite é 5 MB. |

**Loading:** "Comparando o currículo com cada requisito. A página atualiza sozinha." · "Extraindo os requisitos da vaga…" · "Escrevendo os rascunhos a partir do seu currículo. Pode levar alguns segundos." · "Carregando currículos…" (reticências com o caractere único **…**).

**Sucesso:** "Currículo salvo. 12 trechos prontos para citação." · "Vaga lida. 9 requisitos extraídos: 6 obrigatórios e 3 diferenciais." · "Análise concluída. 3 lacunas em 8 requisitos." · "2 rascunhos prontos. 1 precisa da sua resposta." · "Candidatura registrada em Enviada." · "Conta apagada. Currículos, vagas e análises foram removidos."

**Score:** rótulo **Score de aderência**; número **72/100** (mono, badge neutro); apoio: "Resume o quanto o currículo comprova os requisitos desta vaga. Obrigatórios pesam mais. Não avalia você." (`(d)` 2026-11-02; a frase anterior, "Resume quantos requisitos desta vaga o currículo comprova. Não avalia você.", fica `~superseded 2026-11-02`, porque o score pondera obrigatórios 70% × diferenciais 30% e "Atende em parte" vale metade) Barras: "Obrigatórios: 4 de 6 com evidência." · "Diferenciais: a vaga não lista."

**Evidência:** título "Evidência no currículo (2)" (forma única); citação entre “aspas curvas” com legenda *Currículo · trecho 3*; link "Ver trecho 3 completo"; sem citação: "Nenhum trecho do currículo comprova este item."; avisos "Só reformulam o que já está no currículo. Nenhum fato novo entra." e "As respostas são rascunhos baseados só no seu currículo: revise antes de enviar."

### 12.8 Glossário e regras de estilo

| Conceito | Use | Evite |
|---|---|---|
| Análise | análise | match, avaliação, relatório |
| Requisito | requisito | skill, exigência, critério |
| Evidência | evidência (o trecho citado), citação (o texto entre aspas), trecho | prova (só na tagline), snippet, chunk |
| Lacuna | lacuna | gap (só em código), ponto fraco, oportunidade |
| Triagem | pergunta/rascunho de triagem | screening, formulário |
| Candidatura | candidatura; "se candidatar" | application, aplicação |
| Score | score (rótulo: "score de aderência") | nota, pontuação, % de compatibilidade |
| Obrigatório / Diferencial | obrigatório / diferencial | must-have / nice-to-have |
| Rascunho | rascunho | resposta pronta, resposta final |
| Apagar | apagar (conta, currículo, vaga) | excluir, deletar, remover |
| Funil | funil | pipeline, kanban |

Mapa de vocabulário de código para tela: `met` Atende · `partial` Atende em parte · `not_met` Não atende · sem citação Sem evidência · `chunk` trecho · `gap` lacuna · `breakdown.required` Obrigatórios · `breakdown.nice_to_have` Diferenciais. Na interface e na copy **nunca se cita cor**; fala-se do significado.

**Estilo:** frase completa termina com ponto; botão, rótulo, título, badge e item de menu sem ponto final; sem exclamação em produto; reticências `…`; aspas curvas “ ” na citação; separador ` · `; formato pt-BR (vírgula decimal, ponto de milhar, "5 MB", dd/mm/aaaa, "R$ 9.000"); score sempre `72/100`; contagens em algarismos com pluralização correta; sentence case; nome **VagaFit**; "você" (nunca "o usuário" na UI); botão em infinitivo, instrução em imperativo de "você"; acentuação completa; "e-mail" e "pré-visualizar" com hífen; título de empty state ≤ 5 palavras, erro ≤ 2 frases, botão ≤ 3 palavras.

### 12.9 Restrições e limites (seção 12 do brief)

> Proposta `(i)` da ECHO `~superseded 2026-11-02`: **aprovada por Pedro Pompeu `(d)` em 2026-11-02**, inteira. Os antigos [confirmar] foram resolvidos assim: claims de privacidade só os confirmados no código (o aviso de LGPD da seção 12.7); provedor de IA externo informado na tela de novo currículo; aviso de demo com cota fica para quando houver deploy público.

- **Idioma e registro.** Toda a copy do produto, do README e do social preview em pt-BR com acentuação completa. Mensagens técnicas do OpenAPI/Swagger podem ficar em inglês; rótulos de interface nunca. Registro de dev para dev, em "você", nunca institucional.
- **Palavras e promessas proibidas.** "garantido", "match perfeito" (brief) e a família listada em 12.4. Nenhuma frase prevê o resultado de uma candidatura.
- **Limites de afirmação.** O VagaFit avalia o **currículo**, não a pessoa. "Evidência verificada" significa que a **citação existe no trecho do currículo** (cópia literal); não significa que a interpretação da IA esteja correta. "Atende" só aparece com citação ao lado. Sugestões e rascunhos usam só fatos do currículo; qualquer ação de correção começa com "se você tem essa experiência". Todo texto de IA é rotulado **rascunho**. O score é um resumo, não uma nota. Claims de privacidade só entram se confirmados no código.
- **Honestidade de portfólio.** O README e a demo dizem que é projeto de portfólio com demo pública e cota de IA limitada, antes de a cota esgotar (vale a partir do deploy público). Sem números de usuários ou empresas inexistentes. Métricas só de teste e engenharia. Sem comparação nominal com produtos de terceiros.
- **Limites de marca.** Sem emoji, confete, troféu, estrela, foguete, alvo, aperto de mão; sem selo ou carimbo ("Aprovado", "Certificado", "Verificado" como carimbo). Âmbar é exclusivo da evidência. Status nunca depende só de cor.
- **Dados e LGPD.** Onde coleta currículo, o texto diz o que é guardado e que apagar conta remove currículos, vagas e dados vinculados. Currículo é dado pessoal: exemplos públicos usam currículo fictício, marcado como tal. Informar que o conteúdo é enviado a um provedor de IA externo.
- **Acessibilidade da linguagem.** Frases curtas; `aria-label` acompanha o rótulo visível ("Score de aderência: 72 de 100"); datas e números em pt-BR.

Veja também: 03 (vereditos), 08 (rótulos nos componentes), 13 (exemplos).

## 13. Exemplos de aplicação

### 13.1 Exemplo completo: resultado da Ana Exemplo

Dados **fictícios**. Persona: Ana Exemplo, desenvolvedora backend. Vaga fictícia: "Desenvolvedora Backend Pleno · Empresa Exemplo".

```
Análise · Desenvolvedora Backend Pleno · Empresa Exemplo         Score de aderência  [ 72/100 ]
                                                                 Resume quantos requisitos desta
Obrigatórios   ████████████░░░░░░  4 de 6 com evidência          vaga o currículo comprova.
Diferenciais   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄  A vaga não lista                Não avalia você.

[Atende]  Experiência com Python e FastAPI
  ▌“Construí uma API de pagamentos em FastAPI com PostgreSQL e filas.”
  ▌Currículo · trecho 3                          Ver trecho 3 completo

[Atende em parte]  Mensageria em produção
  ▌“Consumidores de fila para conciliação diária.”   Currículo · trecho 5
  Parte do requisito tem citação. O que falta: operação em produção com alta vazão.

[Não atende]  Experiência com Kubernetes
  O currículo não cobre este requisito.
  Se você tem essa experiência, adicione ao currículo e refaça a análise.

[Sem evidência]  Testes de carga
  Nenhum trecho do currículo comprova este item.
```

Notas: o score está em badge neutro de petróleo com `72/100` em mono, sem semáforo. A marca-texto âmbar aparece **só** dentro das citações. Cada veredito tem ícone e texto. Os trechos usam "Currículo · trecho N", nunca UUID.

### 13.2 Prompts para o Claude Code

Pontos de partida; ajuste o escopo. **Criar um componente**
```
Leia BRAND.md (seções 03, 07, 08) e brand/design-tokens.css. Crie o componente <VerdictBadge> conforme a
seção 8.4: ícone + texto sempre; "Atende" só com hasEvidence; use apenas classes do Tailwind que leem
tokens (nada de hex ou px soltos). Cubra os estados da especificação e escreva testes para a regra
met-sem-citação => "Sem evidência".
```

**Revisar uma tela contra a marca**
```
Leia BRAND.md e revise src/pages/AnalysisResultPage.tsx. Aponte: cores fora dos tokens, âmbar fora de
evidência, status só por cor, score com semáforo, mono em texto corrido, copy fora da seção 12 (verbos,
rótulos, palavras banidas). Liste achado, arquivo, linha e correção. Não edite ainda.
```

**Escrever copy**
```
Leia BRAND.md seção 12. Escreva o empty state e as 3 mensagens de erro da tela de vagas: o que aconteceu +
o que fazer, sentence case, sem exclamação, vocabulário do glossário (12.8). Não use as palavras da lista
"Nunca diga". Use a persona fictícia Ana Exemplo em qualquer exemplo.
```

**Gerar o README / social preview**
```
Leia BRAND.md (02, 11, 12.5). Monte o texto do README: tagline, descritor, 3 pontos de prova, stack em
lista seca. Use "Cada ponto, com prova." e "Sem prova, é lacuna.". Nenhum dado real de currículo.
```

### 13.3 Checklist de implementação (fase seguinte, fora do escopo deste documento)

Aplicação no código do front-end, a executar depois da revisão humana. Aplicado em 2026-11-01 (marca v1.2):

- [x] Substituir `frontend/src/styles/tokens.css` por `brand/design-tokens.css` (o `index.css` já faz `@import "./tokens.css"`).
- [x] Substituir `tailwind.config.js` por `brand/tailwind.config.ts`.
- [x] Trocar `border-line` por `border-line-strong` em Input, Textarea, Select e na variante `secondary` do Button (WCAG 1.4.11).
- [x] Trocar `shadow-card` por `shadow-dialog` no `ConfirmDialog`.
- [x] Score neutro: remover `scoreTone` (semáforo) e criar `ScoreBadge` com `72/100` em mono.
- [x] Criar `VerdictBadge` com a regra `met` sem citação => "Sem evidência" em tom neutro tracejado (hoje é aviso).
- [x] Criar `EvidenceQuote` (mono, marca-texto, faixa lateral, "Currículo · trecho N") e usá-lo no `EvidenceList`.
- [x] Alert: adicionar ícone por variante (status nunca só por cor).
- [x] `index.css`: usar `--focus-ring-width`, `--focus-ring-color`, `--focus-ring-offset` no `:focus-visible`; remover `html { color-scheme: light }`.
- [x] Aplicar a copy da ECHO: cota esgotada, "Sem evidência", "Score de aderência", verbos unificados, textos de marca do login e do rodapé, mensagem de conta apagada.
- [x] Instalar `@fontsource/ibm-plex-sans` e `@fontsource/ibm-plex-mono` (aprovados) e importar os pesos da seção 5.3.
- [x] Ícones: instalar `@heroicons/react` (aprovado) e criar `components/icons.tsx` com os três ícones próprios (seção 07).
- [ ] Favicon a partir de `brand/logo/vagafit-favicon.svg`; social preview a partir do lockup light (com o texto em curvas). Favicon feito em 2026-11-01; social preview pendente.
- [x] Rodar `python lint.py` e o build antes de concluir.

Veja também: 08, 12, 14.

## 14. Governança da marca

### 14.1 Quem é dono de quê

| Área | Dono | Pode mudar sozinho `(i)` | Exige Pedro Pompeu `(d)` |
|---|---|---|---|
| Conceito, posicionamento, símbolo, paleta, regras de uso (01, 02, 03, 07, 11) | ARIA | Ajuste de tom derivado, desde que mantenha os papéis de cor | Novo conceito, novo símbolo, mudança de papel de cor, uso do âmbar |
| Tokens, specs de componente, motion, data viz (03 a 10) | MAXWELL | Valor de token que preserve contraste AA, novo estado de componente | Nova dependência, mudança de arquitetura de tokens |
| Voz, glossário, microcopy, restrições (12) | ECHO | Reescrita de string dentro das regras | Regra de negócio na copy, claims de privacidade, tagline, palavras banidas |
| Estrutura do documento, QA, versão, changelog (00, 13, 14, 15) | NOVA | Correção, exemplos, reorganização | — |
| Decisão final e dependências | Pedro Pompeu | — | Tudo que for `(d)` |

### 14.2 Como atualizar

1. Abra a mudança descrevendo seção, motivo e impacto (qual token, componente ou string muda).
2. O dono da área propõe; a NOVA roda o checklist de qualidade (contraste, 8 estados, exemplos, Do/Don't).
3. Mudança de arquitetura, nova dependência ou regra de negócio: validação prévia de Pedro, registrada como `(d)`.
4. Atualize `brand/design-tokens.css` e `brand/tailwind.config.ts` **juntos** (os blocos escuros do CSS são idênticos entre si: `[data-theme="dark"]` e `prefers-color-scheme`).
5. Registre no changelog (seção 15) e incremente a versão.
6. Antes de concluir: validação mecânica do projeto (`python lint.py`, se existir) e build do front.

**Conteúdo permitido neste repositório:** nada sensível. Sem e-mail, sem chave, sem dado real de currículo. Exemplos só com **Ana Exemplo**.

### 14.3 Versionamento

- **MAJOR (X.0):** muda o conceito, o símbolo ou os papéis de cor.
- **MINOR (1.X):** novo componente, novo token, nova regra, nova seção de conteúdo.
- **PATCH (1.0.X):** correção de texto, exemplo ou valor sem mudar regra.
- Fato nunca se apaga: o que for substituído é marcado `~superseded AAAA-MM-DD` apontando para o fato novo.
- Status: Draft, Review, Stable. Passa a Stable quando os itens de 14.4 estiverem resolvidos.

### 14.4 Decisões, pendências e sugestões

**Decisões registradas**

| Data | Prov. | Decisão |
|---|---|---|
| 2026-11-01 | (d) | Fontes IBM Plex Sans + IBM Plex Mono, self-hosted via `@fontsource` (aprovado; instalação depois) |
| 2026-11-01 | (d) | Tagline principal "Cada ponto, com prova."; linha de apoio "Sem prova, é lacuna." |
| 2026-11-01 | (d) | Score em badge neutro de petróleo, `72/100` em mono, sem semáforo |
| 2026-11-01 | (d) | `BRAND.md` e `brand/` são versionados no repositório público; nada sensível; persona "Ana Exemplo" |
| 2026-11-01 | (d) | Modo claro é o padrão (brief); escuro derivado |
| 2026-11-01 | (i) | "Sem evidência" = `met` sem citação; `not_met` = lacuna, "Não atende" (resolve a ambiguidade 1 da ECHO) |
| 2026-11-01 | (i) | Terracota compartilhado entre aviso e "Atende em parte" aceito (sempre ícone e texto) |
| 2026-11-01 | (i) | Faixa lateral âmbar da evidência e borda tracejada de "Sem evidência" são decorativas |
| 2026-11-01 | (d) | Fundo branco vetado; modo claro em Sálvia (canvas `#DAE4DC`, surface `#EDF2EE`) |
| 2026-11-01 | (d) | Ícones: Heroicons (`@heroicons/react`, 24/outline); `lucide-react` descartado |
| 2026-11-01 | (d) | Símbolo "Infinito com duas pessoas" (1a); "Visto sublinhado" `~superseded 2026-11-01` |
| 2026-11-01 | (d) | Desenho do 1a refeito pela rodada 3 da prancha: fita em duas cores (você neutro, a vaga petróleo), cruzamento por cima, arco aberto. O traço fino de cor única da rodada 2 fica `~superseded 2026-11-01` |
| 2026-11-01 | (d) | Wordmark "vagafit" em Plex Mono 500 minúsculo com "fit" grifado (híbrido e) |
| 2026-11-01 | (d) | Verbo de remoção "Apagar"; botão "Analisar vaga" (resolve as ambiguidades 3 e 4 da ECHO) |
| 2026-11-01 | (i) | Versão reduzida do símbolo (sem arcos) para favicon e ícone de app, abaixo de 32 px `~superseded 2026-11-01`: o favicon passa a ser o próprio 1a no quadrado petróleo, como na rodada 3 |
| 2026-11-01 | (i) | Três ícones próprios no estilo Heroicons: sem evidência, citação, grifo |
| 2026-11-01 | (i) | `--color-brand` = petróleo-600; tons derivados do escuro aceitos; ID do trecho = "Currículo · trecho N" |
| 2026-11-01 | (d) | Tema claro é o oficial: `data-theme="light"` fixo; escuro só por escolha explícita futura |
| 2026-11-02 | (d) | Frase de apoio do score explicita o peso dos obrigatórios (resolve a ambiguidade 2 da ECHO) |
| 2026-11-02 | (e) | PDF sem texto selecionável é recusado com mensagem própria (resolve a ambiguidade 5) |
| 2026-11-02 | (d) | Aviso "Sua sessão expirou" na tela de login quando o refresh falha (resolve a ambiguidade 6) |
| 2026-11-02 | (e) | A mensagem do backend (`error.message`) tem prioridade sobre a do front; a copy do backend segue esta seção (resolve a ambiguidade 7) |
| 2026-11-02 | (d) | Aviso de LGPD e de provedor de IA externo na tela de novo currículo; nenhum outro claim de privacidade (resolve as ambiguidades 8 e 9) |
| 2026-11-02 | (d) | Seção 12.9 aprovada inteira |
| 2026-11-02 | (d) | Barras do breakdown mostram "N de M com evidência" no lugar do percentual |

**Pendente de aprovação de Pedro Pompeu `(d)`**

| Item | Estado |
|---|---|
| `lucide-react` como dependência | `~superseded 2026-11-01`: resolvido, Heroicons `(d)` |
| Busca de anterioridade da marca no INPI (símbolo e nome) | Aberto; antes de registro ou uso comercial |
| ECHO, ambiguidade 2: fórmula do score (a frase de apoio assume que o score resume requisitos com evidência) | `~superseded 2026-11-02`: resolvido, frase nova `(d)` |
| ECHO, ambiguidade 3: "Apagar" × "Excluir" (recomendação: manter **Apagar**) | `~superseded 2026-11-01`: resolvido, **Apagar** `(d)` |
| ECHO, ambiguidade 4: "Analisar vaga" × "Criar análise" no botão | `~superseded 2026-11-01`: resolvido, **Analisar vaga** `(d)` |
| ECHO, ambiguidade 5: PDF só-imagem de fato falha? (a causa foi retirada do texto da seção 12.7 até confirmar) | `~superseded 2026-11-02`: confirmado `(e)`, falha; linha própria na 12.7 |
| ECHO, ambiguidade 6: aviso de sessão expirada na tela de login | `~superseded 2026-11-02`: resolvido, aviso `(d)` |
| ECHO, ambiguidades 7 a 9: mensagem do backend sobrescreve a do front; claims de privacidade; provedor de IA | `~superseded 2026-11-02`: 7 confirmada `(e)`; 8 e 9 resolvidas com o aviso de LGPD `(d)` |
| Seção 12.9 inteira (restrições propostas pela ECHO) | `~superseded 2026-11-02`: aprovada `(d)` |
| Valor "4 de 6 com evidência" derivado de `requirements[]` no front (MAXWELL) | `~superseded 2026-11-02`: aprovado `(d)`; conta requisitos do grupo com citação, e o percentual ponderado só define o comprimento |

**Sugestões da NOVA (não são decisões)**
- Tokenizar `8rem` e o ponto de quebra `40rem` do exemplo de barras (`--size-bar-label`, `--bp-sm`) — MAXWELL.
- Confirmar área de respeito (`x` = 1/4 do símbolo) e tamanhos mínimos (seção 2.5) — ARIA. Revisto para o símbolo novo na 1.1 e de novo na 1.2.
- Direção de imagem (seção 11) deriva só das proibições; confirmar ou ampliar — ARIA.
- Converter o wordmark em curvas para os ativos estáticos depois de instalar a fonte.
- Confirmar o desenho final do `circle-dashed` ao adotar Lucide. `~superseded 2026-11-01`: Lucide descartado; o tracejado agora é o `NoEvidenceIcon` próprio (seção 07).

**Achados para registrar em `context/achados.md` (fora do escopo desta entrega, que não edita `context/`):** borda de controle com 1,44:1 (corrigida por `--color-line-strong`); diálogo sem elevação com o novo `--shadow-card`; `::backdrop` e herança de variáveis em navegadores antigos; `color-scheme: light` fixo no `index.css`.

## 15. Changelog

| Versão | Data | Mudança |
|---|---|---|
| 1.0 | 2026-11-01 | Primeira versão. Conceito Laudo (ARIA); 375 tokens em 3 camadas, Tailwind 3.4, specs de 10 componentes e 3 novos (VerdictBadge, ScoreBadge, EvidenceQuote) (MAXWELL); voz, microcopy, glossário e restrições (ECHO); logo em 4 variantes com SVG e usos proibidos; governança. Status: Review. |
| 1.1 | 2026-11-01 | Escolhas de Pedro na prancha visual: fundo Sálvia (7 primitivos novos; canvas, surface, sunken, tinta, linhas); símbolo "Infinito com duas pessoas" com versão reduzida; wordmark "vagafit" em Plex Mono com grifo; Heroicons e três ícones próprios; "Apagar" e "Analisar vaga". Contrastes do claro refeitos. |
| 1.2 | 2026-11-01 | Símbolo 1a com o desenho da rodada 3 da prancha (fita em duas cores com degradê no cruzamento, vão por máscara, arco aberto preenchido); favicon = símbolo no quadrado petróleo; tokens `--color-logo-you` e `--color-logo-job` (385 variáveis); usos proibidos e contrastes refeitos. Mesma escolha de Pedro (1a + e): a versão sobe para 1.2, e não para MAJOR, porque o símbolo escolhido não mudou, só o desenho. |
| 1.3 | 2026-11-02 | Ambiguidades 2, 5, 6, 7, 8 e 9 da ECHO resolvidas: nova frase de apoio do score, mensagens de PDF escaneado, sessão expirada e aviso de LGPD na 12.7; seção 12.9 aprovada `(d)`. Continuam abertos: busca no INPI e o "4 de 6 com evidência" (o front mostra percentual). |
| 1.3.1 | 2026-11-02 | "4 de 6 com evidência" aprovado e aplicado no front (o percentual sai do texto). Resta só a busca no INPI. |
