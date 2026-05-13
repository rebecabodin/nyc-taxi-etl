# NYC Taxi ETL

Projeto de Engenharia de Dados focado na construção de um pipeline ETL simples utilizando dados de viagens de táxi amarelo de Nova York.

## Objetivo

O objetivo do projeto é criar um pipeline capaz de:

- Ler dados brutos em formato CSV
- Validar a qualidade dos dados
- Realizar transformações
- Criar métricas analíticas
- Persistir os dados tratados em Parquet
- Criar consultas e views SQL
- Disponibilizar um dashboard em Streamlit

## Fonte dos dados

Dataset utilizado:

**NYC Yellow Taxi Trip Data**

Fonte original: Kaggle / NYC Taxi & Limousine Commission

Arquivos utilizados no projeto:

- yellow_tripdata_2016-01.csv
- yellow_tripdata_2016-02.csv
- yellow_tripdata_2016-03.csv

Os arquivos CSV não são versionados no GitHub por serem arquivos grandes.

## Arquitetura do projeto

A arquitetura do pipeline segue o fluxo:

Kaggle → Camada Raw → Extract → Validate → Transform → Load → SQL Views → Dashboard

O desenho da arquitetura está disponível na pasta `docs/`.

## Estrutura do projeto

```text
nyc-taxi-etl/
├── app/
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
├── docs/
├── notebooks/
├── sql/
├── src/
├── .gitignore
└── README.md


Tecnologias utilizadas
Python
Pandas
PyArrow
BigQuery SQL
Streamlit
Git e GitHub
Status do projeto

Em desenvolvimento.

Etapas previstas:

 Desenho da arquitetura
 Criação da estrutura inicial do projeto
 Publicação inicial no GitHub
 Leitura dos arquivos CSV
 Validação dos dados
 Transformações
 Persistência em Parquet
 Criação de views SQL
 Dashboard em Streamlit

```text
