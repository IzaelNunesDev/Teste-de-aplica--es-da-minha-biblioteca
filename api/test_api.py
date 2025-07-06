#!/usr/bin/env python3
"""
Script para testar a API FastAPI
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Testa endpoint de saúde"""
    print("🏥 Testando health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_stats():
    """Testa estatísticas do sistema"""
    print("📊 Testando estatísticas...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_benchmark():
    """Testa benchmark das ORMs"""
    print("🚀 Testando benchmark...")
    
    # Benchmark pequeno para teste rápido
    payload = {
        "sample_size": 100,
        "orm_type": "both",
        "operation": "both"
    }
    
    response = requests.post(f"{BASE_URL}/benchmark", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print("✅ Benchmark executado com sucesso!")
        for result in results:
            print(f"  {result['orm']}: {result['ops_per_second']:.0f} ops/s, {result['memory_mb']:.1f} MB")
    else:
        print(f"❌ Erro: {response.text}")
    print()

def test_compare():
    """Testa comparação das ORMs"""
    print("⚖️ Testando comparação...")
    response = requests.get(f"{BASE_URL}/compare")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        comparison = response.json()
        print("✅ Comparação executada!")
        print(json.dumps(comparison, indent=2))
    else:
        print(f"❌ Erro: {response.text}")
    print()

def test_taxi_operations():
    """Testa operações com dados de taxi"""
    print("🚕 Testando operações de taxi...")
    
    # Buscar viagens
    response = requests.get(f"{BASE_URL}/taxis/1?limit=3")
    print(f"Buscar viagens - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Viagens encontradas: {response.json()}")
    else:
        print(f"Erro: {response.text}")
    
    # Inserir viagens de exemplo
    sample_trips = [
        {
            "vendor_id": "99",
            "pickup_datetime": "2024-01-01T12:00:00",
            "dropoff_datetime": "2024-01-01T12:30:00",
            "passenger_count": 2,
            "trip_distance": 5.5,
            "rate_code_id": 1,
            "store_and_fwd_flag": "N",
            "payment_type": "1",
            "fare_amount": 15.50,
            "extra": 1.0,
            "mta_tax": 0.5,
            "tip_amount": 3.0,
            "tolls_amount": 0.0,
            "improvement_surcharge": 1.0,
            "total_amount": 21.0,
            "congestion_surcharge": 2.5,
            "airport_fee": 0.0
        }
    ]
    
    response = requests.post(f"{BASE_URL}/taxis/bulk", json=sample_trips)
    print(f"Inserir viagens - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Viagens inseridas: {response.json()}")
    else:
        print(f"Erro: {response.text}")
    print()

def test_performance():
    """Testa performance da API"""
    print("⚡ Testando performance da API...")
    
    # Teste de latência
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/health")
    end_time = time.time()
    
    latency = (end_time - start_time) * 1000  # em ms
    print(f"Latência do health check: {latency:.2f}ms")
    
    # Teste de throughput
    print("Testando throughput (10 requests)...")
    start_time = time.time()
    
    for i in range(10):
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(f"❌ Erro na requisição {i+1}")
    
    end_time = time.time()
    total_time = end_time - start_time
    throughput = 10 / total_time
    
    print(f"Throughput: {throughput:.2f} requests/segundo")
    print()

def main():
    """Executa todos os testes"""
    print("🧪 INICIANDO TESTES DA API")
    print("=" * 50)
    
    try:
        # Testes básicos
        test_health()
        test_stats()
        
        # Testes de benchmark
        test_benchmark()
        test_compare()
        
        # Testes de operações
        test_taxi_operations()
        
        # Testes de performance
        test_performance()
        
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API")
        print("Certifique-se de que a API está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ ERRO: {e}")

if __name__ == "__main__":
    main() 