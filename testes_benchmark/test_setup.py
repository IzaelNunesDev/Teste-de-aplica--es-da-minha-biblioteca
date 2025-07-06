#!/usr/bin/env python3
"""
Script de teste para verificar configuração do benchmark
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    print("🔍 Testando imports...")
    
    try:
        import caspyorm
        print("✅ CaspyORM importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar CaspyORM: {e}")
        return False
    
    try:
        import cassandra
        print("✅ cassandra-driver importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar cassandra-driver: {e}")
        return False
    
    try:
        import cqlengine
        print("✅ cqlengine importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar cqlengine: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar pandas: {e}")
        return False
    
    try:
        import rich
        print("✅ rich importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar rich: {e}")
        return False
    
    try:
        import psutil
        print("✅ psutil importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar psutil: {e}")
        return False
    
    return True

def test_data_loading():
    """Testa se os dados podem ser carregados"""
    print("\n📊 Testando carregamento de dados...")
    
    try:
        from benchmark.utils import load_nyc_taxi_data
        from benchmark.config import get_data_config
        
        data_config = get_data_config()
        parquet_file = data_config['parquet_file']
        
        if not Path(parquet_file).exists():
            print(f"❌ Arquivo de dados não encontrado: {parquet_file}")
            return False
        
        # Carrega uma amostra pequena
        df = load_nyc_taxi_data(parquet_file, sample_size=100)
        print(f"✅ Dados carregados: {len(df)} registros")
        print(f"   Colunas: {list(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False

def test_config():
    """Testa se as configurações podem ser carregadas"""
    print("\n⚙️ Testando configurações...")
    
    try:
        from benchmark.config import (
            get_connection_config, 
            get_benchmark_config, 
            get_data_config,
            get_schema_config
        )
        
        conn_config = get_connection_config()
        bench_config = get_benchmark_config()
        data_config = get_data_config()
        schema_config = get_schema_config()
        
        print("✅ Configurações carregadas com sucesso")
        print(f"   Cassandra: {conn_config['hosts']}:{conn_config['port']}")
        print(f"   Keyspace: {conn_config['keyspace']}")
        print(f"   Sample size: {bench_config['sample_size']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DE CONFIGURAÇÃO DO BENCHMARK")
    print("=" * 50)
    
    # Testa imports
    if not test_imports():
        print("\n❌ Falha nos imports. Verifique as dependências.")
        return
    
    # Testa configurações
    if not test_config():
        print("\n❌ Falha nas configurações.")
        return
    
    # Testa carregamento de dados
    if not test_data_loading():
        print("\n❌ Falha no carregamento de dados.")
        return
    
    print("\n✅ Todos os testes passaram!")
    print("\n🚀 Para executar o benchmark completo:")
    print("   python benchmark/run_benchmark.py")
    print("\n⚠️  Nota: Você precisa ter um Cassandra rodando em localhost:9042")

if __name__ == "__main__":
    main() 