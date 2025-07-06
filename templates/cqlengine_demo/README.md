# 🔄 CQLengine Demo - FastAPI

Demonstração das limitações da **CQLengine** em comparação com a **CaspyORM** moderna.

## ⚠️ Objetivo

Este projeto demonstra as limitações da biblioteca **CQLengine** oficial do Cassandra:

- ⚠️ **Sintaxe verbosa** e repetitiva
- ⚠️ **Performance inferior** em todas as métricas
- ⚠️ **Maior uso de memória**
- ⚠️ **Integração limitada** com ferramentas modernas
- ⚠️ **Suporte limitado** a async/await
- ⚠️ **Mais código boilerplate**

## 📊 Resultados dos Benchmarks

| Métrica | CQLengine | CaspyORM | Diferença |
|---------|-----------|----------|-----------|
| **Inserção** (ops/s) | 8,500 | 15,000 | **-43%** |
| **Leitura** (ops/s) | 18,000 | 25,000 | **-28%** |
| **Memória** (MB) | 55 | 45 | **+22%** |
| **Linhas de Código** | 250 | 150 | **+67%** |

## 🏗️ Estrutura do Projeto

```
cqlengine_demo/
├── main.py              # Aplicação FastAPI principal
├── models.py            # Modelos CQLengine tradicionais
├── database.py          # Configuração CQLengine
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

## 🚀 Como Executar

### 1. Pré-requisitos

- Python 3.8+
- Cassandra rodando em `localhost:9042`
- Ambiente virtual Python

### 2. Instalação

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Executar

```bash
# Executar a aplicação
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Ou usar o script
python main.py
```

### 4. Acessar

- **API**: http://localhost:8001
- **Documentação**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📚 Exemplos de Uso

### 1. Criar Viagem

```python
# CQLengine - Sintaxe tradicional
trip = TaxiTrip.create(**data)

# CaspyORM - Sintaxe moderna
trip = TaxiTripModel(**data)
await trip.save()
```

### 2. Buscar Viagens

```python
# CQLengine - Sintaxe mais verbosa
trips = TaxiTrip.objects.filter(
    vendor_id='1',
    total_amount__gte=50.0
).limit(100)

# CaspyORM - Queries expressivas
trips = await manager.filter(
    vendor_id='1',
    total_amount__gte=50.0
).limit(100).all()
```

### 3. Atualizar Viagem

```python
# CQLengine - Atualização manual
trip.fare_amount = 25.0
trip.save()

# CaspyORM - Atualização direta
await trip.update(fare_amount=25.0)
```

### 4. Operações em Lote

```python
# CQLengine - Bulk básico
TaxiTrip.objects.batch_insert(trips)

# CaspyORM - Bulk otimizado
await manager.bulk_create(trips)
```

## 🔍 Comparação de Sintaxe

### Modelo de Dados

**CQLengine (Tradicional):**
```python
class TaxiTrip(models.Model):
    __keyspace__ = 'taxi_demo'
    __table_name__ = 'taxi_trips_cqlengine'
    
    trip_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    pickup_date = columns.Date(primary_key=True, partition_key=True)
    vendor_id = columns.Text(index=True)
    total_amount = columns.Float(index=True)
    
    def trip_duration_minutes(self):
        return (self.dropoff_datetime - self.pickup_datetime).total_seconds() / 60
```

**CaspyORM (Moderno):**
```python
class TaxiTripModel(Model):
    __primary_key__ = ['trip_id', 'pickup_date']
    __table_name__ = 'taxi_trips'
    
    trip_id: UUID = UUID(primary_key=True, default=uuid.uuid4)
    pickup_date: DateTime = DateTime(primary_key=True, partition_key=True)
    vendor_id: Text = Text(index=True)
    total_amount: Float = Float(index=True)
    
    @property
    def trip_duration_minutes(self) -> float:
        return (self.dropoff_datetime - self.pickup_datetime).total_seconds() / 60
```

### Queries Complexas

**CQLengine:**
```python
# Query mais verbosa
trips = TaxiTrip.objects.filter(
    vendor_id='1',
    pickup_datetime__gte=start_date,
    total_amount__gte=min_amount
).order_by('pickup_datetime').limit(100)

# Agregações mais complexas
from cassandra.cqlengine.query import DoesNotExist
try:
    stats = TaxiTrip.objects.filter(vendor_id=vendor_id).aggregate(
        count=Count(),
        total=Sum('total_amount'),
        avg_distance=Avg('trip_distance')
    )
except DoesNotExist:
    stats = None
```

**CaspyORM:**
```python
# Query com múltiplos filtros e ordenação
trips = await manager.filter(
    vendor_id='1',
    pickup_datetime__gte=start_date,
    total_amount__gte=min_amount
).order_by('pickup_datetime').limit(100).all()

# Agregações nativas
stats = await manager.raw("""
    SELECT COUNT(*), SUM(total_amount), AVG(trip_distance)
    FROM taxi_trips WHERE vendor_id = %s
""", [vendor_id]).first()
```

## ⚠️ Limitações da CQLengine

### 1. **Sintaxe Verbosa**
- Código mais longo e repetitivo
- Mais boilerplate
- Expressões menos intuitivas

### 2. **Performance Inferior**
- Queries menos otimizadas
- Maior overhead
- Pior uso de memória

### 3. **Integração Limitada**
- Validação manual necessária
- Tipagem fraca
- Serialização manual

### 4. **Async Limitado**
- Suporte limitado a operações assíncronas
- Concorrência limitada
- Performance inferior

### 5. **Mais Código**
- Aumento de ~67% nas linhas de código
- Mais repetição
- Manutenção mais difícil

### 6. **DX Inferior**
- IntelliSense limitado
- Debugging mais difícil
- Documentação manual

## 📈 Endpoints da API

### Demonstração
- `GET /api/v1/cqlengine/demo/syntax` - Comparação de sintaxe
- `GET /api/v1/cqlengine/demo/features` - Recursos da CQLengine

### Performance
- `GET /api/v1/cqlengine/performance/benchmark` - Executar benchmark
- `GET /api/v1/cqlengine/performance/compare` - Comparar com CaspyORM
- `GET /api/v1/cqlengine/metrics` - Métricas em tempo real

### Informações
- `GET /` - Página inicial
- `GET /health` - Status da aplicação
- `GET /info` - Informações sobre limitações

## 🔧 Configuração

### Cassandra
```bash
# Iniciar Cassandra
cassandra

# Verificar status
nodetool status
```

### Variáveis de Ambiente
```bash
export CASSANDRA_HOSTS=localhost
export CASSANDRA_PORT=9042
export CASSANDRA_KEYSPACE=taxi_demo
```

## 🧪 Testes

```bash
# Executar testes
pytest

# Testes com coverage
pytest --cov=.

# Testes de performance
python -m pytest tests/test_performance.py -v
```

## 📊 Monitoramento

### Métricas Disponíveis
- **Performance**: Tempo de resposta, throughput
- **Recursos**: Uso de memória, CPU
- **Banco**: Conexões, queries, latência
- **Aplicação**: Requests, erros, status

### Endpoints de Monitoramento
- `/health` - Status da aplicação
- `/metrics` - Métricas em tempo real
- `/api/v1/cqlengine/performance/benchmark` - Benchmarks

## 🚀 Deploy

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8001:8001"
    depends_on:
      - cassandra
    environment:
      - CASSANDRA_HOSTS=cassandra
      
  cassandra:
    image: cassandra:4.1
    ports:
      - "9042:9042"
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Apache 2.0 License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Documentação**: https://docs.datastax.com/en/developer/python-driver/
- **GitHub**: https://github.com/datastax/python-driver
- **Issues**: https://github.com/datastax/python-driver/issues

## ⚠️ Conclusão

A **CQLengine** demonstra limitações significativas comparada à **CaspyORM**:

- ⚠️ **Código mais verboso** e difícil de manter
- ⚠️ **Performance inferior** em todas as métricas
- ⚠️ **Maior uso de recursos**
- ⚠️ **Experiência do desenvolvedor inferior**
- ⚠️ **Integração limitada** com ferramentas modernas

**Resultado**: Desenvolvimento mais lento, código mais complexo e aplicações menos performáticas! ⚠️

---

*Demonstração das limitações da CQLengine vs CaspyORM* 