# King Context para Leigos

## Resumo rapido

O **King Context** e uma ferramenta que ajuda agentes de IA e pessoas a
encontrarem a informacao certa sem precisar abrir um monte de arquivos,
documentacao enorme ou dezenas de links.

Em vez de jogar tudo de uma vez para a IA, ele faz algo mais inteligente:

1. guarda o conhecimento localmente;
2. organiza esse conhecimento em partes menores;
3. deixa voce buscar so o pedaco que importa;
4. entrega primeiro um resumo pequeno;
5. so mostra o conteudo completo quando for realmente necessario.

Na pratica, ele funciona como uma mistura de:

- buscador local de documentacao;
- memoria organizada para agentes;
- ferramenta de pesquisa na web;
- arquivo de decisoes do projeto;
- ponte entre conhecimento bruto e uso real no dia a dia.

---

## O problema que ele resolve

Hoje, quando voce quer usar IA para programar, pesquisar ou analisar algo,
normalmente acontece uma destas situacoes:

- a documentacao e grande demais;
- a IA recebe contexto demais e se perde;
- a IA inventa resposta porque nao encontrou o trecho certo;
- voce precisa abrir varios arquivos para descobrir uma informacao simples;
- o projeto toma decisoes tecnicas e ninguem lembra depois o motivo.

O King Context existe para evitar isso.

Ele reduz o excesso de informacao e transforma conhecimento espalhado em algo
facil de consultar.

---

## Em linguagem bem simples: o que esse projeto faz?

Pense assim:

- a documentacao de uma API vira uma biblioteca organizada;
- uma pesquisa na internet vira um acervo pesquisavel;
- as decisoes do time viram uma memoria oficial do projeto;
- a IA consulta so o que precisa, em vez de ler tudo no bruto.

Entao, em vez de perguntar para a IA com base no vazio, voce da a ela um
"armario de conhecimento" arrumado.

---

## O que ele pode guardar

O projeto trabalha hoje com quatro tipos principais de conhecimento:

### 1. Documentacao de produtos e APIs

Exemplos:

- docs do Stripe;
- docs do Exa;
- docs de uma SDK;
- docs internas de uma ferramenta.

O projeto consegue baixar esse material, separar em secoes e indexar para
busca.

### 2. Pesquisa da web aberta

Voce informa um tema, como:

- "prompt engineering";
- "agent memory systems";
- "retry backoff";
- "webhook security".

O projeto pesquisa fontes na web, coleta os materiais, organiza tudo e cria um
corpus local para consulta posterior.

### 3. Decisoes de arquitetura

O projeto tambem consegue guardar ADRs, que sao registros de decisoes
arquiteturais.

Exemplo:

- por que o projeto escolheu CLI em vez de MCP como caminho principal;
- por que uma estrategia antiga foi abandonada;
- qual decisao substituiu outra.

Isso evita o famoso "alguem decidiu isso meses atras, mas ninguem lembra por
que".

### 4. Aprendizados acumulados

Existe uma area chamada `.king-context/_learned/` onde o proprio agente pode
salvar atalhos e descobertas uteis feitas durante o uso.

Isso significa que, com o tempo, o sistema pode ficar mais rapido e mais
esperto para aquele corpus especifico.

---

## O que ele pode fazer no dia a dia

Aqui estao as possibilidades reais do projeto hoje.

### Buscar documentacao indexada

Voce pode procurar assuntos como:

- autenticacao;
- rate limit;
- streaming;
- configuracao;
- parametros de uma API.

O sistema busca pelos metadados e mostra os trechos mais promissores.

### Ler so um preview antes de abrir tudo

Antes de consumir o conteudo inteiro, voce pode pedir apenas uma previa.

Isso e importante porque:

- economiza contexto;
- economiza tokens;
- evita leitura desnecessaria;
- ajuda a confirmar se aquele trecho e mesmo o que voce precisa.

### Ler a secao completa

Se a previa estiver certa, entao voce abre a secao completa.

### Navegar por topicos e tags

Se voce ainda nao sabe exatamente o que procurar, pode explorar os topicos
associados a um corpus e descobrir as secoes relacionadas.

### Fazer busca exata por texto

Se voce souber a palavra exata, nome de classe, metodo, parametro ou erro,
pode usar busca de texto direto, como um "grep".

Isso e muito util para achar:

- nomes de cabecalhos;
- mensagens de erro;
- codigos;
- classes;
- funcoes;
- termos especificos.

### Indexar JSONs exportados

Se o projeto ja produziu um arquivo JSON com o material processado, voce pode
mandar indexar esse arquivo para transforma-lo em um acervo pesquisavel.

### Pesquisar a web por tema

Com `king-research`, o sistema monta um corpus inteiro sobre um assunto a partir
da web aberta.

Isso serve para:

- estudar um tema antes de implementar;
- comparar abordagens;
- levantar estado da arte;
- reunir referencias em um so lugar;
- dar base para uma IA pensar melhor sobre um assunto.

### Fazer scraping de sites de documentacao

Com `king-scrape`, o projeto consegue:

- descobrir paginas de um site de docs;
- filtrar o que parece relevante;
- baixar o conteudo;
- quebrar em partes;
- enriquecer com metadados;
- exportar para uso posterior.

### Registrar decisoes importantes do projeto

Com `kctx adr`, da para:

- listar decisoes existentes;
- buscar decisoes por tema;
- ler uma decisao;
- criar uma nova ADR;
- marcar que uma decisao substituiu outra;
- ligar decisoes relacionadas;
- validar se os registros estao consistentes.

### Servir como base para agentes de IA

Esse e um dos pontos centrais do projeto.

Em vez de um agente:

- abrir documentos gigantes;
- depender de busca remota opaca;
- receber contexto demais;
- alucinar por falta de precisao;

ele pode consultar uma base local organizada e trabalhar com muito mais foco.

### Funcionar como CLI

O projeto foi desenhado com foco forte em linha de comando.

Isso ajuda porque:

- e mais previsivel;
- funciona bem com agentes de codigo;
- facilita automacao;
- pode ser usado em scripts e pipelines.

### Funcionar tambem como MCP

O projeto tambem oferece suporte a MCP server.

Em termos simples: ele tambem pode conversar com ferramentas que esperam esse
tipo de integracao.

### Devolver saida em JSON

Muitos comandos aceitam `--json`, o que permite:

- integrar com scripts;
- automatizar fluxos;
- alimentar outras ferramentas;
- permitir leitura estruturada por agentes.

---

## Principais comandos e o que cada um faz

### `kctx`

E a ferramenta principal para consultar o conhecimento ja indexado.

Com ela voce pode:

- listar bases salvas;
- buscar por assunto;
- ler um trecho;
- navegar por tags;
- fazer busca exata por texto;
- indexar novos arquivos JSON;
- trabalhar com ADRs.

### `king-scrape`

Serve para transformar um site de documentacao em um corpus local pesquisavel.

Uso ideal:

- quando voce quer "baixar e organizar" a documentacao de uma ferramenta.

### `king-research`

Serve para montar um corpus de pesquisa a partir de um tema.

Uso ideal:

- quando voce nao tem uma documentacao unica;
- quando precisa juntar varias fontes sobre um assunto;
- quando quer basear uma analise em varias referencias.

### `king-context-server`

E a interface MCP do projeto.

Uso ideal:

- quando a integracao precisa acontecer por MCP em vez de CLI.

---

## Como imaginar o fluxo completo

Um uso comum pode ser assim:

1. voce escolhe uma documentacao ou um tema;
2. o projeto coleta esse conhecimento;
3. ele organiza esse material em secoes menores;
4. ele marca cada secao com palavras-chave e contexto;
5. depois voce ou a IA fazem buscas pequenas e precisas;
6. leem uma previa;
7. abrem a secao inteira so quando fizer sentido.

Esse jeito de trabalhar e o coracao do projeto.

---

## Diferenca entre os tipos de busca

### Busca por documentacao

Use quando voce quer descobrir:

- como uma API funciona;
- quais parametros existem;
- como autenticar;
- como configurar uma biblioteca;
- como um recurso oficial foi documentado.

### Busca por pesquisa

Use quando voce quer descobrir:

- o que varias fontes dizem sobre um tema;
- melhores praticas;
- comparacoes;
- tendencias;
- opinioes tecnicas consolidadas.

### Busca por decisao do projeto

Use quando voce quer descobrir:

- por que o time escolheu um caminho;
- qual decisao ainda vale;
- o que foi substituido;
- como uma mudanca se conecta com decisoes passadas.

---

## Niveis de esforco da pesquisa

O `king-research` permite variar a profundidade da pesquisa.

### `--basic`

Busca menor e mais rapida.

Bom para:

- exploracao inicial;
- perguntas simples;
- levantar um panorama rapido.

### `--medium`

Meio-termo entre velocidade e profundidade.

Bom para:

- estudos normais;
- comparacoes moderadas;
- temas com alguma complexidade.

### `--high`

Mais abrangente e mais demorado.

Bom para:

- pesquisas serias;
- temas amplos;
- coleta grande de fontes.

### `--extrahigh`

Varredura maxima dentro da proposta atual do projeto.

Bom para:

- levantamento bem profundo;
- mapeamento mais completo de um assunto;
- criacao de corpus grande.

---

## O que existe dentro da pasta `.king-context`

Essa pasta e o "cerebro local" do projeto.

Ela costuma guardar coisas como:

- `docs/`: documentacoes indexadas;
- `research/`: pesquisas indexadas;
- `data/`: arquivos brutos/exportados antes ou durante indexacao;
- `adr/`: arquivos Markdown das decisoes arquiteturais;
- `decisions/project/`: indice derivado das decisoes;
- `_learned/`: atalhos e aprendizados acumulados.

---

## O que significa "local-first"

Quer dizer que o conhecimento organizado fica na sua maquina, dentro do
projeto, em vez de depender o tempo todo de um servico remoto para cada busca.

Isso traz vantagens como:

- mais controle;
- mais transparencia;
- mais previsibilidade;
- menor dependencia de terceiros;
- chance de trabalhar com menos custo de contexto.

---

## Por que isso ajuda uma IA

IA costuma errar por alguns motivos bem comuns:

- contexto demais;
- contexto ruim;
- contexto irrelevante;
- falta do trecho exato;
- ambiguidade mal resolvida.

O King Context tenta atacar exatamente isso.

Ele nao promete "magica". O que ele faz e melhorar a qualidade do material que
chega ate a IA.

E quando a entrada melhora, a resposta tende a melhorar tambem.

---

## Quem pode usar esse projeto

Ele e especialmente util para:

- desenvolvedores;
- equipes que usam agentes de codigo;
- pessoas que pesquisam temas tecnicos;
- times que querem registrar decisoes de arquitetura;
- projetos que lidam com muita documentacao.

Mesmo assim, a ideia geral e simples o bastante para qualquer pessoa entender:
organizar conhecimento grande em partes menores e consultaveis.

---

## O que precisa para funcionar

Dependendo do uso, o projeto pode precisar de algumas chaves de API.

As principais mencionadas no proprio repositorio sao:

- `FIRECRAWL_API_KEY`: para scraping de documentacao;
- `EXA_API_KEY`: para pesquisas na web com `king-research`;
- `OPENROUTER_API_KEY`: opcional em alguns fluxos de enriquecimento;
- `JINA_API_KEY`: opcional para alguns recursos de pesquisa.

Nem toda funcionalidade precisa de todas as chaves.

---

## O que esse projeto nao e

Para evitar expectativa errada, vale dizer tambem o que ele nao e.

- Nao e uma IA por si so.
- Nao e um chatbot pronto para usuario final.
- Nao e um substituto de leitura critica.
- Nao e um banco magico que entende qualquer coisa perfeitamente sem preparo.

Ele e uma **camada de organizacao e retrieval** para melhorar como conhecimento
e encontrado e entregue.

---

## Exemplo de uso em linguagem simples

Imagine que voce quer usar uma API nova.

Sem King Context:

- voce abre um monte de paginas;
- copia e cola trechos;
- a IA le blocos enormes;
- parte do contexto e desperdicada;
- respostas podem vir incompletas ou confusas.

Com King Context:

1. voce coleta a documentacao;
2. indexa o material;
3. busca por "authentication";
4. le primeiro a previa;
5. abre o trecho certo;
6. usa isso para implementar com mais seguranca.

Agora imagine o mesmo raciocinio para um tema de pesquisa, como
"prompt engineering".

Em vez de depender de memoria solta ou de links dispersos, voce monta um corpus
local e vai consultando as partes relevantes.

---

## Estado atual do projeto

Pelo proprio repositorio, o projeto esta em desenvolvimento ativo e a licenca e
MIT.

Tambem vale notar que ele esta evoluindo em torno de:

- CLI como interface principal;
- suporte a agentes;
- documentacao e pesquisa no mesmo ecossistema;
- memoria de decisoes arquiteturais;
- uso local e eficiente de contexto.

---

## Em uma frase

Se eu tivesse que explicar o King Context de forma bem direta:

> Ele transforma documentacao, pesquisa e decisoes do projeto em uma base local
> organizada para que pessoas e agentes encontrem so o trecho certo, na hora
> certa.

---

## Sugestao de leitura depois deste guia

Se quiser se aprofundar no repositorio, os melhores proximos arquivos sao:

- `README-pt-br.md`
- `docs/CLI_GUIDE.md`
- `validation/examples/`
- `validation/minimax-tts-first-shot/`

Esses arquivos mostram a visao do projeto, os comandos e exemplos reais de uso.
