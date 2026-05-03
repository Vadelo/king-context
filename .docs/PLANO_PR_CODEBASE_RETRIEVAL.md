# Plano de PR: Codebase Retrieval no King Context

## Objetivo

Adicionar suporte para indexar e consultar codebases locais como um novo corpus
oficial do King Context, mantendo a filosofia atual do projeto:

- local-first;
- progressive disclosure;
- busca por metadados antes de leitura completa;
- foco em agentes e contexto eficiente.

---

## Tese da PR

O King Context nao deve tratar codebase como texto bruto. O valor real desta
PR e transformar codigo em unidades estruturadas e consultaveis.

Em vez de apenas indexar arquivos, a feature deve ajudar a responder perguntas
como:

- onde essa feature comeca;
- quais modulos esse fluxo afeta;
- que testes cobrem esse comportamento;
- qual ADR explica essa implementacao;
- que partes do sistema se relacionam com uma decisao arquitetural.

---

## Escopo da primeira PR

### Entregas

- novo store `code`;
- pipeline de ingestao de codebase local;
- suporte de consulta via `kctx`;
- schema de corpus de codigo;
- links basicos entre codigo, testes e ADRs;
- documentacao de uso;
- suite de testes robusta.

### Fora de escopo

- embeddings;
- call graph completo;
- compreensao profunda de muitas linguagens;
- execucao de codigo;
- refatoracao automatica;
- analise semantica pesada.

---

## Proposta de UX

### Novo comando de ingestao

Sugestao principal:

- `king-codebase . --name my-project --yes`

Alternativa:

- `kctx code index .`

Recomendacao: usar `king-codebase` para ficar coerente com `king-scrape` e
`king-research`.

### Comandos de consulta

- `kctx list code`
- `kctx search "job coordination" --source code`
- `kctx read my-project workers/lock-manager --source code --preview`
- `kctx topics my-project --source code`

---

## Modelo de dados

### Store final

- `.king-context/code/<slug>/`

### Dados exportados

- `.king-context/data/code/<slug>.json`

### Unidade indexada

Cada secao do corpus de codigo deve representar uma unidade util de leitura,
como:

- arquivo;
- funcao;
- classe;
- metodo;
- rota;
- job;
- config;
- teste;
- entrypoint.

### Campos sugeridos por secao

- `title`
- `path`
- `kind`
- `language`
- `module`
- `symbols`
- `keywords`
- `use_cases`
- `tags`
- `priority`
- `related_files`
- `related_tests`
- `related_adrs`
- `content`
- `start_line`
- `end_line`

---

## Estrategia de implementacao

### Fase 1: file-level

Indexar arquivos relevantes com metadados estruturais:

- caminho;
- linguagem;
- papel do arquivo;
- imports principais;
- tags;
- resumo curto;
- trecho de conteudo controlado.

### Fase 2: symbol-level

Extrair simbolos relevantes de linguagens prioritarias.

Primeira recomendacao:

- Python com `ast`;
- JavaScript/TypeScript com extracao leve e segura;
- JSON/YAML para configuracoes.

### Fase 3: relacoes

Adicionar ligacoes simples:

- arquivo para teste relacionado;
- modulo para ADR relacionada;
- simbolo para arquivo pai;
- entrypoint para arquivos referenciados.

---

## Seguranca

Esta PR precisa ser especialmente cuidadosa.

### Regras obrigatorias

- nunca indexar `.env`, segredos, certificados ou chaves;
- ignorar `.git/`, `node_modules/`, `.venv/`, `dist/`, `build/`, `coverage/`,
  caches e saidas geradas;
- ignorar binarios;
- limitar tamanho por arquivo;
- limitar tamanho por secao;
- nao seguir symlinks para fora do repositorio;
- operar em modo somente leitura;
- nunca executar codigo do projeto indexado;
- permitir listas de inclusao e exclusao configuraveis.

### Validacoes minimas

- bloquear arquivos acima de um tamanho definido;
- normalizar paths antes de indexar;
- registrar arquivos ignorados por motivo;
- deixar claro no output quando algo foi excluido por seguranca.

---

## Relacao com ADR

Esta feature deve conversar diretamente com a memoria de decisoes.

### Objetivo

Permitir perguntas como:

- qual ADR explica este modulo;
- que codigo foi impactado por esta decisao;
- a implementacao atual ainda bate com a ADR.

### MVP de ligacao

- associacao por metadados;
- associacao por keywords e areas da ADR;
- opcionalmente por comentario, docstring ou anotacao manual.

---

## Mudancas tecnicas provaveis

### CLI

Arquivos principais:

- `src/context_cli/cli.py`
- `src/context_cli/store.py`
- `src/context_cli/searcher.py`
- `src/context_cli/indexer.py`

### Novo modulo

Sugestao:

- `src/king_context/codebase/cli.py`
- `src/king_context/codebase/discover.py`
- `src/king_context/codebase/extract.py`
- `src/king_context/codebase/export.py`
- `src/king_context/codebase/config.py`

### Instalacao e docs

- atualizar wrappers se necessario;
- atualizar `docs/CLI_GUIDE.md`;
- atualizar `README.md` e `README-pt-br.md`;
- adicionar exemplo em `validation/examples/`.

---

## Ordem de execucao recomendada

1. Criar uma ADR para a feature.
2. Definir schema do corpus de codebase.
3. Criar fixture de repositorio pequeno para testes.
4. Implementar descoberta de arquivos com filtros de seguranca.
5. Implementar extracao file-level.
6. Implementar extracao symbol-level para Python.
7. Adicionar `code` como novo source no `kctx`.
8. Adicionar links basicos com testes e ADRs.
9. Documentar o fluxo.
10. Rodar testes completos e revisar regressao.

---

## Criterios de aceite

A PR so deve ser considerada pronta se:

- indexar um repositorio pequeno sem vazar arquivos sensiveis;
- `kctx search` encontrar arquivos e simbolos relevantes no store `code`;
- `kctx read --preview` funcionar no novo store;
- os fluxos atuais de `docs`, `research` e `adr` continuarem funcionando;
- houver cobertura de testes para seguranca, parser e integracao;
- a documentacao deixar limites e comportamento bem claros.

---

## Plano de testes

## 1. Testes unitarios

Cobrir:

- regras de ignore;
- exclusao de `.env` e segredos;
- deteccao de linguagem;
- parser Python com `ast`;
- extracao de simbolos;
- normalizacao de paths;
- limite de tamanho;
- bloqueio de symlink externo;
- schema do JSON exportado.

## 2. Testes de integracao

Criar fixture com:

- `src/`
- `tests/`
- `config/`
- uma ADR
- um `.env` fake que deve ser ignorado

Validar:

- indexacao completa;
- busca por arquivo;
- busca por funcao;
- leitura preview;
- leitura full;
- `--source code`;
- ligacao entre modulo e ADR;
- ligacao entre modulo e teste.

## 3. Testes de regressao

Rodar toda a suite existente:

- `tests/test_context_cli/*`
- `tests/test_research/*`
- `tests/test_scraper/*`
- `tests/test_installer_*`
- `tests/test_server.py`

Objetivo:

- provar que a nova feature nao quebra `docs`, `research` ou `adr`.

## 4. Testes de seguranca

Casos obrigatorios:

- `.env` presente e nao indexado;
- binario grande ignorado;
- `node_modules` ignorado;
- symlink para fora do repo ignorado;
- arquivo gigante truncado ou excluido;
- path traversal rejeitado.

## 5. Testes de qualidade de retrieval

Criar queries reais e validar top-1 ou top-3:

- "where does job ownership start"
- "how are retries configured"
- "which test covers lock manager"
- "which decision explains cli-first retrieval"

---

## Estrategia para a PR ficar redonda

### 1. Abrir com ADR

Antes da implementacao, registrar a direcao da feature.

Titulo sugerido:

- `Introduce codebase retrieval as a first-class King Context store`

### 2. Fazer um MVP pequeno e forte

Melhor:

- Python muito bem suportado

do que:

- varias linguagens com suporte superficial.

### 3. Caprichar em fixtures e exemplos

Itens que aumentam muito a qualidade percebida:

- caso de validacao em `validation/examples/`;
- walkthrough na `docs/CLI_GUIDE.md`;
- exemplo no README.

### 4. Separar bem os commits

Sugestao:

1. `adr: record codebase retrieval direction`
2. `feat(codebase): add secure local codebase exporter`
3. `feat(cli): add code store retrieval support`
4. `test(codebase): add fixtures and regression coverage`
5. `docs: document codebase retrieval workflow`

### 5. Posicionamento da PR

Descrever a entrega como:

- first-class codebase retrieval MVP;
- metadata-first;
- local-first;
- safe by default;
- base para evolucoes futuras.
