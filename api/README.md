# 🚀 API FastAPI - Benchmark ORM

API para demonstrar cenários de uso das ORMs CaspyORM vs CQLengine com FastAPI.

## 🏃‍♂️ Como Executar

```bash
# Ativar ambiente virtual
source ../venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar a API
python main.py
```

A API estará disponível em: http://localhost:8000

## 📚 Documentação Automática

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 Endpoints

### Informações Básicas
- `GET /` - Informações da API
- `GET /health` - Status da aplicação
- `GET /stats` - Estatísticas do sistema

### Benchmark
- `POST /benchmark` - Executar benchmark das ORMs
- `GET /results` - Resultados dos benchmarks
- `GET /compare` - Comparar performance das ORMs

### Operações com Dados
- `GET /taxis/{vendor_id}` - Buscar viagens por vendor_id
- `POST /taxis/bulk` - Inserir múltiplas viagens

## 📊 Exemplos de Uso

### Executar Benchmark
```bash
curl -X POST "http://localhost:8000/benchmark" \
     -H "Content-Type: application/json" \
     -d '{
       "sample_size": 1000,
       "orm_type": "both",
       "operation": "both"
     }'
```

### Comparar ORMs
```bash
curl "http://localhost:8000/compare"
```

### Buscar Viagens
```bash
curl "http://localhost:8000/taxis/1?limit=5"
```

## 🎯 Cenários de Uso

1. **Benchmark Comparativo** - Compara performance das ORMs
2. **Operações CRUD** - Demonstra operações básicas
3. **Bulk Operations** - Testa inserções em lote
4. **Queries Complexas** - Consultas por diferentes critérios
5. **Monitoramento** - Acompanha uso de recursos

## 🔧 Configuração

A API usa as mesmas configurações do benchmark:
- Cassandra local em `localhost:9042`
- Keyspace: `benchmark_nyc_taxi`
- Dataset: NYC Taxi (parquet files) 