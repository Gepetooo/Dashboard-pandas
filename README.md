# Dashboard de análise exploratória

Aplicação Django com análise em Pandas e visualizações interativas em Plotly.js. Os filtros permitem explorar sexo, classe e faixa etária. As visualizações comparam taxa de sobrevivência por classe e sexo, distribuição de idade por desfecho, tarifas por classe, passageiros por local de embarque, taxa por faixa etária e correlações entre variáveis numéricas.

A estrutura da página está em `analytics/templates/analytics/dashboard.html`, os estilos em `analytics/static/analytics/dashboard.css` e a inicialização dos gráficos em `analytics/static/analytics/dashboard.js`.

## Dados utilizados

- Conjunto/tabela: Titanic, arquivo `titanic.csv` do repositório público Seaborn Data Repository.
- Granularidade: uma linha por registro de passageiro; o CSV contém 891 registros e 15 colunas.
- Colunas carregadas: `survived`, `pclass`, `sex`, `age`, `sibsp`, `parch`, `fare`, `embarked`, `deck` e `embark_town`.
- Fonte e documentação: https://github.com/mwaskom/seaborn-data
- Arquivo CSV: https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv
- Cópia local do arquivo: `data/titanic.csv` (incluída no projeto; o dashboard lê essa cópia sem precisar baixar o dataset a cada execução).
- Justificativa: conjunto conhecido e pequeno, com variáveis numéricas e categóricas que permitem analisar distribuições, valores ausentes, comparações entre grupos e correlações com o desfecho.
- Tratamento: conversão numérica com Pandas, padronização dos campos textuais e preenchimento apenas do rótulo de local de embarque ausente como “Não informado” na visualização. Os registros originais permanecem preservados; valores ausentes não são imputados e tarifas atípicas são sinalizadas pela regra IQR, mas mantidas.
- Análise: `describe()` resume idade, tarifa, irmãos/cônjuges e pais/filhos a bordo; a matriz usa correlação de Pearson entre sobrevivência, classe, idade, tarifa e composição familiar. Gráficos de sobrevivência por classe e faixa etária apresentam padrões exploratórios entre grupos.
- Limitação: o CSV não possui variável de data/ano, portanto não permite tendência temporal; a análise de tendências é feita entre faixas etárias e classes. Correlação não implica causalidade.

## Execução

Instale as dependências listadas em `requirements.txt`, entre na pasta `dashboard` e execute `python manage.py runserver`. Abra `http://127.0.0.1:8000/`. A função `carregar_conjunto_dados()` carrega o dataset da cópia local e mantém o resultado em cache na memória do processo Django; não é necessária conexão para acessar os dados. O Plotly.js e a localização em português são carregados por CDN.