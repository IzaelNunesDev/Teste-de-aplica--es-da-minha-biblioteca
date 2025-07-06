# 🏁 Benchmark CaspyORM vs CQLengine

Projeto de benchmark comparativo entre **CaspyORM** e **CQLengine** para demonstrar performance, produtividade e features.

## 📊 Métricas Comparadas

- 🚀 **Velocidade de inserção** (rows/s)
- 🔍 **Velocidade de consulta** (queries/s)  
- 🧠 **Consumo de memória** (MB)
- ⚙️ **Suporte async** (CaspyORM ✅ / CQLengine ❌)
- 🔧 **Schema sync** (Automático / Manual)
- 📦 **Integração Pydantic** (Nativa / Ausente)

## 🚀 Como Executar

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Executar benchmark
python benchmark/run_benchmark.py
```

## 📁 Estrutura do Projeto

```
benchmark/
├── core/
│   ├── base_caspy.py       # Teste CaspyORM
│   └── base_cqlengine.py   # Teste CQLengine
├── run_benchmark.py        # Script principal
├── config.py              # Configurações
├── utils.py               # Utilitários
└── results/               # Resultados JSON
```

## 📈 Resultado Esperado

```
📊 Inserção de 50.000 registros:
   CaspyORM     → 842 registros/s
   CQLengine    → 610 registros/s
   ✅ CaspyORM mais rápido por ~38%

🔍 Consulta simples (1k queries):
   CaspyORM     → 19.231 ops/s
   CQLengine    → 11.212 ops/s
```

## 🔧 Configuração

Edite `benchmark/config.py` para ajustar:
- Conexão Cassandra
- Tamanho da amostra
- Número de queries
- Tamanho do batch

## 📝 Dependências

- CaspyORM (standalone)
- cassandra-driver
- cqlengine  
- pandas
- rich
- psutil 