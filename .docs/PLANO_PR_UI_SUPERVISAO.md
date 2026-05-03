# Plano de PR: UI de Supervisao do Contexto

## Objetivo

Criar uma UI de supervisao para o King Context que permita inspecionar,
navegar e entender o conhecimento indexado sem substituir a CLI.

Essa UI deve ajudar a responder:

- o que existe no projeto;
- como a arquitetura esta organizada;
- quais corpus foram indexados;
- que decisoes explicam cada area;
- por que certos resultados aparecem nas buscas;
- por onde um usuario novo deve comecar.

---

## Tese da feature

A UI nao deve ser um "chat bonito". Ela deve ser uma camada visual de
supervisao do contexto.

O diferencial e mostrar a forma do conhecimento:

- corpus;
- topicos;
- secoes importantes;
- relacoes;
- decisoes;
- mudancas futuras.

---

## Proposta de valor

### Para onboarding

- entender rapidamente o projeto;
- descobrir corpus disponiveis;
- navegar por areas, tags e secoes.

### Para arquitetura

- ver dominios e relacoes do sistema;
- conectar implementacao e ADR;
- enxergar lacunas de documentacao ou decisao.

### Para retrieval

- aumentar confianca no que foi indexado;
- explicar de onde o contexto veio;
- permitir inspecao antes do uso por agentes.

---

## Escopo do MVP

### Entregas

- `Corpus Explorer`
- `Overview` com contagens e estado dos stores
- `Decision View`
- `Search Inspector`
- `Architecture Map` inicial baseado em relacoes leves
- geracao read-only por meio da CLI

### Fora de escopo

- edicao de codigo;
- refatoracao automatica;
- tempo real;
- grafo profundo de dependencias;
- visualizacao perfeita de mudancas por Git.

---

## Fontes de dados

- `.king-context/docs/`
- `.king-context/research/`
- `.king-context/decisions/project/`
- `.king-context/adr/`
- futuramente `.king-context/code/`

---

## Estrategia tecnica

### Abordagem inicial

Comecar com dashboard estatico gerado localmente pelo `kctx`.

Vantagens:

- sem dependencias web pesadas;
- sem servidor adicional;
- seguro por padrao;
- facil de testar;
- preserva a filosofia local-first.

### Modelo

1. Ler os stores ja indexados.
2. Gerar um snapshot JSON consolidado.
3. Embutir esse snapshot em um HTML estatico.
4. Permitir busca, navegacao e inspecao no navegador.

---

## Telas e blocos do MVP

### 1. Overview

- total de corpus;
- total de secoes;
- total de ADRs;
- data de geracao;
- resumo por store.

### 2. Corpus Explorer

- lista de `docs`, `research` e `decisions`;
- tags principais;
- secoes prioritarias;
- preview ao clicar.

### 3. Architecture Map

- grafo simples de corpus, tags e decisoes;
- relacoes iniciais por keywords, tags e areas;
- foco em entendimento macro, nao em renderizacao perfeita.

### 4. Decision View

- ADRs ativas;
- ADRs historicas;
- timeline resumida;
- relacoes com corpus.

### 5. Search Inspector

- busca local no snapshot;
- resultados agrupados por origem;
- explicacao do que bateu;
- detalhe ao selecionar.

---

## Seguranca

### Regras

- modo somente leitura;
- nunca expor `.env`, segredos ou arquivos ignorados;
- limitar tamanho de previews;
- truncar payloads muito grandes;
- nao executar nada do projeto;
- deixar claro quando o contexto esta incompleto.

### Validacoes

- nenhum dado do dashboard pode vir de arquivos fora dos stores indexados;
- o HTML deve ser gerado apenas com dados normalizados;
- previews devem ser escapados com seguranca.

---

## Implementacao recomendada

1. Criar uma ADR da feature.
2. Criar modulo de snapshot/read-only.
3. Criar comando CLI para `dashboard`.
4. Gerar HTML estatico inicial.
5. Adicionar testes unitarios e de integracao.
6. Documentar fluxo na CLI guide.

---

## Plano de testes

## 1. Testes unitarios

- consolidacao do snapshot;
- contagens por store;
- descoberta de tags;
- heuristica de relacao ADR -> corpus;
- renderizacao segura do HTML;
- truncamento de previews.

## 2. Testes de integracao

- `kctx dashboard --json`
- `kctx dashboard --output <arquivo>`
- fixture com docs, research e ADR
- validacao do HTML gerado
- validacao da navegacao por dados embutidos

## 3. Testes de regressao

- suite existente de `context_cli`
- garantir que a nova feature nao muda stores atuais

## 4. Testes de seguranca

- nenhuma referencia a `.env`
- nenhum dado fora dos stores
- conteudo escapado corretamente

---

## Criterios de aceite

- a UI mostra corpus reais;
- a UI mostra secoes e tags relevantes;
- a UI mostra ADRs e relacoes basicas;
- a busca local encontra itens importantes;
- nada sensivel e exposto;
- o fluxo continua coerente com local-first e CLI-first.

---

## Estrategia de PR

### Commit sugeridos

1. `adr: record supervision ui direction`
2. `feat(cli): add context dashboard snapshot generator`
3. `feat(ui): add static supervision dashboard`
4. `test(dashboard): cover snapshot and html generation`
5. `docs: document supervision dashboard workflow`

### Posicionamento

Descrever a entrega como:

- supervision UI;
- read-only;
- local-first;
- explorer for context, architecture and decisions;
- foundation for future codebase and change views.
