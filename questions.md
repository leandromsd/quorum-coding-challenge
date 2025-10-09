1) Discuta sua estratégia e decisões implementando a aplicação. Considere complexidade de tempo, custo de esforço, tecnologias usadas e outras variáveis importantes.

Li o enunciado e tentei pensar em algo que uma pessoa consiga baixar, rodar e entender em poucos minutos. Escolhi Django com Django REST Framework pela praticidade e familiaridade que já tenho com a stack. Em poucos minutos consigo criar modelos, rotas, serializers e páginas HTML funcionando. Usei SQLite para não exigir nenhum serviço externo; embora o enunciado dissesse que não precisava usar banco de dados, preferi usar esse banco para aplicar conceitos e demonstrar meu conhecimento na utilização do ORM, relacionamentos entre as tabelas e performance.

Para importar os CSVs criei um management command (load_data). Optei por pandas para ler os arquivos, pois é um framework fácil de usar e que também pode ser escalado, pois consegue ler grandes volumes de dados. A carga é transacional (se der erro, nada é aplicado), idempotente (limpo antes de inserir) e valida os arquivos com mensagens compreensíveis quando algo está errado (coluna faltando, patrocinador inexistente, vote_type inválido). A ideia é que, se a pessoa do outro lado errar um arquivo, ela consiga entender por que a carga falhou sem precisar abrir o código.

Na API, expus endpoints diretos para stats, legisladores e projetos, com listagem e detalhe. Não deixei paginação ligada por padrão para simplificar o uso neste desafio; é fácil habilitar depois, caso faça sentido. A interface web tem páginas simples com tabelas, apenas o necessário para visualizar as mesmas informações da API. Os testes cobrem o comando de carga, os modelos, os endpoints e as páginas. Preferi testes que simulam o uso: carregar dados, conferir idempotência, verificar as contagens e se as rotas respondem o que prometem.

Em termos de complexidade, a importação é linear no tamanho dos arquivos, e as consultas ficam baratas quando uso annotate para contar. Se o volume crescer, dá para indexar colunas usadas em filtros/ordenações e, se necessário, ativar paginação na API e recortes nas telas.

No front tentei fazer sem ajuda de frameworks adicionais e de forma simples. Como está tudo integrado com Django e DRF, eu poderia até fazer consultas diretamente nos modelos sem chamar a API. Optei por construir e usar as APIs porque isso permite ter um front isolado (ex.: React em outro repositório) consumindo os mesmos dados do back-end.

No fim, foquei em ser pragmático, usando menos camadas e mais clareza: poucos comandos para rodar, erros fáceis de entender e comportamento previsível.

2) Como você mudaria sua solução para considerar futuras colunas que poderiam ser solicitadas, como “Data de Votação do Projeto” ou “Co‑Patrocinadores”?

Para “Data de Votação”, eu adicionaria um campo de data em Vote (DateTimeField com timezone). O campo aceitaria null/blank para evitar problemas de migração com dados passados e adicionaria também um índice na coluna para ordenar e filtrar por período com eficiência. Não mudaria VoteResult, porque a data pertence ao evento de votação (Vote), não ao voto individual.

Para co‑patrocinadores, eu removeria o campo primary_sponsor do Bill e criaria uma tabela intermediária explícita entre Bill e Legislator para concentrar todo o patrocínio em um único lugar. Esse modelo (BillSponsorship) teria: bill, legislator, type (PRIMARY ou CO), além de campos opcionais, se necessário. Colocaria um UniqueConstraint em (bill, legislator) para evitar duplicidade e índices em (bill, type) e (legislator, type) para facilitar consultas. Se a regra do sistema for permitir apenas um patrocinador principal por bill, dá para impor uma restrição via constraint condicional que garanta no máximo um registro com type=PRIMARY por bill. Essa modelagem deixa o sistema pronto para evoluir (novos tipos de patrocínio, períodos, estados) sem precisar mexer novamente na estrutura básica.

3) Como você mudaria sua solução se, em vez de receber CSVs de dados, você recebesse uma lista de legisladores ou projetos de lei para os quais deveria gerar um CSV?

Eu inverteria o fluxo e criaria um comando de exportação (e, se necessário, um endpoint) que aceita legisladores ou projetos e escreve os arquivos CSV em um diretório de saída. Os nomes e formatos manteriam compatibilidade com os arquivos originais para facilitar integração. Validaria os dados recebidos, retornaria erros amigáveis se algo não existisse e geraria pelo menos legislators.csv, bills.csv, votes.csv e vote_results.csv. Para volumes maiores, consideraria mover a geração para uma tarefa assíncrona com filas, entregando um link de download quando pronto.

4) Quanto tempo você gastou trabalhando na tarefa?

Algo em torno de quatro a cinco horas no total, somando leitura do enunciado, organização do projeto, implementação dos modelos, loader, APIs, páginas e testes.
