#!/usr/bin/env python3
"""
Teste de conexão com Cassandra
"""

try:
    from cassandra.cluster import Cluster
    
    print("🔍 Testando conexão com Cassandra...")
    
    # Conecta ao cluster
    cluster = Cluster(['localhost'])
    session = cluster.connect()
    
    print("✅ Conectado ao Cassandra com sucesso!")
    
    # Lista keyspaces
    keyspaces = session.execute("DESCRIBE KEYSPACES")
    print(f"📋 Keyspaces disponíveis: {[ks.keyspace_name for ks in keyspaces]}")
    
    # Fecha conexão
    session.shutdown()
    cluster.shutdown()
    
    print("✅ Teste de conexão concluído!")
    
except Exception as e:
    print(f"❌ Erro ao conectar com Cassandra: {e}")
    print("💡 Verifique se o Cassandra está rodando em localhost:9042") 