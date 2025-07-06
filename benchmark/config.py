"""
Configurações para o benchmark CaspyORM vs CQLengine
"""

import os
from typing import Dict, Any

# Configurações do Cassandra
CASSANDRA_CONFIG = {
    'hosts': ['localhost'],
    'port': 9042,
    'keyspace': 'benchmark_nyc_taxi',
    'consistency_level': 'ONE'
}

# Configurações do benchmark
BENCHMARK_CONFIG = {
    'sample_size': 50000,  # Número de registros para teste (50k para benchmark robusto)
    'query_iterations': 1000,  # Número de queries para teste de consulta
    'batch_size': 2000,  # Tamanho do batch para inserções
    'warmup_iterations': 100  # Iterações de aquecimento
}

# Configurações ULTRA para benchmark otimizado
ULTRA_BENCHMARK_CONFIG = {
    'chunk_size': 50000,  # Chunks maiores para reduzir I/O
    'batch_size': 50,  # Batches maiores para bulk operations
    'target_size_gb': 0.5,  # Tamanho alvo em GB para o dataset
    'memory_monitoring': True,  # Monitoramento de memória em tempo real
    'progress_logging': True,  # Log progressivo detalhado
    'preprocessing_optimized': True,  # Pré-processamento otimizado
    'bulk_operations': True,  # Usar operações bulk quando disponível
    'parallel_processing': False,  # Processamento paralelo (desabilitado por padrão)
    'cache_models': True,  # Cache de modelos para reutilização
    'optimized_queries': True  # Queries otimizadas
}

# Configurações de dados
DATA_CONFIG = {
    'parquet_file': 'data/nyc_taxi/yellow_tripdata_combined.parquet',
    'parquet_files': [
        'data/nyc_taxi/yellow_tripdata_2024-01.parquet',
        'data/nyc_taxi/yellow_tripdata_2024-02.parquet', 
        'data/nyc_taxi/yellow_tripdata_2024-03.parquet'
    ],
    'target_records': 100000  # 100k registros para benchmark ULTRA
}

# Schema da tabela NYC Taxi
NYC_TAXI_SCHEMA = {
    'table_name': 'yellow_taxi_trips',
    'columns': {
        'vendor_id': 'text',
        'pickup_datetime': 'timestamp',
        'dropoff_datetime': 'timestamp', 
        'passenger_count': 'int',
        'trip_distance': 'float',
        'rate_code_id': 'int',
        'store_and_fwd_flag': 'text',
        'payment_type': 'text',
        'fare_amount': 'float',
        'extra': 'float',
        'mta_tax': 'float',
        'tip_amount': 'float',
        'tolls_amount': 'float',
        'improvement_surcharge': 'float',
        'total_amount': 'float',
        'congestion_surcharge': 'float',
        'airport_fee': 'float'
    },
    'partition_key': ['vendor_id', 'pickup_datetime'],
    'clustering_key': ['dropoff_datetime']
}

def get_connection_config() -> Dict[str, Any]:
    """Retorna configuração de conexão com Cassandra"""
    return CASSANDRA_CONFIG.copy()

def get_benchmark_config() -> Dict[str, Any]:
    """Retorna configuração do benchmark"""
    return BENCHMARK_CONFIG.copy()

def get_data_config() -> Dict[str, Any]:
    """Retorna configuração de dados"""
    return DATA_CONFIG.copy()

def get_schema_config() -> Dict[str, Any]:
    """Retorna configuração do schema"""
    return NYC_TAXI_SCHEMA.copy() 