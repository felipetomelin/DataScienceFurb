# 🏎️ DataScienceFurb — F1 2026 Lap Times & Telemetry

**Disciplina:** Data Science  
**Instituição:** FURB — Universidade Regional de Blumenau  
**Aluno:** Felipe Tomelin  

---

## Dataset

**Name:** F1 2026 Season — Lap Times & Telemetry  
**Source:** [Kaggle — stevefza/f1-2026-bahrain-testing-day-2](https://www.kaggle.com/datasets/stevefza/f1-2026-bahrain-testing-day-2)

> Raw CSV files are **not committed** to this repository (~203 MB total). Download directly from Kaggle and place in `data/raw/`.

---

## Repository Structure

```
DataScienceFurb/
├── data/
│   ├── raw/                  # CSVs originais do Kaggle (não commitados — ver .gitignore)
│   ├── processed/            # Dataset limpo após Data Preparation
│   └── README.md             # Descrição dos arquivos do dataset
│
├── notebooks/
│   └── data_preparation.py   # Pipeline de Data Preparation (ETL)
│
├── docs/
│   └── DATA_DICTIONARY.md    # Dicionário de dados — todos os campos pós-preparação
│
└── README.md                 # Este arquivo
```

---

## Etapas do Projeto

### ✅ Etapa 1 — Data Preparation
Pipeline implementado em [`notebooks/data_preparation.py`](notebooks/data_preparation.py).

Etapas realizadas:
1. **Load** — Carregamento de todos os CSVs da pasta `data/raw/`
2. **Normalização de colunas** — `snake_case`, lowercase, sem caracteres especiais
3. **Tratamento de valores ausentes** — imputação por mediana/moda; drop de colunas com ≥ 80% missing
4. **Validação de tipos** — lap times parseados de string para float (segundos); booleanos corrigidos
5. **Remoção de duplicatas**
6. **Feature Engineering** — `laptime_formatted`, `tyre_life_category`, `speed_*_delta_pct`, `session_tag`
7. **Tratamento de outliers** — método IQR 3× com Winsorização (caps, sem remoção de linhas)
8. **Export** — CSV limpo salvo em `data/processed/f1_2026_laps_cleaned.csv`

### ✅ Etapa 2 — Data Dictionary
Documentação completa de todos os campos disponível em [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

---

## Como Executar

```bash
# 1. Clone o repositório
git clone https://github.com/felipetomelin/DataScienceFurb.git
cd DataScienceFurb

# 2. Baixe o dataset do Kaggle e coloque em data/raw/
#    https://www.kaggle.com/datasets/stevefza/f1-2026-bahrain-testing-day-2

# 3. Instale as dependências
pip install pandas numpy

# 4. Execute o pipeline de Data Preparation
python notebooks/data_preparation.py
```

---

## Dependências

| Biblioteca | Versão mínima | Uso |
|---|---|---|
| `pandas` | ≥ 1.5 | Manipulação de DataFrames |
| `numpy` | ≥ 1.23 | Operações numéricas |
| `glob` | built-in | Leitura de múltiplos CSVs |
