---
id: plan
title: Plano Técnico do Projeto Arca
---

# Plano Técnico do Projeto Arca

## 1. Visão Geral

**Objetivo do Arca:** O Arca é um sistema projetado para gerenciar e disponibilizar conteúdo de forma dinâmica a partir de arquivos Markdown e YAML. O objetivo principal é permitir que usuários mantenham suas informações em arquivos legíveis e versionáveis, enquanto o sistema fornece uma interface web interativa para visualizar e interagir com esses dados. Em vez de depender de um banco de dados permanente como fonte de verdade, o Arca trata os arquivos como fonte primária e utiliza um banco de dados **efêmero** apenas para indexação e performance. Isso garante que o conteúdo seja facilmente editável fora do sistema (por exemplo, em editores de texto ou ferramentas de controle de versão) e que quaisquer alterações sejam refletidas quase em tempo real na interface do usuário.

**Princípios Fundamentais do Projeto:** O projeto se baseia em vários princípios-chave:

- _Single Source of Truth:_ Os arquivos Markdown/YAML no sistema de arquivos representam a verdade fundamental do conteúdo. O banco de dados serve apenas como cache/acelerador e pode ser recriado a qualquer momento a partir dos arquivos.
- _Simplicidade e Transparência:_ Tecnologias simples e formatos abertos (texto Markdown, YAML) facilitam a adoção e manutenção. Usuários podem inspecionar e editar diretamente o conteúdo sem ferramentas proprietárias.
- _Atualização em Tempo Real:_ Alterações nos arquivos são detectadas automaticamente (via **watchers** de sistema de arquivos) e propagadas para a interface, garantindo que usuários vejam informações atualizadas sem operações manuais de sincronização.
- _Modularidade:_ A arquitetura é dividida em componentes bem definidos (monitoramento de arquivos, banco de dados, backend, frontend), permitindo fácil manutenção, testes isolados e futuras extensões.
- _Portabilidade e Autonomia:_ O Arca pode rodar localmente sem dependências pesadas (usa um banco SQLite local). O conteúdo pode ser versionado ou sincronizado usando ferramentas externas (como Git ou Dropbox), sem bloqueios do sistema.
- _Consistência e Validação:_ Antes de usar qualquer dado, o sistema valida as estruturas YAML contra esquemas definidos, prevenindo que dados incorretos causem falhas em tempo de execução.

**Tecnologias Utilizadas:** Para alcançar esses objetivos, o Arca aproveita uma stack tecnológica moderna e enxuta:

- **Linguagem:** Python (aproveitando sua vasta biblioteca e simplicidade para prototipação).
- **Armazenamento:** Arquivos **Markdown** (texto formatado) e **YAML** (dados estruturados) como fonte de dados; **SQLite** como banco de dados temporário em runtime.
- **Backend:** Framework **FastHTML** para construir a API RESTful e gerenciar requisições HTTP; integração com **Pydantic** para validação de dados e definição de esquemas.
- **Frontend:** Biblioteca **FastHTML** (acoplada ao FastHTML) para geração de HTML dinâmico via código Python, aliada ao **HTMX** para adicionar interatividade e atualizações assíncronas na interface web _sem necessidade de JavaScript customizado_.
- **Monitoramento de Arquivos:** Biblioteca de "watchers" (por exemplo, **Watchdog** ou similar) para observar mudanças no sistema de arquivos em tempo real e acionar reações.
- **CLI:** Interface de linha de comando (possivelmente usando Click ou Typer em Python) para iniciar o servidor e executar utilidades (como validação manual, importação/exportação).
- Além disso, bibliotecas auxiliares incluem um parser Markdown (para converter conteúdo Markdown em HTML quando necessário) e um parser YAML (para ler e escrever os metadados YAML).

## 2. Arquitetura Geral

### Camadas da Arquitetura

A arquitetura do Arca é organizada em camadas bem definidas, separando as responsabilidades de cada componente:

- **Camada de Conteúdo (Arquivos):** Na base, residem os arquivos Markdown e YAML no sistema de arquivos, que contêm todo o conteúdo e dados estruturados. Esses arquivos são mantidos pelos usuários (manualmente ou via ferramentas externas) e formam a fonte primária de informação da aplicação.

- **Camada de Monitoramento e Ingestão:** Um módulo de watchers observa continuamente a camada de conteúdo. Quando detecta alterações (criação, modificação ou deleção de arquivos), aciona o processo de ingestão: o arquivo afetado é lido, seu conteúdo Markdown e metadados YAML são parseados e validados. Em seguida, as informações são inseridas ou atualizadas no banco de dados efêmero.

- **Camada de Dados (Banco Efêmero):** Os dados extraídos dos arquivos são armazenados em um banco de dados SQLite mantido em runtime. Esse banco de dados atua como um cache indexado, permitindo consultas rápidas e estruturadas pelo backend. Ele reflete exatamente o estado atual dos arquivos monitorados, mas não é considerado a fonte definitiva (pode ser descartado e reconstruído a qualquer momento a partir dos arquivos de conteúdo).

- **Camada de Backend (API/Lógica):** O backend, implementado em FastHTML, serve de intermediário entre a camada de dados e a camada de apresentação. Ele expõe **endpoints** HTTP (rotas) que permitem ao frontend requisitar conteúdo (por exemplo, listar itens, obter detalhes de um item) ou acionar ações (como revalidar dados ou adicionar conteúdo). Nessa camada também reside a lógica de negócio: regras de como os dados são filtrados, relacionados e enviados ao frontend, garantindo que a interface receba informações consistentes e já no formato necessário (por exemplo, HTML pronto ou JSON estruturado).

- **Camada de Frontend (Interface do Usuário):** No topo da arquitetura está a interface web apresentada ao usuário final. Construída com FastHTML e HTMX, ela é essencialmente uma aplicação de página única impulsionada pelo servidor: carrega páginas e componentes dinâmicos sob demanda via requisições ao backend, atualizando a exibição sem recarregar totalmente a página. Essa camada inclui os componentes de UI (listas, formulários, visualizações de conteúdo) e utiliza as rotas do backend para obter ou enviar dados.

Essa separação em camadas garante que cada parte do sistema possa evoluir ou ser substituída independentemente. Por exemplo, poderíamos trocar o mecanismo de armazenamento (usar outro banco de dados) sem refatorar a lógica de apresentação, ou atualizar a interface sem alterar como os dados são armazenados.

### Fluxo Geral de Funcionamento

O funcionamento do Arca envolve a interação coordenada de todas as camadas em um fluxo contínuo. Em linhas gerais, o fluxo segue estes passos:

1. **Inicialização:** Ao iniciar o Arca (por exemplo, via CLI ou ao subir o servidor), o sistema carrega a configuração inicial e ativa os watchers para monitorar o diretório de conteúdo especificado. Em seguida, é realizada uma varredura inicial de todos os arquivos Markdown/YAML presentes. Cada arquivo é lido: se contém metadados YAML (por exemplo, front matter), esses são extraídos e validados; o conteúdo Markdown é parseado quando necessário. As informações resultantes são armazenadas no banco SQLite efêmero, criando um índice inicial de todo o conteúdo disponível.

2. **Execução do Servidor:** Com o conteúdo indexado, o sistema inicia o backend FastAPI, tornando disponíveis os endpoints da API e interface. O servidor fica então em espera para receber requisições HTTP do frontend (ou de clientes API externos). Os watchers de arquivos permanecem ativos em segundo plano, prontos para captar alterações no sistema de arquivos.

3. **Interação do Usuário (Frontend):** O usuário acessa a interface web do Arca através de um navegador. A página inicial (servida pelo backend) apresenta uma visão geral ou lista de conteúdos disponíveis, servindo como ponto de entrada para navegação. Essa página é construída dinamicamente pelo FastHTML, possivelmente listando títulos e descrições obtidos do banco de dados. A interface carrega elementos básicos (como cabeçalho, menu e um contêiner vazio ou resumo de conteúdo) e utiliza HTMX para preencher detalhes conforme a interação do usuário.

4. **Requisições de Dados:** Quando o usuário interage com a interface – por exemplo, clicando em um item da lista para ver detalhes – o frontend utiliza HTMX para fazer uma requisição AJAX ao backend (por exemplo, um GET na rota de detalhes daquele item). O FastAPI recebe essa requisição, consulta o banco efêmero para recuperar os dados solicitados (por exemplo, o conteúdo completo em Markdown e metadados do item), processa a lógica necessária (como transformar Markdown em HTML) e devolve uma resposta. No caso do uso de HTMX, essa resposta muitas vezes já é um fragmento de HTML pronto para ser inserido na página existente.

5. **Atualização da UI:** Ao receber a resposta do backend, o HTMX no frontend insere o fragmento de HTML retornado no lugar apropriado da página (conforme definido pelos atributos `hx-target` e `hx-swap`). Assim, por exemplo, o painel de detalhes na interface é preenchido com o conteúdo completo do item selecionado, **sem recarregar a página inteira**. Toda a navegação e interação do usuário segue esse padrão: ações na UI desencadeiam chamadas à API, que retornam dados ou HTML, e a página é parcialmente atualizada de forma dinâmica.

6. **Detecção de Alterações Externas:** Enquanto o usuário navega, o módulo de watchers está constantemente observando o diretório de conteúdo. Se, por exemplo, o usuário (ou outro colaborador) edita um arquivo Markdown externamente em um editor de texto, salva um novo arquivo ou remove um existente, o watcher detectará essa mudança no sistema de arquivos quase imediatamente.

7. **Atualização Incremental do Conteúdo:** Ao detectar uma mudança, o watcher aciona o processo de atualização incremental: o arquivo modificado é reprocessado – no caso de alteração ou criação, lê o novo conteúdo, extrai/valida o YAML e atualiza (ou insere) a entrada correspondente no SQLite; no caso de deleção, remove a entrada respectiva do banco. Essa operação ocorre em segundo plano, de forma atômica e rápida, usando transações SQLite para garantir consistência. Durante esse breve momento, o backend continua operando normalmente (pode servir outros pedidos); requisições para o item em mudança podem ainda obter dados antigos se a atualização não tiver terminado, mas logo em seguida o banco reflete o novo estado.

8. **Propagação para a Interface:** Uma vez que o banco de dados é atualizado, qualquer nova requisição do frontend trará já o conteúdo atualizado. Por exemplo, se o usuário estava visualizando uma lista de documentos e um novo arquivo Markdown foi adicionado por alguém, o próximo pedido que atualizar essa lista (manual ou automático) já incluirá o novo documento. Opcionalmente, podemos implementar no frontend mecanismos de atualização automática (como um refresh periódico via HTMX ou um aviso visual) para informar o usuário de novas alterações, dado que o sistema em si não "empurra" atualizações para o cliente sem uma requisição (a não ser que seja estendido com WebSockets futuramente).

9. **Encerramento:** Quando o servidor é finalizado, os watchers são desligados e o banco de dados efêmero pode ser descartado. Em caso de reinício do sistema, todo o processo de inicialização ocorre novamente, garantindo que nenhuma mudança nos arquivos seja perdida – afinal, os arquivos são a base persistente.

Esse fluxo geral assegura que o Arca responda dinamicamente a mudanças, oferecendo ao usuário uma experiência fluida onde o conteúdo é sempre atualizado e consistente com os arquivos de origem, sem necessidade de operações manuais de sincronização durante o uso normal.

## 3. Estrutura de Arquivos e Organização

### Armazenamento de Arquivos Markdown e YAML

O projeto Arca adota uma estrutura clara para armazenar os arquivos de conteúdo (Markdown) e seus metadados (YAML). Todos os arquivos relevantes residem em um diretório raiz de conteúdo configurável (por exemplo, uma pasta chamada **`content/`** ou **`dados/`** no projeto). Dentro desse diretório:

- Os arquivos **Markdown (`*.md`)** contêm o conteúdo principal em formato de texto com marcação simples – por exemplo, artigos, notas ou documentação, usando títulos, listas, links, etc., para formatação.

- Os arquivos **YAML (`*.yaml` ou `*.yml`)** carregam dados estruturados, normalmente metadados ou configurações relacionadas ao conteúdo Markdown. Há duas abordagens possíveis para organizar o YAML:
  - _YAML embutido (Front Matter):_ Cada arquivo Markdown pode começar com um bloco YAML (conhecido como _front matter_) na própria primeira parte do arquivo. Esse bloco, delimitado por `---`, inclui chaves e valores de metadados (como título, data, tags, etc.) específicos daquele conteúdo. O Arca, ao ler o arquivo, reconhece e separa esse trecho inicial antes de processar o Markdown.
  - _YAML separado:_ Alternativamente, pode-se manter metadados em arquivos YAML separados. Por exemplo, para um documento `projeto1.md`, pode haver um arquivo `projeto1.yaml` contendo as meta-informações correspondentes (como título, descrição, status). Outra possibilidade é ter arquivos YAML que funcionem como bases de dados de certos tipos de registro independentes do Markdown – por exemplo, um `usuarios.yaml` contendo uma lista estruturada de usuários, complementando perfis escritos em Markdown.

Independentemente da abordagem (front matter vs. arquivos separados), o Arca espera uma correspondência clara entre conteúdo e metadados:

- Se usar front matter, o sistema extrai esse bloco YAML automaticamente de dentro do `.md` durante a leitura, associando-o ao conteúdo do próprio arquivo.
- Se usar arquivos separados, é recomendável que tenham nomes ou caminhos correspondentes aos arquivos Markdown, para que o sistema possa relacioná-los. Uma convenção simples é usar o mesmo nome base: ex. `notas/ideias.md` teria metadados em `notas/ideias.yaml`. Outra estratégia é definir no próprio YAML alguma referência (um ID ou título) que corresponda ao conteúdo do Markdown, mas isso adiciona complexidade – manter nomes iguais é mais direto.

Os usuários podem organizar subdiretórios livremente dentro do diretório de conteúdo para categorizar informações. Por exemplo:

```
content/
├── projetos/
│   ├── projeto1.md
│   ├── projeto1.yaml
│   ├── projeto2.md
│   └── projeto2.yaml
├── notas/
│   ├── ideias.md
│   ├── ideias.yaml
│   └── referencias.md  (este talvez use front matter internamente)
└── config.yaml         (exemplo de arquivo YAML global de configuração)
```

No exemplo acima, há duas pastas ("projetos" e "notas") categorizando diferentes tipos de documentos. Cada Markdown opcionalmente tem seu YAML de mesmo nome ao lado. Um arquivo especial `config.yaml` na raiz poderia conter configurações globais do Arca (por exemplo, nome do sistema, usuário responsável, etc.).

O sistema deve ser configurado para saber onde estão os arquivos de conteúdo. Essa configuração pode ser feita via um arquivo de configuração do Arca ou parâmetros de inicialização, definindo o caminho raiz do conteúdo e possivelmente extensões ou padrões de arquivo a considerar (por padrão, `*.md` e `*.yaml` no diretório de conteúdo).

Em resumo, o Arca mantém os **dados do usuário separados do código**: todo conteúdo dinâmico reside no diretório configurado (fácil de versionar, sincronizar ou editar), enquanto o código e estrutura do sistema ficam em outro lugar.

### Estrutura Recomendada de Diretórios e Arquivos

Para manter o projeto organizado e extensível, recomenda-se a seguinte estrutura de diretórios e arquivos no repositório do Arca:

```
arca_project/
├── arca/                 # Pacote principal do aplicativo Arca
│   ├── __init__.py
│   ├── core/             # Núcleo da aplicação (lógica principal e baixo nível)
│   │   ├── watcher.py    # Módulo de monitoramento de arquivos
│   │   ├── parser.py     # Módulo para parsear Markdown e YAML
│   │   ├── models.py     # Definições de modelos de dados (Pydantic, possivelmente ORM)
│   │   ├── db.py         # Módulo de acesso ao banco de dados SQLite (CRUD e consultas)
│   │   └── utils.py      # Funções utilitárias (ex: formatação de datas, auxiliares)
│   ├── api/              # Lógica de backend e definição das rotas FastAPI
│   │   ├── __init__.py
│   │   ├── routes.py     # Definição das rotas (endpoints) da API/backend
│   │   ├── controllers.py# Funções que implementam as regras de negócio para cada rota
│   │   └── schemas.py    # (Opcional) Definições de schemas Pydantic para requests/responses da API
│   ├── ui/               # Componentes de interface (FastHTML + HTMX)
│   │   ├── __init__.py
│   │   ├── components/   # Componentes reutilizáveis de UI
│   │   │   ├── list_view.py     # Exemplo: componente de lista de itens
│   │   │   ├── detail_view.py   # Exemplo: componente de detalhe de item
│   │   │   └── ...              # Outros componentes de UI
│   │   ├── pages.py      # Montagem de páginas completas combinando componentes
│   │   └── static/       # Arquivos estáticos (CSS, JS do HTMX, imagens de interface)
│   ├── cli/              # Implementação da interface de linha de comando
│   │   ├── __init__.py
│   │   └── main.py       # Definição dos comandos CLI (usando Click/Typer)
│   └── config.py         # Configurações gerais do sistema (paths, opções, constantes)
├── content/              # Diretório (ou link) para os arquivos de conteúdo (Markdown/YAML)
│   └── ...               # (Estrutura de arquivos de conteúdo conforme explicado acima)
├── tests/                # Suíte de testes automatizados
│   └── ...               # (Testes unitários para parser, watchers, API, etc.)
├── requirements.txt      # Dependências de pacotes Python
├── README.md             # Documentação do projeto
└── main.py               # Script de entrada para rodar o Arca (inicia CLI ou servidor)
```

**Descrição da estrutura:**

- O código fonte do Arca fica no pacote `arca/`, contendo submódulos para cada responsabilidade (núcleo, API, UI, CLI).
- Os arquivos de **conteúdo do usuário** ficam fora do pacote de código, facilitando sua atualização independente. Essa pasta pode ser apontada por uma configuração (e pode ser externa ao projeto se desejado).
- A pasta `core` abriga funcionalidades gerais independentes de frameworks (como monitoramento, parsing, acesso ao DB). A pasta `api` integra essas funcionalidades ao framework FastAPI (definindo endpoints e usando a lógica do core).
- A pasta `ui` contém os elementos de interface construídos com FastHTML e recursos estáticos como CSS e scripts HTMX. Isso mantém separada a lógica de servidor da formatação visual.
- `cli` fornece um ponto de entrada para executar o programa via terminal, definindo comandos e opções.
- A presença de `tests` é recomendada para garantir que cada parte funcione isoladamente (por exemplo, testar que o parser extrai corretamente os dados YAML, ou que o watcher reage a mudanças conforme esperado).
- O arquivo `config.py` ou similar consolida constantes e configurações (por exemplo, versão do esquema, opções de debug, etc.), podendo carregar também configurações de um `config.yaml` se decidido ter config em YAML.
- O arquivo `main.py` é a entrada do programa, possivelmente chamando a CLI ou rodando diretamente o servidor, conforme parâmetros.

Essa estrutura modular sugere uma separação clara entre:

- **Conteúdo do usuário** (`content/`)
- **Código da aplicação** (`arca/`)
- **Interface de uso** (CLI, UI)
- **Configuração e utilidades** (`config.py`, CLI)
- **Dados efêmeros** (o banco SQLite, se persistido em disco, pode ficar em um local designado, como `arca/arca.db` ou uma pasta de cache/temporária).

Mantendo essa organização, a implementação torna-se mais limpa e facilita futuras extensões, além de ajudar um LLM ou desenvolvedor a navegar pelo projeto entendendo rapidamente onde estão as diferentes partes.

## 4. Banco de Dados Efêmero (SQLite)

### Estratégia de Armazenamento

O Arca utiliza um banco de dados SQLite como armazenamento efêmero para indexar e facilitar o acesso ao conteúdo dos arquivos Markdown/YAML. A natureza "efêmera" significa que este banco de dados não é a fonte autoritativa dos dados e pode ser descartado e reconstruído a partir dos arquivos sempre que necessário. A estratégia de armazenamento foca em simplicidade e velocidade:

- **Esquema de Dados:** O banco de dados é projetado para armazenar as informações essenciais extraídas dos arquivos. Por exemplo, pode haver uma tabela principal `documentos` com colunas como:

  - `id` (identificador único, possivelmente o caminho ou um hash do caminho do arquivo),
  - `titulo`,
  - `conteudo_markdown` (ou possivelmente a versão HTML gerada do Markdown),
  - campos correspondentes aos metadados importantes (por exemplo, `data`, `autor`, `tags`, etc., se aplicável).

  Alternativamente, os metadados YAML podem ser armazenados em uma coluna única estruturada (por exemplo, JSON) para flexibilidade, caso os campos variem muito entre documentos. Se o sistema esperar tipos distintos de conteúdo com campos diferentes, poderíamos ter tabelas separadas (ex: `projetos`, `usuarios`) ou incluir um campo `tipo` em cada registro para distinguir e usar colunas extras conforme o tipo.

- **Armazenamento em Memória vs. Disco:** Por padrão, o SQLite pode rodar em memória (`:memory:`) para velocidade máxima, tornando-se realmente efêmero (não persistindo nada em disco). Entretanto, em muitos casos utilizaremos um arquivo de banco de dados temporário (por exemplo `./arca_cache.db`) durante a execução. Isso facilita depuração (podemos inspecionar o conteúdo indexado usando ferramentas SQLite) e permite reutilizar o índice se o sistema for reiniciado rapidamente sem mudanças nos arquivos. De qualquer forma, a premissa é que se o banco for limpo ou perdido, ele pode ser recriado integralmente lendo os arquivos de conteúdo.

- **Mapeamento Objeto-Relacional (ORM) ou Acesso Direto:** Para interagir com o SQLite, podemos usar acesso direto via bibliotecas padrão (como o módulo `sqlite3` do Python executando comandos SQL) ou utilizar um mini-ORM. Dado o escopo enxuto e a integração com Pydantic, uma opção conveniente é usar **SQLModel** (um ORM leve baseado em SQLAlchemy e Pydantic) para mapear modelos de dados Python às tabelas SQLite. Com SQLModel, por exemplo, podemos definir classes que representam as tabelas (derivadas de `sqlmodel.SQLModel`) espelhando os modelos Pydantic, facilitando inserções e consultas. Alternativamente, podemos manter as coisas simples e executar consultas SQL manualmente através de funções no módulo `db.py`, já que o esquema é relativamente simples e conhecido.

Em suma, o banco de dados é estruturado de forma a refletir os dados chave do conteúdo, favorecendo consultas rápidas e data access seguro, sem duplicar toda a informação dos arquivos (por exemplo, pode não fazer sentido armazenar todo o corpo do Markdown se o tamanho for muito grande e se for possível parsear on-the-fly – mas, por performance, possivelmente armazenaremos o corpo ou a versão HTML do corpo para não precisar reparsear a cada requisição).

### Atualização Incremental

A atualização do banco de dados é feita de forma incremental para refletir mudanças nos arquivos, minimizando reprocessamento:

- **Inserção Inicial:** Na inicialização (passo 1 do fluxo geral), após ler todos os arquivos, o Arca insere cada entrada no SQLite. Esta operação pode ser feita em lote (usando transações para agrupar múltiplos inserts) ou de forma individual, dependendo da implementação. O importante é que o estado inicial do banco represente fielmente todos os arquivos encontrados.

- **Detecção de Mudanças:** Com os watchers ativados, quando um evento de arquivo ocorre, o sistema identifica qual arquivo foi afetado e de que tipo de evento se trata (criação, modificação ou deleção).

- **Processamento de Criação/Modificação:** Para novos arquivos ou arquivos alterados, o processo de ingestão carrega o conteúdo e metadados do arquivo atualizado. Em seguida:

  - Se o arquivo for **novo**, um novo registro é inserido na tabela correspondente. Por exemplo, um novo documento recebe um novo `id` (ou usa seu caminho como chave) e todos os seus campos são preenchidos via uma operação INSERT no banco.
  - Se o arquivo já existia (eventos de **modificação**), o sistema realiza uma atualização seletiva: somente os campos que podem ter mudado são atualizados. Na prática, como tanto o conteúdo quanto algum metadado podem ter mudado, é comum atualizar todos os campos associados àquele registro. Utiliza-se uma query UPDATE filtrando pelo identificador (ex.: `UPDATE documentos SET titulo=?, conteudo_markdown=?, data=? ... WHERE id = ?`). Antes de atualizar, o novo conteúdo passa novamente pela validação YAML e, se relevante, o Markdown é reconvertido para HTML, para garantir que o banco sempre tenha dados consistentes e prontos para uso.

- **Processamento de Remoção:** Se um arquivo foi **deletado**, o sistema identifica sua chave (por exemplo, o caminho ou ID) e remove o registro correspondente do SQLite (operação DELETE). Além disso, se houver tabelas relacionadas (por exemplo, uma tabela separada de tags vinculadas a documentos), deve-se remover ou atualizar essas entradas para não deixar dados órfãos. Idealmente, o esquema do SQLite usará chaves estrangeiras com ON DELETE CASCADE ou a lógica de negócio cuidará de remover entradas associadas.

- **Consistência e Concorrência:** O SQLite suporta múltiplas conexões, mas apenas uma escrita por vez (as escritas lockeiam o banco durante a transação). Para evitar conflitos, o Arca adota uma estratégia simples: todas as atualizações provenientes dos watchers são enfileiradas e executadas sequencialmente, garantindo que apenas uma transação de escrita ocorra por vez. Leituras (consultas feitas pelo backend para atender requisições) podem ocorrer em paralelo; o SQLite permite múltiplas leituras simultâneas mesmo durante escritas curtas. Assim, o impacto de performance durante uma atualização é mínimo e de curta duração.

- **Controle de Versão do Índice:** Opcionalmente, pode-se manter no banco um campo de versão ou timestamp indicando a última atualização de cada registro ou do conjunto de dados. Isso poderia ajudar, por exemplo, a rapidamente ver se o índice está atualizado em relação aos arquivos (embora os watchers já garantam isso, um campo `ultima_atualizacao` por registro ajuda em debug e validações). Porém, dada a natureza efêmera, isso é mais para conferência – o controle histórico real é delegado ao versionamento de arquivos, não ao banco.

Resumindo, o Arca realiza atualizações no banco de forma **pontual e eficiente**: em vez de reconstruir tudo a cada mudança, ele insere/atualiza/remove apenas o que foi afetado, mantendo o custo de sincronização baixo mesmo com um volume grande de conteúdo.

### Índices e Performance

Para garantir respostas rápidas, mesmo com crescimento do número de conteúdos, são utilizados índices adequados no SQLite:

- **Índice Primário:** O identificador de cada documento (por exemplo, o caminho do arquivo ou um ID numérico) atua como chave primária da tabela principal e é automaticamente indexado. Isso permite buscas eficientes por ID, o que é útil para recuperar um item específico (por exemplo, ao navegar para a página de detalhe de um documento, usa-se seu ID/index como chave de busca).

- **Índices em Campos de Filtro:** Se o sistema oferecer funcionalidades de busca ou filtragem (por exemplo, filtrar documentos por tag, data ou categoria), é importante indexar esses campos. Por exemplo, pode-se criar um índice em `data` se frequentemente listarmos documentos ordenados ou filtrados por data; um índice em `autor` se quisermos buscar todos documentos de um autor específico. Se tags forem armazenadas em uma tabela separada de relacionamento (muitos-para-muitos), então índices sobre a tabela de associação (`documento_id` e `tag`) aceleram essas consultas.

- **Full-Text Search (FTS):** Para buscas de texto completo no conteúdo dos documentos, o SQLite oferece extensões FTS5 que permitem indexar texto livre com eficiência. O Arca pode opcionalmente criar uma tabela virtual FTS para o conteúdo (e talvez título) dos documentos, possibilitando consultas por palavra-chave muito rápidas. Essa feature seria útil se o projeto incluir uma funcionalidade de pesquisa global robusta. Caso contrário, uma busca simples pode ser implementada com LIKE no conteúdo (adequado apenas para conjuntos pequenos ou médios de dados).

- **Tamanho e Escalabilidade:** O SQLite lida bem com milhares de registros e bancos até gigabytes, mas o Arca espera normalmente volumes moderados (documentação, notas ou projetos de porte médio). Com índices corretos, listagens e buscas devem ser praticamente instantâneas para o usuário. Devemos garantir que operações custosas (como reindexar todo o conteúdo ou revalidar tudo) só ocorram quando necessário (por exemplo, se o usuário explicitamente reiniciar ou rodar um comando de rebuild). A atualização incremental evita ter que reprocessar tudo com frequência, mantendo o desempenho estável.

- **Manejo de Migrações:** Sendo o banco efêmero e dependente do esquema de arquivos, mudanças no esquema do banco não são críticas – podemos simplesmente dropar e recriar. Ainda assim, para facilidade de desenvolvimento, poderíamos usar migrações simples (via Alembic ou SQLModel) se quisermos preservar caches. Porém, no espírito KISS (_keep it simple_), é mais fácil regenerar o banco quando o código do Arca é atualizado para uma versão com esquema diferente, já que a fonte final (arquivos) não muda.

Em suma, o banco SQLite serve para otimizar o acesso e a consulta, mas sem introduzir dependência forte: o sistema permanece focado nos arquivos como fonte permanente e no SQLite apenas como uma ferramenta de agilidade. A configuração padrão preza por performance suficiente para rodar localmente, sem requerer servidores de banco de dados dedicados ou manutenção complexa.

## 5. Validação e Schema YAML

### Definição de Schemas YAML

Para garantir consistência dos dados, o Arca define esquemas formais para todos os conteúdos YAML esperados. Isso é feito através de modelos de dados que descrevem os campos e tipos permitidos em cada YAML, usando as facilidades do Pydantic:

- **Modelos Pydantic:** Utilizamos **Pydantic** para declarar classes Python correspondentes ao formato esperado dos metadados. Por exemplo, podemos ter uma classe `DocumentoMeta` (herdando de `pydantic.BaseModel`) com atributos como `titulo: str`, `data: datetime`, `autor: Optional[str]`, `tags: List[str]`, etc. Cada atributo representa uma chave esperada no YAML e possui um tipo específico. Esses modelos servem como _schemas_ (esquemas) para validação.

- **Múltiplos Schemas (se necessário):** Se houver diferentes tipos de conteúdo com metadados distintos, definimos múltiplos modelos Pydantic. Por exemplo, além de documentos de texto, se o Arca gerencia uma lista de projetos com campos próprios (deadline, status, membros), poderíamos ter uma classe `ProjetoMeta` com campos correspondentes. Nesse caso, precisamos de uma forma de identificar qual schema aplicar a um dado arquivo. Isso pode ser feito:

  - Pelo contexto (ex: todos os YAML na pasta `projetos/` usam o schema de projeto),
  - Ou por um campo no próprio YAML (ex: `tipo: projeto`),
  - Ou mesmo pelo nome do arquivo.
    Em muitos casos simples, todos os documentos compartilham o mesmo esquema de metadados, então um único modelo Pydantic basta.

- **Validações Complexas:** Os schemas podem incluir validações além dos tipos básicos. Pydantic permite, por exemplo, definir restrições (como valor mínimo/máximo, regex para strings) ou transformações (converter automaticamente strings para datetime). Também é possível usar validadores personalizados do Pydantic (`@validator`) para checagens interdependentes, caso necessário (por exemplo, garantir que se um campo "status" for "concluído", então a data de conclusão esteja preenchida). Isso permite que a _lógica de negócio de integridade_ seja em parte resolvida já na fase de validação de dados, antes de chegar ao resto do sistema.

- **Documentação do Schema:** Todos os schemas YAML do Arca devem ser documentados para os usuários saberem como preencher os metadados corretamente. Essa documentação pode constar no README ou wiki do projeto, descrevendo cada campo, tipo e obrigatoriedade. Idealmente, exemplos de YAML válidos são fornecidos. Isso é importante porque, como o Arca espera certos campos, quem for editar ou adicionar conteúdos precisa seguir o padrão para que o sistema aceite.

### Validação com Pydantic

O processo de validação ocorre automaticamente durante a ingestão de cada arquivo:

- **Parsing YAML para Objeto:** Quando um watcher (ou a rotina de carga inicial) detecta um arquivo YAML ou um bloco YAML em um Markdown, o conteúdo YAML (carregado via uma biblioteca como PyYAML ou `ruamel.yaml`) é transformado em um dicionário Python. Em seguida, o Arca seleciona o modelo Pydantic apropriado e tenta criar uma instância desse modelo a partir do dicionário. Por exemplo: `meta = DocumentoMeta(**dados_yaml)`.

- **Comportamento do Pydantic:** Ao instanciar o modelo:

  - Ele **converte tipos** automaticamente quando possível (e.g., strings para datetime se o campo for datetime, inteiros para strings, etc., conforme especificado).
  - Verifica a presença de todos os **campos obrigatórios** (se algum campo definido no modelo não estiver no YAML e não tiver um valor padrão, ocorrerá erro).
  - Aplica quaisquer **validações personalizadas** definidas (por exemplo, um validador poderia assegurar que a lista de tags não esteja vazia, ou que uma string corresponda a certo padrão).
  - Se tudo estiver correto, a instância `meta` será criada contendo os dados tipados.

- **Sucesso na Validação:** Se a validação for bem-sucedida, obtemos um objeto Python do modelo, já com os tipos coerentes. Esse objeto pode então ser:

  - Diretamente usado para inserir dados no SQLite (por exemplo, usando `meta.dict()` para obter um dicionário nativo com valores prontos para serem gravados).
  - Usado pelo backend para preencher templates ou respostas (por exemplo, `meta.titulo` já seria uma string confiável).
  - Armazenado em cache em memória se for útil (embora neste projeto provavelmente usaremos diretamente a escrita no DB).

- **Falha na Validação:** Se a validação falhar, o Arca trata o erro de forma controlada:

  - Registra (em log ou console) uma mensagem indicando qual arquivo e qual campo causou problema, para que o usuário possa corrigir. Exemplo de mensagem: _"Erro de validação em 'projetos/projeto1.yaml': campo 'data' ausente ou formato inválido."_
  - Decide como proceder com o conteúdo problemático. Em geral, a estratégia padrão é **ignorar ou não indexar** conteúdo inválido para evitar comportamento imprevisível. Isso significa que se um arquivo contém metadados fora do padrão, ele não aparecerá na interface até ser corrigido (ou aparecerá parcialmente se somente parte dos dados for usada). Em alguns casos, poderíamos optar por indexar parcialmente (por exemplo, armazenar o conteúdo Markdown mas deixar certos campos em branco), mas isso deve ser bem pensado para não mascarar erros.
  - Aplica valores default quando definidos: Pydantic permite definir valores padrão para campos. Então, se um campo opcional estiver ausente, o modelo simplesmente usa o default (sem erro). Isso deve ser aproveitado para campos que realmente podem faltar. Dessa forma, a validação só falha em caso de problemas graves ou ausência de campos essenciais.

- **Integração Contínua:** Essa validação ocorre tanto na carga inicial de todos os arquivos quanto em cada atualização detectada pelos watchers. Ou seja, se um arquivo for editado e ficar com um YAML inválido, no momento de reingestão aquele arquivo será rejeitado ou marcado como erro, mas isso não derruba o sistema – apenas impede aquela atualização específica. O restante do Arca continua funcionando e atendendo outros conteúdos.

- **Validação de Saída:** Pydantic também pode ser utilizado no retorno de dados via API (schemas de resposta), garantindo que o backend só envie dados no formato esperado. Por exemplo, podemos definir modelos Pydantic para as respostas JSON da API (como `DocumentoResposta` contendo título, conteúdo, etc.) e retornar instâncias deles. O FastAPI integrará esses modelos na documentação OpenAPI automaticamente. No contexto do Arca, como muitas rotas retornam HTML, essa parte é secundária; mas para endpoints /api, seria útil.

Em resumo, o uso de Pydantic proporciona uma camada robusta de validação e conversão de dados entre YAML e as estruturas internas do Arca. Isso diminui a chance de erros ocultos e fornece feedback imediato aos usuários que escrevem os arquivos YAML, incentivando boas práticas de formatação de dados.

### Verificação dos Dados antes do Uso

Antes que qualquer dado do YAML seja efetivamente usado pelo sistema (seja exibido na interface ou gravado no banco), ele passa pelo crivo da validação. Esse processo de verificação prévia garante integridade e conformidade, e traz diversos benefícios:

- **Prevenção de Erros em Tempo de Execução:** Ao validar os dados logo ao carregar o arquivo, evitamos situações em que campos ausentes ou valores inesperados causem exceções no meio de uma operação do backend ou frontend. Por exemplo, se a interface espera que todo documento tenha um campo `titulo` para exibir, a validação assegura que ou o título está presente (ou um padrão foi fornecido), ou então o documento nem será indexado se faltar essa informação crucial. Isso evita bugs como `AttributeError` ou páginas quebradas por falta de dados.

- **Mensagens de Diagnóstico:** Ao rejeitar dados inválidos, o sistema pode notificar de forma clara (no log ou em uma seção de diagnóstico da UI, se implementarmos) quais arquivos não foram indexados e por quê. Isso é importante para a experiência do desenvolvedor/usuário que está alimentando o Arca com conteúdo; ele deve saber se cometeu um erro no YAML para corrigi-lo rapidamente. Em desenvolvimento, essas mensagens ajudam a depurar problemas nos schemas.

- **Tolerância e Continuidade:** A validação de cada arquivo é isolada; um YAML malformado não impede que outros conteúdos sejam carregados. Isso significa que o sistema se degrada graciosamente: em vez de travar por causa de um erro, ele simplesmente ignora aquele conteúdo problemático e continua servindo os demais conteúdos válidos. Assim, um erro em um item específico não tira o sistema inteiro do ar.

- **Validação de Consistência Cruzada (futuro):** No escopo atual, a validação via Pydantic cobre apenas cada unidade de conteúdo individualmente. Se houvesse regras de consistência entre arquivos (por exemplo, um projeto referenciando um usuário que deve existir), isso exigiria lógica adicional no backend ou em um processo de pós-validação. No plano atual, mantemos a independência de cada arquivo para simplicidade. Mas futuramente, poderíamos adicionar verificações globais (ex: um plugin que verifique se todas as referências X existem).

- **Conformidade com Esquemas Evolutivos:** Caso os schemas evoluam ao longo do tempo (por exemplo, adicionando novos campos obrigatórios em uma versão futura do Arca), poderemos detectar quais arquivos estão desatualizados. Por ora, isso não se aplica, mas a estrutura com Pydantic permite gerenciar versões de modelos se necessário, facilitando migrações (por exemplo, marcando campos antigos como deprecados e logando avisos se ainda forem usados nos YAML).

Em essência, nenhum dado entra no "motor" do Arca sem antes ser conferido. Isso fornece segurança de que o que chega ao usuário final e às funções internas está conforme o esperado, reduzindo necessidade de depuração posterior e garantindo previsibilidade. A validação atua como uma fronteira de proteção entre a fonte de dados (que pode ser manipulada manualmente pelos usuários) e o sistema automatizado.

## 6. Backend (FastAPI)

### Rotas e Endpoints

O backend do Arca, construído com FastAPI, expõe uma série de rotas HTTP que permitem ao frontend (ou outros clientes) acessar os dados e funcionalidades do sistema. Estas rotas são desenhadas tanto para servir páginas inteiras quanto fragmentos (no caso de HTMX) ou dados estruturados (JSON, no caso de uso via API). Principais endpoints previstos:

- **Rota Raiz (`GET /`):** Fornece a página inicial da aplicação. Normalmente, essa página pode listar os principais conteúdos ou categorias disponíveis, servindo como um ponto de partida para o usuário. Em termos de implementação, essa rota provavelmente usa FastHTML para montar um HTML com a estrutura básica do aplicativo (por exemplo, cabeçalho com nome do sistema, um menu ou barra lateral, e um contêiner central vazio ou com um resumo). A lista de itens iniciais (se houver) pode ser inserida ali ou carregada via HTMX logo após. Se a interface for single-page, essa rota já carrega um layout geral e talvez alguns dados iniciais.

- **Listagem de Conteúdos (`GET /documentos` ou similar):** Endpoint para obter uma lista de documentos ou itens. Pode servir uma página completa ou, se chamado via HTMX, retornar apenas o fragmento HTML da lista de itens. Essa rota consultaria o SQLite para pegar todos os documentos (ou talvez aplicar um filtro/ordenação padrão, como por data ou categoria) e os enviaria para um componente de template que gera a listagem (por exemplo, uma `<ul>` com `<li>` para cada documento, ou cards). Se houver categorias, poderíamos ter rotas como `/projetos` listando só os projetos, etc., organizando conforme a estrutura de conteúdo.

- **Detalhe de Conteúdo (`GET /documentos/{id}`):** Endpoint para obter os detalhes de um documento específico identificado por `id` (ou por um slug/caminho). Ao ser acessado diretamente (via navegador ou via HTMX), retorna o conteúdo completo: título, metadata formatada e corpo (conteúdo) convertido em HTML. Esse endpoint busca no banco o item correspondente e usa componentes FastHTML para montar a exibição. Via HTMX, provavelmente retornaremos apenas o `<div>` com o detalhe para inserção na página; acessando diretamente, podemos retornar a página inteira (incluindo layout comum) para permitir bookmark/share do link.

- **Endpoints de API (JSON):** Além das rotas que servem HTML para o próprio app, o Arca pode expor endpoints RESTful para integração ou uso programático. Exemplos:

  - `GET /api/documentos` – retorna JSON com a lista de documentos (cada item com campos básicos como id, título, talvez um resumo curto).
  - `GET /api/documentos/{id}` – retorna JSON com todos os dados do documento identificado, incluindo metadados e conteúdo (talvez o conteúdo em Markdown ou HTML puro).
  - `POST /api/documentos` – permitir criar um novo documento enviando JSON com campos (esse e os seguintes apenas se implementarmos criação via API).
  - `PUT /api/documentos/{id}` – atualizar um documento existente.
  - `DELETE /api/documentos/{id}` – remover um documento.

  Esses endpoints facilitam integração com outros sistemas, ou mesmo a criação de um cliente alternativo (por exemplo, um aplicativo móvel que consome a API). Como o foco inicial é a interface web própria, podemos implementá-los gradualmente. De qualquer forma, graças ao FastAPI, é relativamente simples adicionar esses endpoints aproveitando os mesmos modelos Pydantic de validação.

- **Busca (`GET /buscar?q=texto`):** Se implementada a funcionalidade de busca, uma rota de busca aceita um parâmetro de query (`q`) e retorna resultados correspondentes. Via frontend, isso poderia ser acionado por um formulário ou barra de busca, e, usando HTMX, atualiza a lista de itens com os resultados filtrados. Internamente, o backend consultaria o SQLite (possivelmente usando a funcionalidade FTS mencionada ou uma busca por título/conteúdo) e monta uma lista de resultados. Esse endpoint poderia ser `GET /buscar` retornando HTML (lista de resultados) ou `/api/busca` retornando JSON com resultados, ou ambos.

- **Atualizações/Criação de Conteúdo (`POST /documentos` e `PUT/PATCH /documentos/{id}`):** Caso o escopo do Arca inclua edição de conteúdo via web, então rotas para criar novos documentos ou atualizar existentes precisam ser definidas. Por exemplo, um `POST /documentos` receberia dados (talvez de um formulário HTMX ou JSON) com conteúdo Markdown e metadados, criaria um novo arquivo .md (e .yaml se aplicável) no sistema de arquivos e retornaria sucesso ou o conteúdo criado. Similarmente, um `PATCH /documentos/{id}` para editar um documento encontraria o arquivo correspondente e aplicaria mudanças. No MVP do Arca, podemos inicialmente não oferecer edição via UI (focando em leitura/visualização), mas deixar as rotas previstas para futura implementação.

- **Rotas de Utilidades/Administração:** Poderíamos incluir endpoints para operações administrativas ou de utilidade, por exemplo:

  - `POST /recarregar` ou `/sync`: forçar reescaneamento de todos os arquivos (por exemplo, se o usuário suspeita de algo fora de sincronia, apesar dos watchers).
  - `GET /status`: retorna informações sobre o estado do sistema (quantos docs indexados, última atualização).
  - Se houver autenticação no futuro, rotas de login/logout (`/login`, `/logout`) seriam parte do backend também.

- **Recursos Estáticos:** Embora não sejam "rotas de lógica de negócio", o Arca provavelmente precisa servir arquivos estáticos (especialmente se os documentos incluem imagens ou se temos CSS/JS do frontend). FastAPI permite montar um StaticFiles para servir, por exemplo, a pasta `content/` para imagens (com cuidado, talvez filtrar para não expor YAML via web desnecessariamente), ou uma pasta `ui/static` para estilos. Podemos definir que URLs começando com `/static/` mapeiam para um diretório local específico. Assim, se um Markdown referencia `![Diagrama](static/img/diagrama.png)`, a aplicação consegue servir esse arquivo.

Todas essas rotas serão organizadas usando as facilidades do FastAPI. Podemos agrupar rotas relacionadas em **routers** separados. Por exemplo, um router para conteúdo principal (`router_conteudo`) com prefixo `/documentos` e outro router para API (`router_api`) com prefixo `/api`. Isso mantém o código organizado e permite desabilitar ou modificar facilmente um conjunto de endpoints sem afetar outro.

### Lógica de Negócio

A lógica de negócio do backend se encarrega de orquestrar as operações quando uma rota é acessada. Enquanto as rotas definem "o quê" (qual recurso ou ação), a lógica de negócio define "como" isso acontece. Principais responsabilidades dessa lógica:

- **Consulta de Dados:** Quando uma rota de leitura (GET) é chamada, a lógica consulta o banco efêmero para obter os dados solicitados. Isso pode ser feito via funções dedicadas no módulo de dados (por exemplo, `db.get_all_documents()` ou `db.get_document(id)`), que encapsulam as queries SQL ou chamadas ORM correspondentes. A lógica de negócio em si fica simples: receber a requisição, chamar a função de dados apropriada, e guardar o resultado (por exemplo, uma lista de documentos ou um documento único). Em caso de registros não encontrados, esta é a etapa em que se detecta e lida com isso (retornando 404 se um id não tiver correspondência).

- **Formatação e Preparação:** Após obter os dados brutos do banco, a lógica prepara os dados para envio ao cliente. Se for uma rota HTML, isso envolve possivelmente converter o conteúdo Markdown em HTML (caso não tenhamos armazenado a versão HTML), sanitizar/escapar onde necessário e organizar as informações em estruturas adequadas para os componentes FastHTML. Por exemplo, formatar a data para um formato legível antes de passá-la ao template, ou calcular campos derivados (como um tempo estimado de leitura a partir do número de palavras, caso quisermos mostrar isso). Se for uma rota JSON, a lógica pode converter objetos Pydantic em `dict` ou diretamente retornar modelos (FastAPI faz isso automaticamente). A formatação inclui também decidir quais dados enviar: por exemplo, podemos omitir conteúdo muito grande em listagens (enviar só um resumo) e enviar o conteúdo completo apenas na rota de detalhe.

- **Regras Específicas de Negócio:** Quaisquer regras particulares definidas para o domínio do Arca são aplicadas aqui. Por exemplo:

  - Se houver um campo `publicado` nos metadados e está false, a lógica de listagem poderia filtrar esses documentos para não serem listados para usuários (talvez só admin veja).
  - Se documentos têm relações (ex: um projeto tem várias notas associadas), a lógica de detalhe de projeto poderia também buscar e incluir essas notas.
  - Controle de acesso simples (antes de ter autenticação robusta): poderíamos, por configuração, marcar certas categorias como restritas e o backend decide não servi-las se não for admin, etc. (Isso é especulativo, mas exemplifica lógica de negócio além do CRUD básico).
  - Ao criar um novo documento via API, a lógica de negócio poderia aplicar regras como gerar um ID único (slug) baseado no título, garantir que não há duplicata, etc.

- **Persistência de Mudanças:** Nos endpoints de escrita (POST/PUT/PATCH), a lógica vai receber dados de entrada (via um modelo Pydantic do request ou via campos de formulário) e aplicar mudanças correspondentes nos arquivos de conteúdo. Isso envolve:

  - Converter a requisição em formato interno: por exemplo, no caso de criação de documento, pegar um objeto Pydantic representando o novo doc e transformá-lo em texto Markdown/YAML.
  - **Escrita em disco:** Gravamos o novo arquivo `.md` (e `.yaml` se houver metadados separados) no sistema de arquivos, no local apropriado. Essa operação deve ser segura: idealmente usar escrita atômica (escrever em arquivo temporário e renomear) para evitar corromper em caso de falha.
  - Uma vez escrito o arquivo, o watcher detectará a mudança e atualizará o banco automaticamente. Podemos, se necessário, forçar a atualização chamando manualmente a rotina de ingestão para não esperar pelo watcher (embora normalmente a espera seja mínima).
  - Após a persistência, a lógica decide o que retornar: talvez os dados do novo documento (já validados) ou um simples status de sucesso. Em caso de edição, possivelmente retorna o novo conteúdo atualizado para atualizar a interface via HTMX.

- **Tratamento de Erros e Exceções:** A lógica de negócio também trata condições de erro:

  - Se um documento não for encontrado (por exemplo, id inexistente), retorna-se uma resposta HTTP 404 através de `HTTPException` do FastAPI.
  - Se ocorrer um erro ao ler ou escrever no disco (falta de permissão, disco cheio), isso deve ser capturado e uma resposta 500 ou 503 apropriada enviada, possivelmente com uma mensagem amigável.
  - Erros de validação de entrada (em endpoints de escrita) geram respostas 422 automáticas no FastAPI (se usando Pydantic nos parâmetros). Podemos customizar a mensagem, mas geralmente não é necessário.
  - Caso alguma regra de negócio não permita a operação (por exemplo, tentativa de criar documento com ID duplicado), retornar um 409 (Conflito) ou 400 (Bad Request) com mensagem clara.

- **Desempenho e Cache:** Em alguns casos, a lógica pode optar por otimizações de desempenho. Por exemplo:
  - Se o conteúdo Markdown for muito pesado para converter toda hora, podemos armazenar a versão HTML no banco ou em cache em memória quando a conversão for feita pela primeira vez, evitando reconverter repetidamente enquanto o arquivo não muda.
  - Se uma lista de documentos é solicitada com frequência e o conteúdo não muda, poderíamos cachear o resultado (por exemplo, guardar o HTML gerado da lista por alguns segundos). Entretanto, no Arca as mudanças podem ocorrer a qualquer momento via arquivos, então caches teriam que ser invalidados pelos watchers. A princípio, manteremos as coisas simples sem caches complexos, confiando no SQLite e no desempenho local.

Em suma, a lógica de negócio do Arca permanece relativamente simples, pois estamos basicamente repassando conteúdo do ponto A (arquivos) para ponto B (frontend) com validação intermediária. Ao manter a maior parte da "inteligência" nos arquivos (metadados bem estruturados) e na camada de validação, o backend atua principalmente como **orquestrador confiável de dados** e aplicador de regras de integridade.

### Comunicação com Frontend e Banco de Dados

A comunicação entre as camadas (frontend <-> backend <-> banco de dados) acontece da seguinte maneira dentro do backend:

- **Comunicação com o Banco de Dados:** O backend interage com o SQLite através de funções ou métodos internos do módulo `db`. Ao iniciar o aplicativo FastAPI, ele pode abrir uma conexão com o banco (ou utilizar conexões sob demanda). Como o SQLite está no mesmo processo, podemos mantê-lo simples:

  - Podemos usar uma única conexão compartilhada entre as requisições (Thread-local se for multi-thread, ou uma conexão por thread se necessário configurar `check_same_thread=False` no sqlite3). Com SQLAlchemy/SQLModel, usaríamos uma sessão por request geralmente.
  - Consultas típicas incluem seleção de documentos por critérios ou id; junções com outras tabelas (se houver).
  - Atualizações diretas pelo backend ocorrerão principalmente se implementarmos criação/edição via API, pois normalmente as atualizações vêm do watcher. Nesses casos, como descrito, podemos escrever no arquivo e deixar o watcher cuidar do DB, ou o backend escrever no DB também.
  - O design preferido: o backend em operações de escrita **não escreve diretamente no banco**, apenas no arquivo, e confia no watcher para refletir isso no banco. Assim mantemos uma única fonte de escrita de DB (os watchers), evitando duplicar lógica de inserção. Isso simplifica a coerência (menos risco de divergência entre arquivo e DB).
  - Em operações de leitura, a comunicação com o DB é síncrona e rápida. O SQLite retorna dados que a lógica de negócio usa imediatamente.

- **Comunicação com o Frontend (FastHTML + HTMX):** Em vez de retornar apenas dados puros, muitas das rotas retornam HTML já estruturado via componentes FastHTML:

  - Quando uma rota é chamada por uma interação HTMX, nossa função de rota provavelmente vai montar componentes FastHTML e retorná-los. FastAPI, por padrão, espera que retornemos ou objetos de dados (que converte para JSON) ou `Response`/`HTMLResponse`. O FastHTML, ao criar componentes (por exemplo, `Div(...)`), fornece uma maneira de convertê-los para HTML string. Em alguns casos, integrar FastHTML com FastAPI envolve usar um decorator ou função especial (`@app.get(..., response_class=HTMLResponse)` e retornar uma string HTML gerada).
  - Exemplo: na rota de detalhe, podemos ter algo como:
    ```python
    from fastapi.responses import HTMLResponse
    @app.get("/documentos/{id}", response_class=HTMLResponse)
    def detalhe_documento(id: str):
        doc = db.get_document(id)
        if not doc:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        html_content = renderizar_detalhe(doc)  # função que usa FastHTML para gerar HTML
        return html_content
    ```
    Onde `renderizar_detalhe` poderia usar componentes definidos em `ui/components/detail_view.py` para construir o HTML.
  - Na prática, FastHTML pode permitir retornar diretamente componentes sem chamar `HTMLResponse` explicitamente, mas o conceito é esse: o backend envia já o HTML necessário para o front.
  - Para chamadas via HTMX, esse HTML costuma ser fragmento (por exemplo, sem `<html><body>` inteiros, apenas o conteúdo a inserir). Quando as mesmas rotas são acessadas diretamente (full page load), podemos incluir o layout completo.
  - Com o HTMX, podemos aproveitar recursos como cabeçalhos `HX-Request` que o cliente envia para saber se a requisição veio via HTMX (requisição assíncrona) ou foi navegação normal. Assim, a rota poderia diferenciar:
    - Se `HX-Request` estiver presente: retornar só o HTML fragmento (conteúdo interno).
    - Caso contrário (acesso direto): retornar uma página inteira, incluindo cabeçalho, etc.
      Isso fornece progressivo enhancement e possibilidade de usar a app mesmo sem JS.

- **Atualizações do Cliente:** Conforme discutido, a comunicação é essencialmente _cliente->servidor_ sob demanda. O backend responde mas não inicia contato. Se quisermos notificar o cliente sobre mudanças (como "novo conteúdo disponível"), teríamos que implementar WebSockets ou SSE. No escopo atual, não o faremos, mas é algo que a arquitetura poderia adicionar depois sem mudanças drásticas.

- **Coordenando Estado:** Embora o Arca não seja uma aplicação intensiva em estado de sessão, vale notar:
  - Se adicionarmos autenticação no futuro, a comunicação incluirá cookies/tokens e possivelmente we usaremos recursos do FastAPI para gerenciar usuários nas rotas.
  - Atualmente, qualquer usuário que acessar o servidor Arca obtém os mesmos dados (é uma ferramenta local ou interna). Então não há distinção de sessão no conteúdo entregue.
  - O banco de dados efêmero, em conjunto com watchers, garante que o backend sempre consulte uma fonte atualizada. Portanto, a comunicação backend->DB não precisa se preocupar em verificar timestamps dos arquivos, etc. Confiamos que o watchers já atualizou o DB. Uma precaução: se uma requisição chegar exatamente enquanto um watcher está processando uma atualização, podemos ter uma race condition. Contudo, SQLite vai lockar a escrita; a requisição ou vai:
    - Ver dados antigos (se leu antes da escrita aplicar), ou
    - Esperar brevemente pelo lock e então ler dados novos.
      Isso raramente será notado pelo usuário devido à rapidez. Logo, não nos aprofundamos nisso além de reconhecer que é um comportamento aceitável (um eventual leve atraso ou necessidade de refresh manual).

Em resumo, o backend do Arca age como **cola** entre o DB e o frontend, usando FastAPI para estruturar as comunicações e FastHTML para entregar respostas que o frontend entenda e apresente de forma fluida. Cada camada se comunica usando formatos e protocolos bem estabelecidos (SQL/ORM, funções Python e HTTP/HTML), facilitando entendimento e debug.

## 7. Frontend (FastHTML + HTMX)

### Estrutura de Componentes FastHTML

O frontend do Arca utiliza o **FastHTML** para construir a interface do usuário de forma declarativa em Python. Em vez de templates HTML tradicionais, definimos componentes da interface como funções ou classes Python retornando elementos FastHTML (que representam tags HTML). Essa abordagem facilita a reutilização e a composição de UI. A estrutura de componentes pode ser pensada assim:

- **Componentes Básicos:** São funções ou classes que correspondem a elementos UI autocontidos e reutilizáveis. Por exemplo, um componente `ItemLista(doc)` que recebe os dados de um documento e devolve um elemento `<li>` formatado com título e talvez um resumo, configurado com atributos HTMX (como `hx-get` para carregar detalhes do documento quando clicado). Outro exemplo: um componente `DetalheDocumento(doc)` que formata a exibição completa de um documento (título, metadados e conteúdo). Esses componentes básicos encapsulam a apresentação de uma pequena parte da interface e podem ser usados em diferentes contextos.

- **Componentes Compostos:** São componentes que combinam vários componentes básicos para formar uma seção maior da interface. Por exemplo, um componente `ListaDocumentos(docs)` que recebe uma lista de documentos e monta uma estrutura `<ul>` contendo múltiplos `ItemLista` dentro. Ou um componente `PaginaProjeto(proj, docs)` que exibe detalhes de um projeto e ao lado lista documentos relacionados, reusando `DetalheDocumento` e `ListaDocumentos`. A ideia é evitar repetição: se há um padrão de exibição recorrente, coloca-se em um componente básico, e as páginas (componentes compostos) montam esses padrões conforme necessário.

- **Layout Geral:** Podemos definir um componente de layout padrão da aplicação, que engloba a estrutura comum a todas as páginas (por exemplo, cabeçalho com o título "Arca", possivelmente um menu de navegação ou barra lateral, e um container principal onde o conteúdo específico de cada página é inserido). Esse layout pode ser aplicado nas respostas completas. Por exemplo, uma função `Layout(conteudo)` que retorna um `<div class="pagina">` contendo o cabeçalho fixo e dentro outro `<div>` com o conteúdo passado. Assim, as rotas que entregam página inteira podem fazer `return Layout(PaginaInicial(...))`. Já respostas HTMX podem devolver apenas partes internas para não duplicar header.

- **Encapsulamento via Funções vs. Classes:** O FastHTML permite ambas abordagens. Podemos implementar componentes como simples funções (que retornam estruturas HTML montadas) ou como classes que talvez mantenham algum estado ou métodos auxiliares. No caso do Arca, a maioria dos componentes pode ser funções puras sem estado – elas recebem dados e devolvem HTML, não precisam lembrar de nada entre chamadas. Isso é preferível pela simplicidade. Por outro lado, se quisermos usar OOP, poderíamos criar, por exemplo, uma classe `DocumentoComponent` com métodos `render_lista` e `render_detalhe`, mas isso não parece necessário no momento.

Ao manter componentes pequenos e focados, um desenvolvedor (ou LLM) que implemente a UI pode facilmente mapear cada parte da página a uma função, facilitando o preenchimento de dados e evitando duplicação de código. Além disso, se for preciso alterar a aparência de um item na lista, faz-se em um lugar (`ItemLista`) e reflete em todos os lugares onde é usado.

### Integração com HTMX

O **HTMX** é o motor que traz interatividade à aplicação sem exigir JavaScript manual. A integração do HTMX no FastHTML acontece adicionando atributos `hx-` aos componentes HTML conforme necessário:

- **Navegação Parcial:** Elementos clicáveis (como links ou botões) recebem atributos `hx-get` ou `hx-post` apontando para as rotas do backend que fornecem o conteúdo desejado, e configuram `hx-target` e `hx-swap` para indicar onde inserir a resposta. Por exemplo, um link de documento pode ser representado por:

  ```python
  A(doc.titulo, href=f"/documentos/{doc.id}", hx_get=f"/documentos/{doc.id}", hx_target="#conteudo-detalhe", hx_swap="innerHTML")
  ```

  Nesse caso:

  - `hx-get="/documentos/{id}"` indica que ao clicar, o HTMX fará uma requisição GET para essa URL em vez de navegação padrão.
  - `hx-target="#conteudo-detalhe"` designa o elemento HTML (identificado por id `conteudo-detalhe`) que deverá ser atualizado com a resposta.
  - `hx-swap="innerHTML"` define que o conteúdo interno desse target será substituído pelo resultado retornado (poderia ser `outerHTML` para substituir o próprio elemento alvo, etc., mas innerHTML é comum).

  Assim, quando o usuário clicar no link, o conteúdo de detalhes será carregado e inserido sem recarregar a página inteira. É importante também incluir `href` normal para acessibilidade e caso o usuário abra em nova aba – isso permite comportamento padrão se JS estiver desabilitado.

- **Formulários e Ações:** Se houver formulários (por exemplo, uma busca ou, futuramente, um formulário de edição), podemos usar `hx-post` ou `hx-trigger`. Exemplo de busca autocompletar:

  ```html
  <form
    id="form-busca"
    hx-get="/buscar"
    hx-target="#lista-documentos"
    hx-trigger="keyup changed delay:500ms">
    <input type="text" name="q" placeholder="Buscar..." />
  </form>
  ```

  Neste exemplo hipotético:

  - O formulário captura eventos de tecla (com um atraso de 500ms após o usuário parar de digitar) e envia requisições GET para `/buscar?q=...` automaticamente.
  - O resultado substitui o conteúdo do elemento `#lista-documentos` (que poderia ser a mesma lista onde mostramos todos documentos, agora filtrada).

  Para criação/edição, um formulário poderia usar `hx-post` e no botão de submit atributos `hx-target` para substituir talvez um modal de edição por uma mensagem de sucesso ou pelo conteúdo atualizado.

- **Indicadores de Carregamento:** O HTMX suporta atributos para indicar estado de carregamento. Por exemplo, podemos definir um elemento com `id="loading"` e no link ou form colocar `hx-indicator="#loading"` para que ele apareça enquanto a requisição está em andamento. Assim, fornecemos feedback visual ao usuário (um spinner, texto "Carregando...", etc.).

- **Controle de Degradação:** Um ponto forte do HTMX é que ele se sobrepõe ao comportamento padrão HTML sem removê-lo. Devemos garantir que todos os links e formulários funcionem mesmo sem JavaScript, para acessibilidade e robustez:

  - Isso significa sempre ter `href` nos links (mesmo que repitam o hx-get), e um destino de ação normal nos forms (action URL).
  - A aplicação do backend deve ser capaz de servir páginas inteiras para esses endpoints de detalhe, busca etc., para que se um usuário recarregar manualmente ou navegar diretamente, ele obtenha a página completa.
  - Com isso, obtemos um site funcional sem JS, e _melhorado_ com HTMX quando disponível, o que é uma boa prática (Progressive Enhancement).

- **Atualização de Partes Múltiplas da Página:** Em algumas interações, pode ser útil atualizar mais de um alvo ou outros elementos fora do alvo principal. O HTMX fornece recursos como `hx-swap-oob` (out-of-band) para que a resposta do servidor contenha fragmentos dirigidos a outros containers. Por exemplo, se ao criar um novo documento via form queremos tanto limpar o form quanto adicionar o item na lista e mostrar uma mensagem, podemos embutir na resposta HTML segmentos marcados com `hx-swap-oob="true"` para outros IDs. Isso nos permite orquestrar mudanças múltiplas com uma só resposta. No projeto inicial, podemos não precisar disso, mas a possibilidade existe para futuras interações mais complexas.

- **Exemplo de Fluxo HTMX:**
  - O usuário clica no título de um documento na lista (um `<a>` com hx-get configurado).
  - O HTMX intercepta o click, faz uma requisição AJAX para o backend (`GET /documentos/123`).
  - O backend retorna o HTML do detalhe (por exemplo, um `<div>` com título, conteúdo, etc.).
  - O HTMX recebe e substitui o conteúdo do `<div id="conteudo-detalhe">` com esse novo HTML, de acordo com hx-target.
  - O URL do navegador pode ser atualizado via `hx-push-url="true"` no link, o que faz com que essa navegação seja registrada no histórico (permitindo usar botão voltar e compartilhamento de link diretamente para o documento).
  - Todo esse ciclo acontece sem recarregar a página principal, dando a sensação de aplicação dinâmica.

A integração com HTMX é fundamental para o Arca, pois ela permite alta responsividade e simplicidade do frontend. Não precisamos escrever código JavaScript manual para atualizar a interface em resposta a ações – definimos a intenção via atributos e deixamos o HTMX e o servidor cuidarem do resto. Isso alinha com o princípio do projeto de manter simplicidade e trazer reatividade de forma elegante.

### Organização Modular dos Componentes

Para facilitar a manutenção, os componentes FastHTML devem ser organizados de forma modular, seguindo a estrutura de diretórios já indicada:

- No diretório `arca/ui/components/`, definimos um módulo Python por componente ou por grupo de componentes relacionados. Por exemplo, `list_view.py` pode conter a implementação de `ListaDocumentos` e `ItemLista`. Já `detail_view.py` pode conter `DetalheDocumento` e possivelmente componentes auxiliares como `CampoMeta` (um componente pequeno para exibir um campo de metadado formatado). Essa separação pode ser temática (por página ou por tipo de elemento).

- Podemos ter um arquivo central (por exemplo, `arca/ui/pages.py`) que combina componentes para formar páginas completas retornáveis nas rotas. Por exemplo, uma função `pagina_inicial(docs)` que internamente usa `ListaDocumentos(docs)` e insere em um layout básico, retornando um elemento pronto. Esse módulo _pages_ atua quase como um controlador de apresentação, orquestrando componentes para montar as telas.

- Separar componentes em arquivos ajuda um eventual desenvolvedor a localizar onde modificar caso queira alterar apenas a listagem, sem tocar no restante da UI. Também ajuda na colaboração, permitindo trabalhar em paralelo em componentes distintos sem conflitos de merge.

- **Estilos e CSS:** O estilo visual dos componentes (cores, fontes, espaçamento) pode ser definido em arquivos CSS na pasta `ui/static`. Podemos adotar classes CSS nas nossas tags para aplicar estilos. Por exemplo, no componente `DetalheDocumento` podemos envolver o conteúdo em `<div class="detalhe-doc">` e então definir no CSS como esse bloco aparece. A modularidade sugere usar classes com prefixos ou nomes claros por componente, para evitar conflito de estilos e facilitar manutenção (ex: `.lista-documentos li { ... }` ou `.detalhe-doc h1 { ... }`). Se quisermos, podemos usar frameworks CSS ou utilitários (como Tailwind CSS) para acelerar o design, mas isso é secundário ao plano técnico – podemos manter CSS manual simples inicialmente.

- **Scripts adicionais:** Como regra, estamos evitando JS customizado. Porém, se houver necessidade (um caso específico que HTMX não cubra, ou integração de terceiros), podemos ter arquivos JS em `ui/static` também. Eles seriam incluídos no layout geral. Por exemplo, se quisermos integrar um destaque de sintaxe para trechos de código no Markdown, podemos incluir um script de highlight.js. Mas isso são detalhes de implementação que podem ser adicionados conforme demanda.

Em resumo, a UI deve ser implementada de forma limpa, com componentes coesos e reutilizáveis. Isso não só facilita o trabalho de implementação, mas também deixa caminho aberto para ampliações (adicionar um novo tipo de componente, uma nova página, alterar layout geral) sem impacto global, pois cada peça está relativamente isolada.

### Fluxo de Atualização da UI

O fluxo de atualização da interface do usuário no Arca busca refletir instantaneamente (ou no menor tempo possível) as mudanças de conteúdo, seja oriundas da interação do próprio usuário ou de alterações externas nos arquivos. Vamos considerar os cenários:

- **Interações do Usuário (dinâmica interna):** Como detalhado, ações como clicar para ver detalhes ou enviar um formulário de busca acionam requisições HTMX e atualizam partes da página. Esse é o fluxo normal de navegação dinâmica: usuário age -> frontend (HTMX) envia requisição -> backend responde com HTML -> frontend insere o HTML. Para o usuário, a aplicação se comporta de forma similar a uma single-page app tradicional, embora esteja tudo sendo orquestrado pelo servidor. Isso cobre o cenário de navegação e operação normal dentro dos dados existentes.

- **Atualizações Externas (sincronização de conteúdo):** Quando um arquivo é modificado externamente (por exemplo, o usuário edita um Markdown num editor de texto ou alguém faz git pull de novas notas), o watcher atualiza o banco. **Como a UI fica sabendo?**

  - Por padrão, a UI do Arca não "sabe" automaticamente – ela descobrirá quando o usuário realizar alguma ação que cause uma requisição ou se implementarmos algum mecanismo de notificação.
  - **Atualização Manual:** A forma mais simples é prover ao usuário um meio de atualizar a visualização manualmente. Por exemplo, podemos ter um botão "Atualizar" ou usar o próprio refresh do navegador para recarregar a lista. Se o usuário suspeita de mudanças, ele clica e a lista (ou página atual) é recarregada via HTMX ou full reload, trazendo os novos dados. Isso exige que o usuário tome ação, mas é fácil de implementar e entender.
  - **Atualização Automática Temporizada:** Podemos configurar triggers periódicos com HTMX. Por exemplo, no contêiner de lista de documentos, adicionar `hx-get="/documentos" hx-trigger="every 30s" hx-target="#lista-documentos" hx-swap="innerHTML"`. Isso fará o navegador automaticamente requisitar a lista a cada 30 segundos e atualizar a lista na página, refletindo novos itens ou removendo itens deletados. O intervalo pode ser configurável; 30 segundos é um compromisso para não sobrecarregar o servidor local e ainda assim não deixar mudanças passarem despercebidas por muito tempo.
  - **Indicação Visual de Mudança:** Outra possibilidade é informar o usuário que há conteúdo novo e deixá-lo decidir. Por exemplo, o backend poderia manter um timestamp global de última atualização e expor isso. O frontend poderia periodicamente (ex: cada 1 minuto) fazer uma requisição leve para verificar se o timestamp mudou. Se sim, poderia exibir uma notificação na tela ("Novos conteúdos disponíveis, clique para atualizar"). O usuário clicaria e então faríamos a atualização real. Essa abordagem é gentil com quem está lendo algo, pois não troca o conteúdo sem consentimento, mas informa que algo mudou.
  - **Atualização Push (futuro):** Com WebSockets ou SSE, poderíamos empurrar uma notificação ou até o novo conteúdo para a página assim que o watcher atualizasse algo. Isso não está previsto na implementação inicial por simplicidade, mas é uma direção possível no futuro (por exemplo, integrar o Arca com `fastapi_websocket_rpc` ou usar `uvicorn` websockets).

- **Fluxo de Edição via UI (se implementado no futuro):** Caso permitamos editar conteúdo pela interface:

  - O usuário aciona um comando de edição (por exemplo, um botão "Editar" ao lado de um documento na lista). Isso poderia abrir um formulário com os campos atuais preenchidos (via HTMX, carregando o formulário).
  - O usuário faz alterações e envia (hx-post na rota de atualização).
  - O backend valida e escreve as mudanças no arquivo. O watcher atualizará o DB. O backend poderia, na resposta, já enviar o fragmento atualizado do detalhe ou lista (sabendo que as mudanças serão refletidas, já que acabou de salvar). Provavelmente retornaríamos o novo detalhe para substituir o formulário, ou uma mensagem de sucesso + refrescar a lista.
  - Isso cria um loop completo dentro da interface: criar/editar -> salvar -> visualizar atualizado, sem sair da UI.
  - Precisaremos implementar mecanismos de bloqueio/espera se alguém editar externamente enquanto está sendo editado na UI, mas dado que inicialmente pode ser só um usuário usando, não é complexo.

- **Manutenção de Estado de Navegação:** Graças ao `hx-push-url` e `hx-trigger` adequadamente configurados, o usuário pode usar o botão "voltar" do navegador e ter a interface retornando ao estado anterior (por exemplo, da página de detalhe de volta à lista). Precisamos garantir que definimos `hx-push-url="true"` em interações que mudam o contexto principal (ex: ao clicar em um documento, sim; ao filtrar busca, possivelmente sim também, para permitir compartilhar link de busca). Isso faz com que a URL mude, e se o usuário recarregar aquela URL diretamente, o backend deve servir o conteúdo correspondente (como mencionado nas rotas). Essa integração entre HTMX e histórico é importante para não sacrificar usabilidade.

- **Tratamento de Erros na UI:** Apesar de não ser explicitamente pedido, é parte do fluxo de atualização lidar com erros: se uma requisição falhar (problema no servidor ou rede indisponível), o HTMX por padrão pode inserir a resposta de erro (por exemplo, se recebe um 500 com HTML de erro, ele colocará no target). Seria bom personalizar isso:
  - Podemos interceptar eventos globais do HTMX (há eventos JavaScript `htmx:onError` etc. que podemos vincular) para exibir uma mensagem de erro amigável ou um toast dizendo "Não foi possível carregar, tente novamente".
  - Também, podemos garantir que o backend retorna mensagens de erro claras no HTML ou JSON, para facilitar debugging.
  - Na UX, preferimos que erros não travem a interface: se um detalhe não carregou, o usuário ainda pode usar a lista e tentar de novo.

Em resumo, o fluxo de atualização da UI do Arca é centrado no modelo reativo requisitar/responder: o servidor tem sempre a verdade atualizada, e o cliente obtém conforme demanda. Com algumas melhorias (gatilhos periódicos ou notificações visuais), podemos fazer a interface acompanhar as mudanças externas sem intervenção manual. Tudo isso mantendo a simplicidade – sem cliente pesado, sem gerenciamento de estado complexo no front, apenas HTML enviado conforme preciso.

## 8. Sincronização e Watchers

### Como Mudanças em Arquivos São Detectadas

A sincronização automática do Arca baseia-se em "watchers", que são mecanismos que vigiam alterações no sistema de arquivos. A implementação típica utiliza a biblioteca **Watchdog** (ou alternativa semelhante, como `watchfiles` ou `watchgod`) para monitorar o diretório de conteúdo. O funcionamento é:

- **Inicialização do Watcher:** Na inicialização do sistema, configura-se um observador (observer) no diretório raiz de conteúdo, incluindo todos subdiretórios (monitoramento recursivo). Especificamos quais eventos de arquivo monitorar: criação de arquivos, modificação de arquivos e deleção de arquivos são os principais. Renomeações normalmente geram eventos de deleção+criação, e também podem ser observadas se necessário.

- **Thread Separada:** O watcher roda em um thread separado (ou processo, dependendo da biblioteca, mas geralmente thread para simplicidade). Isso permite que o loop principal do FastAPI não seja bloqueado ao aguardar eventos de arquivo. O observer da Watchdog, por exemplo, tem seu próprio loop que vigia os FS events.

- **Eventos:** Quando algo acontece no file system, o watcher emite eventos. Cada evento contém pelo menos o caminho do arquivo afetado e o tipo de evento (created, modified, deleted, moved). Implementamos um _handler_ de eventos no Arca (por exemplo, uma classe herdando de `watchdog.FileSystemEventHandler`) e registramos no observer.

- **Tratamento de Eventos:** O handler de evento define as ações:

  - **Filtro de Arquivos:** Primeiro, filtramos eventos irrelevantes. Ignoramos arquivos temporários (~, .swp de editores, etc.) e possivelmente arquivos que não sejam `.md` ou `.yaml` (se houver outros na pasta).
  - **Debounce e Agrupamento:** Alguns editores ao salvar podem disparar múltiplos eventos (por exemplo, escrever um arquivo novo, apagar o antigo, renomear). Para evitar duplicidade de processamento, podemos implementar um pequeno atraso ou agrupar eventos em curto intervalo. Uma técnica comum é: ao receber um evento, agendar para processar após X milissegundos, e se outro evento do mesmo arquivo chegar nesse intervalo, cancela-se o primeiro e agenda de novo. Assim, depois de, digamos, 100ms sem novos eventos para aquele caminho, processa-se efetivamente uma vez. Isso evita também sobrecarga quando muitos arquivos mudam quase simultaneamente (ex: um git pull).
  - **Log (opcional):** Em modo debug, podemos logar eventos detectados: "Arquivo X criado", "Arquivo Y modificado", etc., para auditoria.

- **Acionamento de Rotinas de Atualização:** Depois de decidir que um evento deve ser processado (pós-filtro e pós-debounce), o handler vai chamar as rotinas adequadas do núcleo do Arca:

  - **No caso de criação ou modificação de arquivo:** Invocamos a função de processamento (parse + validação + upsert no DB) para aquele arquivo. Provavelmente temos uma função `process_file(path)` no módulo `core/parser.py` ou similar, que encapsula essa lógica. Essa função abrirá o arquivo, lerá seu conteúdo (Markdown e/ou YAML), extrairá e validará metadados, e em seguida chamará o módulo `db` para inserir/atualizar o registro. Lidar com erros aqui: se houver erro de leitura ou de parse, registrar e talvez pular o arquivo.
  - **No caso de deleção de arquivo:** Chamamos a rotina de remoção de registro, algo como `remove_file(path)` que instruirá o módulo `db` a apagar o registro correspondente e limpar relacionamentos.
  - **Renomeação de arquivo:** Se capturarmos rename como evento separado, precisamos tratar como uma deleção do antigo caminho e criação do novo. Isso significa possivelmente fazer duas operações: remover o registro antigo e inserir o novo (lendo o arquivo no novo caminho, que é similar a criar).

- **Resiliência do Watcher:** O watcher deve idealmente lidar com situações como:

  - Grande número de eventos em sequência (como ao mudar de branch no Git ou ao copiar uma pasta inteira dentro do conteúdo). Nesses casos, o CPU pode subir mas o sistema deve processar todos, talvez enfileirando se necessário.
  - Erros de acesso a disco (se um arquivo for removido antes de conseguirmos ler, ou permissão negada). Tais erros devem ser capturados para não quebrar o loop do watcher – apenas logados.
  - Pausas ou retomadas: se o usuário pausar o Arca ou se o watcher falhar e reiniciar, o sistema deve poder re-escanear (talvez fornecer um comando manual para re-scan se necessário).

- **Considerações de Plataforma:** Watchdog usa APIs diferentes em cada OS (inotify no Linux, FSEvents no macOS, ReadDirectoryChangesW no Windows). Em geral, ele abstrai isso. Precisamos apenas indicar o diretório correto e garantir que, se a pasta de conteúdo for muito grande, o OS suporte (inotify tem limites de watch count que podem precisar de aumento se observar milhares de arquivos – mas raramente atinge esse ponto em nossos casos típicos).

Em termos de implementação, esse componente de watchers pode ser configurado no início do servidor (talvez dentro do CLI `serve`, antes de rodar Uvicorn, ou usando `@app.on_event("startup")` no FastAPI para iniciar a thread do watcher). Deve também ser adequadamente finalizado no shutdown (observer.stop, etc.) para encerrar threads limpos.

### Como o Banco é Atualizado Dinamicamente

Uma vez detectada a mudança e acionado o processamento, a sincronização concretiza-se na atualização dinâmica do banco de dados, conforme já esboçado, mas com alguns detalhes adicionais:

- **Atualização Atômica:** Cada evento de modificação/adição resulta em uma transação de banco de dados isolada. Por exemplo, se o arquivo `notas/ideias.md` mudou, o sistema parseia o novo conteúdo e então executa uma transação: inicia a transação SQLite, faz **UPDATE** no registro daquele documento com os novos dados (ou **INSERT** se for novo), e commita. Isso garante que qualquer leitura simultânea do banco veja ou o estado antigo completo ou o novo completo, mas não algo pela metade. O SQLite por padrão já fornece atomicidade em cada comando, mas se quisermos garantir várias escritas consistentes (ex: atualizar documento e suas tags em outra tabela), usamos transação explícita para englobar múltiplas queries.

- **Serialização de Eventos:** Como mencionado, para evitar problemas de concorrência no DB, podemos serializar o processamento de eventos. Uma maneira simples: todos os eventos são colocados numa fila interna e um único thread (pode ser o próprio thread do watcher) retira um por um e processa. Assim, nunca dois eventos serão aplicados simultaneamente ao banco. Isso simplifica a lógica (não precisamos de locks manuais no banco além do que o SQLite faz). A leve latência adicionada (fila) é irrelevante, pois mesmo uma sequência de 20 eventos será processada rapidamente.

- **Sincronismo com Backend:** Se uma requisição chegar exatamente no momento de uma atualização, dependendo de como gerenciamos as conexões:

  - Se usamos uma única conexão no thread principal e o watcher tenta usar a mesma conexão em outro thread, isso viola a regra `SQLite objects created in a thread can only be used in that same thread`. Para contornar:
    - Poderíamos abrir uma **nova conexão** para o thread do watcher (com `check_same_thread=False` e travas adequadas). Assim, o watcher faz suas transações de escrita em outra conexão. O SQLite vai gerenciar a exclusão mútua com locks no arquivo do DB.
    - As conexões diferentes precisam de commit para que a outra veja os dados: ou seja, assim que o watcher commitar, as próximas consultas do backend (em outra conexão) verão os dados atualizados.
    - Essa abordagem multi-conexão é viável. Alternativamente, poderíamos enfileirar eventos e usar o _loop_ do FastAPI (thread principal) para aplicar (ex: via `asyncio.call_soon_threadsafe` se fosse async, ou simples poll em threads). Mas isso complica; mais fácil permitir conexão paralela.
  - Em resumo, a atualização dinâmica envolve compromisso entre isolamento e complexidade. O modelo sugerido: **thread do watcher com própria conexão** para escrita, e conexão(s) de leitura para backend, isolando bem.

- **Reconstrução Total Opcional:** Embora a sincronização incremental seja o padrão, convém manter a habilidade de reconstruir todo o banco a qualquer momento (por exemplo, se suspeitamos que houve alguma inconsistência ou bug). Isso pode ser acionado via CLI (`arca validate` ou `arca sync --rebuild`) ou via um endpoint admin. Nessa situação, o procedimento seria: pausar watchers, dropar as tabelas ou apagar o arquivo SQLite, reprocessar todos os arquivos, e retomar watchers. Isso garante uma forma de recuperação completa caso necessário, mas normalmente não será usado rotineiramente.

- **Exclusão e Consistência:** Ao remover um arquivo e consequentemente deletar seu registro no banco, devemos considerar se há referências a ele. No Arca base, provavelmente não há links fortes (a não ser que tenhamos um conceito de "um documento linka para outro", mas isso seria texto). Se houvesse, poderíamos manter referências quebradas ou também remover/atualizar outros itens. Por exemplo, se tínhamos um projeto listando várias notas e uma nota é deletada, poderíamos querer atualizar um campo de contagem ou lista no projeto. Isso entraria na lógica de negócio do watcher ou backend. Por ora, assumimos independência – deletou o arquivo, saiu da lista e ponto.

- **Notificação Pós-Update:** Uma ideia futura seria notificar a UI imediatamente após uma atualização, mas sem websockets não há um canal do servidor para o cliente após um evento. Uma gambiarra possível é usar um endpoint SSE e o watcher fazer requisições HTTP POST para acionar a UI, mas isso é complexo e não necessário inicialmente. Em vez disso, confiamos nos métodos do frontend (periodic checks ou user refresh).

- **Modo Somente-Leitura vs. Modo Editável:** Se o Arca estiver operando só lendo arquivos que são editados externamente, watchers passivos bastam. Se permitirmos edição via API/UI, o próprio Arca vai escrever nos arquivos. Nessa situação, quando o Arca escreve um arquivo, o watcher vai imediatamente capturar a mudança (já que foi uma mudança no FS). Precisamos evitar uma reação em _loop_ (Arca escreve -> watcher vê -> talvez Arca tente re-escrever). Por isso:
  - Podemos implementar uma flag ou contexto quando a mudança vem de dentro: ex., ao salvar um arquivo via backend, podemos temporariamente desligar watchers ou ignorar eventos naquele caminho, pois sabemos o que foi feito e já tratamos a lógica.
  - Ou simplesmente permitir que o watcher processe, mas garantir que nossa escrita já era conforme o esperado e o DB vai ser atualizado com os mesmos dados (um pouco redundante, mas sem efeitos colaterais além de log).
  - Uma otimização: após escrever arquivo via Arca, em vez de esperar o watcher ler o arquivo de volta, poderíamos chamar direto a função de update do DB e talvez suprimir o evento. Isso torna a escrita via UI quase imediata no DB. Mas isso duplica a lógica (um caminho de update via UI e outro via watcher). Para manter uma única fonte de verdade do pipeline, talvez seja melhor deixar o watcher lidar, mesmo que cause um mínimo de latência.
  - Em todo caso, esse detalhe deve ser considerado se/quando implementar escrita interna.

Em resumo, o sistema de watchers e atualizações dinâmicas é o **coração da sincronização do Arca**. Ele garante que o SQLite (e consequentemente a interface) esteja sempre alinhado com os arquivos em disco, sem necessidade de reiniciar ou atualizar manualmente o índice. A implementação requer atenção a concorrência e performance em caso de múltiplos eventos, mas seguindo padrões e usando as ferramentas existentes (Watchdog, transações SQLite), conseguimos um comportamento robusto.

## 9. Versionamento e Controle de Estado

### Delegação de Versionamento (Git, Dropbox, etc.)

O Arca em si não implementa um sistema de versionamento de conteúdo interno; em vez disso, adota o princípio de delegar essa responsabilidade a ferramentas já consolidadas e confiáveis:

- **Git (Controle de Versão):** É recomendado que o diretório de conteúdo do Arca seja colocado sob um sistema de controle de versão Git, especialmente em cenários de uso colaborativo ou onde se deseja histórico detalhado das mudanças. Usando Git, todas as alterações nos arquivos Markdown e YAML ficam registradas: cada _commit_ representa um estado do conteúdo, permitindo reverter a qualquer momento ou comparar diferenças. O Arca não precisa "saber" do Git – ele continuará monitorando arquivos normalmente. Do ponto de vista do Arca, um _git pull_ que modifica arquivos vai simplesmente gerar eventos de modificação que os watchers tratarão. Um _git checkout_ para outra branch pode causar deleções e criações em massa; o Arca processará todos os eventos e refletirá a mudança de branch na interface (por exemplo, trocando o conjunto de documentos visíveis). Ao **não reinventar o controle de versão**, o Arca se mantém simples e compatível com fluxos de trabalho já existentes. Equipes podem usar PRs, merges e outras práticas Git sem conflito com a ferramenta.

- **Serviços de Sincronização (Dropbox, OneDrive, etc.):** De forma semelhante, usuários podem optar por sincronizar a pasta de conteúdo via serviços de nuvem como Dropbox, Google Drive, OneDrive, etc. Isso oferece uma forma fácil de backup e até de colaboração (embora com menos controle que o Git). Se o diretório `content/` estiver dentro de uma pasta Dropbox, por exemplo, qualquer outro dispositivo conectado àquela conta terá os arquivos atualizados, e se um arquivo for editado em um laptop, o desktop onde o Arca está rodando receberá a atualização via Dropbox sync, e o watcher do Arca então a detectará. Muitos desses serviços também mantêm histórico de versões, então servem como um backup do conteúdo. O Arca, nesse caso, fica completamente agnóstico: ele trata as mudanças vindas do Dropbox como qualquer alteração local. Deve-se ter cuidado com possíveis "conflitos de sincronização" (quando dois editores alteram offline o mesmo arquivo, o Dropbox cria duas cópias). Tais conflitos aparecerão para o Arca como arquivos novos ou modificados; a resolução fica a cargo do usuário manualmente.

- **Controle de Estado Efêmero:** Como o banco de dados SQLite é efêmero e local, ele não é versionado nem sincronizado – e não precisa ser. O importante é que os arquivos de conteúdo estejam versionados/sincronizados. Em caso de algum erro ou mudança indevida, o usuário deve reverter os arquivos usando Git ou restaurar da nuvem. Quando o Arca reiniciar ou quando as mudanças forem aplicadas, ele refletirá o estado restaurado. Isso simplifica muito a nossa responsabilidade; não precisamos gerenciar histórico no aplicativo, apenas ler o estado atual.

- **Backup e Recuperação:** A delegação de versionamento implica que a estratégia de backup do conteúdo do Arca é igual à estratégia de backup dos arquivos. Se os arquivos estão no GitHub, por exemplo, eles já estão seguros remotamente. Se estão no Dropbox, idem. Se o usuário optar por não usar nenhum destes, ele deve manualmente fazer cópias/backup da pasta content/ se for algo importante. O Arca poderia, como ferramenta auxiliar, facilitar isso (talvez um comando `arca backup` que zipa a pasta, etc., ou integração leve com Git), mas não é essencial.

- **Integração Leve com Git:** Embora o Arca não gerencie commits diretamente, podemos considerar facilitar a vida do usuário com alguns ganchos:
  - Por exemplo, um comando CLI `arca commit -m "mensagem"` que essencialmente chama `git add -A` na pasta de conteúdo e `git commit -m "mensagem"` e talvez `git push`. Isso seria implementado apenas se for de interesse, mas mostra que podemos integrar de forma leve, sem o Arca ter um sistema de versionamento próprio.
  - Na interface web, se autenticação e segurança não forem um problema (em uso local), poderíamos ter um botão "Salvar Versão" que internamente executa um commit. Mas isso é futuro e possivelmente fora de escopo inicial.

Em resumo, o Arca **se concentra no presente** – ele reflete o estado atual dos arquivos. O passado (histórico de alterações) e o futuro (sincronização multi-dispositivo) são tratados pelas ferramentas de versionamento e backup externas. Essa filosofia mantém o Arca simples e extensível, e aproveita soluções robustas já existentes em vez de reinventar funcionalidades complexas.

### Como os Usuários Gerenciam Histórico e Sincronização

Dado que o Arca não possui interface própria de versionamento, os usuários são orientados a adotar práticas recomendadas para gerenciar o histórico e sincronização do conteúdo:

- **Commits Frequentes (usando Git):** Após realizar um conjunto de edições significativas nos arquivos, é aconselhável que o usuário **faça commit** dessas mudanças em um repositório Git. Isso cria um ponto de restauração no histórico. O usuário pode escrever uma mensagem de commit descrevendo as alterações (ex: "Adiciona seção X na nota Y" ou "Corrige typos e atualiza data de projeto Z"). Esses commits podem ser feitos manualmente via terminal ou usando ferramentas GUI de Git. O Arca não interage com esse processo; ele pode continuar rodando. De fato, o usuário pode optar por pausar o Arca durante grandes merges para evitar processamento incessante, mas mesmo se não pausar, o Arca lidará com os eventos gerados pelo commit (que geralmente apenas altera metadados de arquivos como .git, não o conteúdo – commits não modificam os arquivos, apenas registram).

- **Branches e Fluxo de Trabalho Colaborativo:** Em ambientes com múltiplos colaboradores, é comum o uso de **branches** e **pull requests** no Git para integrar alterações. Cada colaborador poderia editar uma cópia (fork ou branch) do conteúdo, e o mantenedor mescla as alterações. Enquanto isso, talvez apenas uma instância do Arca (por exemplo, rodando num servidor compartilhado ou na máquina do mantenedor) esteja efetivamente ativa. Quando as alterações são mescladas na branch principal e puxadas (git pull) para o local onde o Arca está rodando, ele vai atualizar a interface. Para colaborar em tempo real, várias pessoas poderiam rodar cada uma o Arca com sua cópia do repositório, mas então cada instância mostraria apenas seu estado local até sincronizar via Git com as dos outros.

  - Se dois colaboradores editam o mesmo arquivo simultaneamente, um conflito de merge pode ocorrer no Git. Esse conflito será resolvido fora do Arca (usando ferramentas do Git). Até resolução, o Arca de cada um mostra suas versões próprias. Após resolvido e sincronizado, o Arca refletirá a versão mesclada.
  - Isso mostra que a conciliação de edições simultâneas é deixada para o Git (ou para políticas de colaboração), não tratada automaticamente pelo Arca.

- **Uso de Dropbox/Cloud:** Se o usuário optar por não usar Git e só usar um serviço de nuvem:

  - Ele confia no serviço para manter histórico (por exemplo, Dropbox permite restaurar versões antigas de um arquivo, mas não tem um log tão visível quanto o Git).
  - Para colaborar, se duas pessoas editam offline e depois conectam, pode gerar arquivos duplicados (ex: "versão conflitante"). O Arca não sabe mesclar esses; ele listará ambos os arquivos se estiverem no diretório. Cabe aos usuários unificá-los manualmente.
  - Portanto, esse método é mais indicado para uso pessoal ou colaboração leve onde as pessoas coordenam para não editar o mesmo item ao mesmo tempo.

- **Snapshots e Releases:** Se o conteúdo do Arca for algo como documentação de software, pode haver a necessidade de marcar "releases" do conteúdo (por ex, v1.0 docs, v2.0 docs). Com Git, isso é fácil – basta criar _tags_ ou branches para cada release. O Arca poderia até ter uma função de mudar a branch de conteúdo ativo para visualizar diferentes versões (não previsto, mas possível, ex: um menu dropdown para selecionar branch, e o Arca troca a pasta ou manda um comando git). Sem Git, seria manual (duplicar pasta, etc.).

- **Recuperação de Histórico:** Para obter uma versão anterior de um documento, o usuário usará o Git:

  - Via linha de comando (git log, git checkout commit antigo, etc.) ou
  - Via uma interface (GitHub web, GitKraken, etc.) para ver o histórico e copiar o conteúdo antigo.
  - O Arca não tem tela de "histórico" própria, a menos que implementemos futuramente integrando com `git log`. Isso pode ser pensado como extensão: por exemplo, um plugin que mostra dentro do Arca as diferenças entre a versão atual e anterior usando `git diff`.

- **Sincronização Multi-instâncias:** Se um usuário deseja rodar o Arca em mais de um local (por exemplo, PC de casa e laptop), ele deve sincronizar os arquivos entre eles (via Git ou nuvem). Não há mecanismo no Arca para mesclar ou sincronizar dois bancos de dados ou duas instâncias ativamente; toda sincronização ocorre através dos arquivos. Portanto, a recomendação é:

  - Use Git push/pull regularmente para que ambos ambientes fiquem atualizados.
  - Ou use uma pasta compartilhada em nuvem acessada por ambos.
  - Nunca tente editar simultaneamente nos dois sem sincronizar, ou verá divergências que só resolvem via versionamento externo.

- **Controle do Estado Efêmero:** Como o SQLite é descartável, se o usuário, por exemplo, faz um git checkout para uma versão antiga do conteúdo, o Arca não preserva um estado antigo – ele recalcula. Isso significa que, se quiséssemos manter também o estado da aplicação em sincronia com versões, teríamos que versionar o SQLite ou ter um por branch, o que complica muito. Mantemos a abordagem de recalcular on-the-fly para qualquer estado dos arquivos.

Em suma, **os usuários gerenciam histórico e sincronização fora do Arca**. O papel do Arca é informar (via logs ou possíveis comandos de validação) se algo está inconsistente e refletir a última versão persistida dos arquivos. A boa prática é integrar o uso do Arca com o uso de Git: editar arquivos, testar visualização no Arca localmente, commitar mudanças. Isso dá um ciclo de feedback rápido e seguro.

## 10. Modos de Execução

### CLI e Suas Funcionalidades

O Arca oferece uma **Interface de Linha de Comando (CLI)** que facilita o uso do sistema em diversos cenários (desenvolvimento, administração, automação). Essa CLI é acessível através de um comando, por exemplo `arca`, disponível após instalar o projeto. Principais funcionalidades e comandos previstos:

- **Inicialização/Criação de Projeto (`arca init`):** Este comando criaria a estrutura básica esperada para começar a usar o Arca. Por exemplo, gera um diretório de conteúdo (se não existir) com alguns subdiretórios de exemplo, talvez arquivos Markdown/YAML de exemplo mostrando o formato esperado, e um arquivo de configuração padrão. Também poderia criar um arquivo `.gitignore` adequado (ignorando o DB, etc.) para facilitar versionamento. Isso ajuda novos usuários a começarem rapidamente e com a estrutura correta.

- **Execução do Servidor (`arca serve`):** Inicia o servidor FastAPI com o Arca, incluindo os watchers. Esse comando configura os watchers, carrega dados iniciais e inicia o serviço web (provavelmente rodando um servidor ASGI como Uvicorn internamente). Parâmetros comuns podem incluir:

  - `--host` e `--port` para especificar em qual endereço e porta o servidor deve rodar (por padrão poderia ser `127.0.0.1:8000`).
  - `--reload` para ambiente de desenvolvimento (recarrega automaticamente se o código fonte mudar, semelhante ao uvicorn --reload).
  - `--content-dir` caso queira sobrescrever o caminho da pasta de conteúdo definido em config.
  - Esse comando provavelmente bloqueia o terminal, exibindo logs de requisição e eventos, até ser interrompido (Ctrl+C).

- **Validação de Conteúdo (`arca validate`):** Realiza uma passagem por todos os arquivos de conteúdo e executa a validação de YAML (via Pydantic) e talvez outras checagens, reportando resultados. Essencialmente, é rodar o mecanismo de ingestão sem iniciar o servidor. Pode listar arquivos processados e, em caso de erros, detalhar quais foram encontrados. Isso seria útil para integração contínua (CI) ou para usuários que queiram verificar se está tudo certo sem subir a interface. O exit code do comando pode indicar sucesso (0) ou falha (1 se algum erro de validação ocorrer, por exemplo), permitindo ferramentas de automação capturarem isso.

- **Busca via CLI (`arca search "termo"`):** Permite fazer consultas de texto diretamente no conteúdo via linha de comando. Esse comando poderia aproveitar o índice (consultando o SQLite) ou simplesmente fazer grep recursivo nos arquivos. Retornaria uma lista de ocorrências, por exemplo:

  ```
  nota1.md: "… contém o termo buscado ..."
  projeto2.md: "… contém o termo buscado ..."
  ```

  Talvez mostrando o contexto ou só contando resultados. Isso é útil para quem está no terminal e quer achar algo rápido sem abrir a interface web.

- **Exportação (`arca export --format FORMATO`):** Gera uma exportação de todo o conteúdo para outro formato. Possíveis formatos:

  - `html`: gera arquivos HTML estáticos para cada documento (usando talvez os mesmos componentes do FastHTML, mas rendendo offline).
  - `json`: produz um JSON consolidado com todos os documentos e metadados (poderia ser usado para importar em outra ferramenta).
  - `pdf` (menos provável inicialmente, mas poderia juntar conteúdos e gerar um PDF).
  - Esse comando facilita tirar "snapshots" do conhecimento em formatos portáteis.

- **Outros utilitários:** Podemos conceber outros comandos auxiliares:

  - `arca list`: lista todos os documentos conhecidos atualmente (pode ser obtido do DB ou lista de arquivos).
  - `arca show <id>`: exibe o conteúdo de um documento específico no terminal, possivelmente formatado em Markdown cru ou texto.
  - `arca edit <id>`: abre o editor de texto padrão no arquivo (usando `xdg-open` no Linux ou similar, ou variável EDITOR).
  - Esses comandos não são críticos mas podem tornar o Arca mais conveniente para uso via terminal.

- **Sistema de Plugins da CLI:** Caso a arquitetura de plugins seja implementada (ver seção 11), a CLI pode carregar comandos adicionais registrados por plugins. Por exemplo, um plugin de publicação externa pode adicionar `arca publish` para mandar conteúdo a um site. A CLI deve ser desenvolvida de modo extensível para possibilitar isso (se usarmos Typer, ele suporta adicionar comandos dinamicamente de outros módulos).

**Implementação da CLI:** Utilizaremos provavelmente a biblioteca **Typer** (do mesmo criador do FastAPI, otimizada para CLI com Python) ou **Click** para implementar a CLI. Essas bibliotecas facilitam o mapeamento de funções para subcomandos e o parsing de argumentos. A CLI integrará com os módulos do Arca:

- Por exemplo, `arca validate` chamará internamente funções do módulo `core.parser` para iterar e validar arquivos, reutilizando o código que watchers usam.
- `arca serve` chamará possivelmente algo como `uvicorn.run(app, host=..., port=...)` programaticamente ou usará `FastAPI()` diretamente com `app.run()` se o FastHTML oferecer essa facilidade.
- A CLI deve ler configurações (por ex, se o usuário configurou o caminho de conteúdo ou porta no `config.py` ou em um `config.yaml`), e permitir sobrescrever via flags.

### Modo Servidor e API

O modo servidor refere-se à execução contínua do Arca como um serviço web disponível para atender requisições. Este é o modo acionado pelo comando `serve`, e pode ter algumas variantes ou opções de operação:

- **Inicialização do Servidor:** Ao rodar `arca serve`, o aplicativo realiza, em ordem:

  1. Carrega configurações (por exemplo, lê `config.py` ou variáveis de ambiente para definir host, port, debug, etc.).
  2. Inicia o monitoramento de arquivos (watchers) para o diretório de conteúdo configurado.
  3. Faz a indexação inicial de conteúdo no SQLite (equivalente a rodar `validate` + inserir no DB).
  4. Instancia o aplicativo FastAPI e inclui as rotas definidas (possivelmente registrando routers).
  5. Atacha a interface FastHTML (se necessário – possivelmente as rotas HTML já usam FastHTML internamente).
  6. Usa Uvicorn (ou Hypercorn, etc.) para iniciar o loop de eventos ASGI, servindo o app no host/porta definidos.

  Durante essa sequência, se algo der errado (ex: pasta de conteúdo não encontrada, porta já em uso), o servidor loga o erro e aborta com mensagem apropriada.

- **Execução Contínua:** Uma vez rodando, o modo servidor:

  - Aceita conexões HTTP e responde conforme implementado.
  - Os watchers continuam ativos em segundo plano.
  - Logs de acesso (requests) e logs de eventos de arquivo podem aparecer no console.
  - O servidor pode rodar indefinidamente até ser manualmente parado.

- **Modo Daemon/Serviço:** Em produção ou uso prolongado, o Arca pode ser configurado para rodar como um serviço de sistema (ex: serviço systemd no Linux) ou no Windows Task Scheduler. Isso não é intrínseco ao Arca, mas há considerações:
  - Precisamos garantir que não há interações de input durante `serve` (somente logs). Já coberto.
  - Opcional: `arca serve` poderia aceitar uma opção `--daemonize` para automaticamente se colocar em background, mas isso é supérfluo em Python normalmente (deixa-se para ferramentas externas gerenciarem).
- **Conectividade Externa:** Por padrão, provavelmente limitaremos o servidor ao host local (127.0.0.1) por segurança, assumindo uso local. O usuário pode especificar `--host 0.0.0.0` se quiser disponibilizar em rede local/internet (nesse caso, deve-se pensar em autenticação, porque qualquer um poderia acessar). Sem um sistema de autenticação, expor publicamente não é aconselhado. O manual do Arca deve deixar isso claro.

- **Documentação da API:** FastAPI gera automaticamente documentação OpenAPI/Swagger para endpoints, especialmente os JSON. Podemos disponibilizar isso em `/docs` ou `/redoc` se não o desabilitarmos. Isso facilita um desenvolvedor ver quais endpoints existem e testar chamadas API. Podemos protegê-lo ou deixá-lo aberto, mas em cenário local não há problema.

- **Modo "Headless" (somente API):** Podemos considerar suportar um modo onde apenas a API JSON funciona e não a interface HTML. Por exemplo, `arca serve --api-only` não carregaria os templates FastHTML, servindo o Arca apenas como backend de dados. Isso seria útil se alguém quisesse usar um frontend custom (mobile app, interface diferente) ou integrar o Arca a outra plataforma. Implementacionalmente, isso significa não incluir as rotas de UI (ou talvez nem carregar FastHTML) – o `routes.py` poderia separar routers `ui_router` e `api_router`, e incluir só o apropriado. Esse não é um requisito essencial, mas mostra a flexibilidade.

- **CLI vs. Servidor:** Enquanto o servidor roda, idealmente o CLI do Arca está ocupando o terminal. Se o usuário quisesse executar outro comando CLI (tipo `arca search`), teria que abrir outro terminal ou parar o servidor. Uma futura possibilidade seria permitir enviar comandos ao servidor rodando (via um endpoint admin ou via sinal de SO), mas isso complica. Um design mais simples: se funções CLI precisarem rodar durante servidor ativo, elas poderiam atuar via chamadas HTTP (por exemplo, `arca search` poderia fazer uma chamada para `http://localhost:8000/api/busca?q=...` em vez de acessar diretamente arquivos). Isso integraria CLI e servidor. Por ora, mantemos separado; a CLI opera offline ou antes de subir servidor, e quando servidor está rodando, usa-se a interface web ou API para interagir.

- **Escalabilidade do Servidor:** Para uso local e modesto, um único processo uvicorn (talvez single worker, single thread, ou usando threads para concurrency do FastAPI) é suficiente. Se alguém quisesse colocar Arca em produção com múltiplos workers, teria que ter cuidado: múltiplos processos watchers poderiam duplicar trabalho ou conflitar, e cada um teria seu SQLite. É melhor evitar rodar mais de uma instância do Arca apontando para o mesmo conteúdo simultaneamente. Se desempenho for problema, seria melhor migrar para um DB central robusto e um único watcher central – mas isso é cenário avançado.

Em resumo, o **modo servidor** é a face principal do Arca em operação contínua, servindo tanto a UI interativa quanto endpoints API para outros usos. Ele foi projetado para ser simples de iniciar via CLI e rodar confiavelmente em segundo plano, integrando watchers e backend sem intervenção adicional.

## 11. Extensibilidade e Futuro

### Possibilidades de Extensões e Plugins

A arquitetura modular do Arca foi pensada para permitir acréscimo de funcionalidades sem necessidade de alterar o core, através de extensões ou plugins. Algumas direções para extensibilidade incluem:

- **Suporte a Novos Formatos de Conteúdo:** Atualmente o Arca foca em Markdown + YAML. Um plugin poderia adicionar suporte a outros formatos:

  - Por exemplo, **CSV/Planilhas**: importar um CSV e apresentá-lo como tabela na UI, ou converter em objetos no SQLite.
  - **Asciidoc ou reStructuredText**: se algum usuário prefere outro formato de marcação em vez de Markdown, um plugin poderia integrar um parser adequado e registrar watchers para arquivos `.adoc` ou `.rst`.
  - **Imagens e Anexos:** Embora o Arca possa já servir imagens referenciadas, um plugin poderia catalogar imagens (gerar galeria, thumbnais) ou suportar upload via UI (transformando UI em um mini-gestor de mídia).

- **Enriquecimento de Conteúdo:** Plugins de processamento poderiam atuar sobre os dados:

  - Exemplo: um plugin de _referências cruzadas_ que analisa os Markdown em busca de padrões (como `[[nome do documento]]`) e automaticamente gera links entre documentos no HTML final.
  - Ou um plugin de _resumo automático_, usando um algoritmo ou mesmo uma API de ML para gerar um resumo de cada documento e salvar num campo extra (que a UI poderia exibir como tooltip).
  - Outro plugin poderia gerar um gráfico (usando Graphviz, por ex.) mostrando relacionamento entre documentos baseado em links ou tags, atualizando a cada mudança.

- **Extensões de Interface/Novas Páginas:** Quer adicionar uma funcionalidade extra na interface sem alterar o core? Um plugin poderia introduzir novas rotas e componentes:

  - Por exemplo, um módulo "Estatísticas" que calcula número de documentos por categoria, taxa de edição, etc., e fornece uma página `/stats` com gráficos.
  - Ou um plugin "Busca Avançada" que adiciona uma página com filtros combináveis (por data, tag) e uma interface refinada para busca, além do básico que já temos.
  - Esses plugins poderiam registrar novos routers no FastAPI e usar FastHTML para seus templates, integrando-se ao menu de navegação possivelmente (talvez via um hook para inserir um link no menu).

- **Autenticação e Controle de Acesso:** De fábrica o Arca não tem usuários ou autenticação, mas um plugin pode adicionar:

  - Sistema de login (possivelmente integrando OAuth2 do FastAPI ou outras libs), com formulário e gestão de sessão.
  - Controle de acesso por documento ou categoria (ex: só usuários autorizados veem certos conteúdos). Isso exigiria marcar arquivos com meta de permissões e o plugin implementaria dependencies nas rotas para checar usuário.
  - Essa funcionalidade seria crucial se alguém quisesse expor o Arca publicamente mas com restrição a um grupo.

- **Integração com Serviços Externos:** Plugins podem conectar o Arca a outros sistemas:

  - Por exemplo, um plugin para **Publicação em Blog**: permite selecionar alguns documentos e exportá-los/postá-los em uma plataforma (WordPress, Medium) via API.
  - Plugin **Notificações**: integra com Telegram/Email para mandar alerta toda vez que um documento for atualizado (usando os hooks de watcher para acionar envio).
  - **Search Engine**: integrar com ElasticSearch ou Algolia para busca full-text mais robusta em vez do SQLite FTS, se necessário. O plugin manteria índice sincronizado e redirecionaria consultas de busca.

- **Persistência Alternativa:** Um plugin (ou configuração avançada) poderia trocar o SQLite por outro banco, se escalabilidade ou multi-instância for necessária:

  - Por exemplo, usar PostgreSQL como banco central. O plugin ou módulo substitutivo implementaria o `db.py` com SQLAlchemy pointing to Postgres. Watchers e backend usariam esse sem notar diferença (exceto config de string de conexão).
  - Isso permitiria rodar Arca em ambiente servidor multi-usuário mais pesado, ou integrar com uma base já existente.

- **CLI e Automação:** Plugins também poderiam estender a CLI:
  - Um plugin de DevOps talvez adicione `arca deploy` para mandar uma exportação para um servidor, ou `arca sync-notion` para sincronizar os docs com Notion ou outra ferramenta.
  - Esses comandos extras seriam registrados via algum mecanismo de discovery (por exemplo, usando setuptools entry_points ou uma lista de plugins no config do Arca).

Para viabilizar essas extensões, o Arca deve definir **pontos de extensão claros (hooks)** e facilitar o registro de plugins:

- Podemos ter um arquivo de configuração listando plugins (ex: `plugins: ["arca_git_integration", "arca_stats"]`). O Arca ao iniciar tenta importar cada módulo plugin e chamar uma função de inicialização pré-definida (por convenção, ex: `def setup(arca_app, config):`). Esse método então registra tudo necessário (rotas, hooks, etc.).
- Hooks específicos a considerar:
  - **Após carregar um arquivo (post-parse):** plugins podem inspecionar ou modificar os dados. Ex: plugin de link resolver poderia nessa fase adicionar hyperlinks no texto antes de salvar no DB.
  - **Após atualizar DB (post-save):** plugin de notificação poderia ser chamado aqui para agir sobre o item novo.
  - **Pré-resposta do backend:** permitir que um plugin altere ou complemente a resposta. Ex: plugin de analytics poderia injetar um script de tracking no HTML sempre que uma página é montada.
  - **Eventos de UI:** embora UI seja do lado cliente, podemos pensar em plugins para UI (como temas visuais). Isso talvez seja feito via configuração de templates ou CSS alternativo.
- **Isolamento:** Garantir que se um plugin falhar, não derrube o sistema principal. Por exemplo, envolver chamadas de hook em try/except e logar erro do plugin, mas continuar a operação principal.

### Hooks para Customizações

Alguns hooks e mecanismos de customização específicos que podemos implementar ou deixar prontos:

- **Hook de Parser (pré/pós parse):** Antes de inserir no banco, após obter o objeto Pydantic válido, podemos ter algo como `core.hooks.post_parse(documento_obj)` que itera sobre funções registradas pelos plugins. Essas funções recebem o objeto documento (ou seus componentes YAML/Markdown) e podem, por exemplo, acrescentar campos derivados ou normalizar dados. Também um `pre_save` similar.

- **Hook pós-save (Watchers):** Depois de uma inserção/atualização no SQLite ocorrer, chamar `core.hooks.after_db_update(id_do_doc)`. Plugins podem então fazer operações externas (atualizar um índice externo, enviar log, etc.). Talvez passar o objeto documento completo também para evitar outra query.

- **Extensão de Modelos:** Permitir que plugins extendam o schema. Por exemplo, um plugin de classificação poderia querer adicionar um campo `prioridade` a todos os documentos. Como Pydantic não permite facilmente monkey patch, poderíamos:

  - Ou ter meta campos flexíveis tipo um JSONField para extras,
  - Ou definir um sistema de "atributos extras" genérico nos YAML e deixar plugin interpretar.
  - Uma abordagem é plugins definirem modelos adicionais e o core valida base + plugin separadamente. Isso pode ficar complicado; possivelmente mantemos cada plugin responsável por validar e armazenar seus campos (talvez em tabelas próprias ou no campo JSON se usarmos).

- **Injeção de Rotas e UI:** Fornecer APIs para plugins adicionarem rotas:

  - O plugin, ao ser carregado, poderia chamar algo como `app.include_router(meu_router)`.
  - Para UI, se quiserem adicionar link no menu, precisamos talvez ter um template base que itere numa lista de itens de menu configuráveis. Plugins poderiam adicionar item a essa lista via um hook ou config injection.
  - Alternativamente, poderíamos ter o menu construído dinamicamente verificando as rotas registradas ou um registro central de "páginas do app".

- **Eventos CLI:** Permitir plugins adicionarem comandos CLI via Typer:

  - Se usamos Typer, podemos instanciar Typer app no core e fornecer função para plugin fazer `app.add_typer(plugin_typer, name="meucomando")`.
  - Ou plugins definem entry_points `arca.commands` que o CLI loader descobre e inclui.

- **Temas de Interface:** Um tipo específico de plugin poderia ser um _tema_ de UI: pacote que inclui templates/CSS diferentes. Se quisermos suportar isso:
  - Podemos projetar as classes CSS de forma sistemática para permitir troca de estilo via arquivo.
  - Um tema plugin talvez substitua o CSS padrão e altere alguns componentes (ex: mudar logos, títulos).
  - Isso não é prioridade, mas é um gancho de customização visual que alguns usuários apreciariam.

Todos esses hooks e extensões servem para que o Arca possa se adaptar a usos que o criador original não previu. Especialmente em contexto de um LLM implementando, fornecer esses pontos de extensão significa que no futuro, sem refazer o core, podemos pedir a um LLM ou desenvolvedor para "adicione funcionalidade X como plugin", e ele terá maneiras ordenadas de fazê-lo.

### Futuro do Projeto (Perspectivas)

Por fim, olhando adiante, enumeramos algumas evoluções futuras e ideias de longo prazo para o Arca, que vão além do escopo imediato mas mostram a direção possível:

- **Edição Web Completa:** Como mencionado, implementar uma interface de edição no próprio Arca. Isso inclui um editor de Markdown (pode ser um simples `<textarea>` ou algo mais rico como editor WYSIWYG/MD em tempo real), possibilidade de editar metadados YAML através de um formulário amigável, e salvar direto via backend. Com isso, o Arca passaria de um sistema _read-mostly_ para um pequeno CMS de arquivos. Seria importante conciliar com o watchers/git: talvez o usuário escolhe editar via web ou via arquivos, e tudo se mantém sincronizado. Essa funcionalidade aumentaria o alcance do Arca para usuários não técnicos.

- **Colaboração em Tempo Real:** Expandindo a edição web, permitir que múltiplos usuários editem simultaneamente e vejam mudanças em tempo real (estilo Google Docs ou Etherpad). Isso exigiria uma arquitetura de sincronização de estado de documento no backend (operational transform ou CRDT) e no frontend, mais uso intensivo de WebSockets. Poderia ser lançado como um modo especial (talvez restrito a certos documentos ou sessão de edição) para não complicar o caso simples. É complexo, mas possível.

- **Modo Offline e Aplicativo Desktop:** Embalar o Arca em uma aplicação desktop (usando Electron ou Tauri, por exemplo) para usuários menos técnicos, ou uma versão mobile. Essencialmente seria criar um browser dedicado que roda o Arca embutido localmente, com UI adaptada. O Arca já sendo local-first facilita isso. Um PWA (Progressive Web App) também poderia permitir usar no browser mesmo offline, armazenando dados localmente e sincronizando depois.

- **Integração com Assistentes de IA:** Dado que o Arca estrutura conhecimento textual, no futuro poderíamos ver integrações interessantes com IA:

  - Um plugin de chatbot onde você faz perguntas sobre seu conhecimento e ele responde (usando um LLM e os documentos como contexto).
  - Sugestão de link: ao escrever um documento, um modelo pode sugerir links para outros documentos relacionados automaticamente.
  - Classificação automática ou geração de sumário/tags com IA.

  Essas coisas não estavam no design original mas combinam bem com a ideia de gerenciamento de conhecimento.

- **Escalabilidade e Multi-usuário Corporativo:** Se o Arca for adotado em ambientes maiores, poderíamos evoluir para suportar:

  - Um banco de dados robusto (Postgres) compartilhado, permitindo múltiplos servidores (por redundância ou balanceamento).
  - Controle de acesso refinado (times, permissões por pasta).
  - Integração com LDAP/SSO para autenticar usuários corporativos.
  - Interface refinada com busca global instantânea e organização de milhares de documentos.
  - Essencialmente, caminhar em direção a um _wiki_ ou _CMS_ corporativo, mas mantendo a filosofia de arquivos markdown por baixo (talvez sincronizando com um repositório Git central).

- **Internacionalização (i18n):** Tornar a interface do Arca traduzível para outros idiomas, e também suportar conteúdo multi-idioma. Por exemplo, dois arquivos representando a mesma página em PT e EN, com o sistema fornecendo switch de idioma.

- **Publicação Externa e Sites Estáticos:** O Arca pode servir como um sistema de gerenciamento de conteúdo para sites. Já que tem tudo em Markdown, semelhante a static site generators (Hugo, Jekyll), poderíamos adicionar recurso de exportar ou até servir um site público. Por exemplo, um modo "publicar" que gera um conjunto de páginas HTML estáticas (talvez sem a parte HTMX, mas com navegação tradicional) para hospedar em qualquer lugar. Ou integração com Github Pages/Netlify para publicar automaticamente as mudanças do repositório.

- **Aprimoramentos de UX e Design:** Com o sistema estável, poderíamos investir em melhorar a experiência:
  - Temas escuro/claro para a interface.
  - Editor Markdown com preview em tempo real.
  - Drag-and-drop de imagens para dentro de documentos via web.
  - Melhor responsividade para uso em telas pequenas (celular/tablet).
  - Dashboard inicial mostrando documentos recentes ou favoritos.

Cada item do futuro pode ser implementado respeitando a arquitetura modular delineada: adicionando módulos ou plugins, sem quebrar os princípios fundamentais (arquivos como fonte, DB efêmero, componentes isolados). O importante é que o plano técnico atual estabelece bases sólidas – conteúdo em arquivos, validação rigorosa, sincronização reativa, backend e frontend desacoplados – sobre as quais é possível construir e inovar.

Com essa visão de extensibilidade e melhorias contínuas, o projeto Arca pode crescer de um gerenciador de conteúdo pessoal simples para uma plataforma robusta de conhecimento, sem perder seus princípios de simplicidade, transparência e modularidade. Isso garante que um LLM especializado (ou qualquer desenvolvedor) possa seguir este plano e implementar o sistema agora, sabendo que ele tem espaço para evoluir no futuro.
