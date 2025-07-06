#!/usr/bin/env python3
"""
Script para executar os demos CaspyORM vs CQLengine side-by-side
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def print_banner():
    """Imprime banner do script"""
    print("🚀" * 50)
    print("   DEMOS CASPYORM vs CQLENGINE - SIDE BY SIDE")
    print("🚀" * 50)
    print()

def print_info():
    """Imprime informações sobre os demos"""
    print("📋 INFORMAÇÕES:")
    print("   • CaspyORM Demo: http://localhost:8000")
    print("   • CQLengine Demo: http://localhost:8001")
    print("   • Documentação CaspyORM: http://localhost:8000/docs")
    print("   • Documentação CQLengine: http://localhost:8001/docs")
    print()

def check_requirements():
    """Verifica se os requisitos estão instalados"""
    print("🔍 Verificando requisitos...")
    
    # Verifica se o Cassandra está rodando
    try:
        import cassandra
        print("✅ cassandra-driver instalado")
    except ImportError:
        print("❌ cassandra-driver não encontrado")
        print("   Execute: pip install cassandra-driver")
        return False
    
    # Verifica se o FastAPI está instalado
    try:
        import fastapi
        print("✅ FastAPI instalado")
    except ImportError:
        print("❌ FastAPI não encontrado")
        print("   Execute: pip install fastapi uvicorn")
        return False
    
    # Verifica se o CaspyORM está instalado
    try:
        import caspyorm
        print("✅ CaspyORM instalado")
    except ImportError:
        print("❌ CaspyORM não encontrado")
        print("   Execute: pip install caspyorm")
        return False
    
    # Verifica se o CQLengine está instalado
    try:
        import cassandra.cqlengine
        print("✅ CQLengine instalado")
    except ImportError:
        print("❌ CQLengine não encontrado")
        print("   Execute: pip install cqlengine")
        return False
    
    print("✅ Todos os requisitos atendidos!")
    print()
    return True

def install_dependencies():
    """Instala dependências dos demos"""
    print("📦 Instalando dependências...")
    
    # Instala dependências do CaspyORM demo
    caspyorm_path = Path("caspyorm_demo")
    if caspyorm_path.exists():
        print("   Instalando dependências CaspyORM...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "caspyorm_demo/requirements.txt"], 
                      check=True, capture_output=True)
        print("   ✅ Dependências CaspyORM instaladas")
    
    # Instala dependências do CQLengine demo
    cqlengine_path = Path("cqlengine_demo")
    if cqlengine_path.exists():
        print("   Instalando dependências CQLengine...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "cqlengine_demo/requirements.txt"], 
                      check=True, capture_output=True)
        print("   ✅ Dependências CQLengine instaladas")
    
    print("✅ Todas as dependências instaladas!")
    print()

def start_caspyorm_demo():
    """Inicia o demo CaspyORM"""
    print("🚀 Iniciando CaspyORM Demo...")
    
    caspyorm_path = Path("caspyorm_demo")
    if not caspyorm_path.exists():
        print("❌ Pasta caspyorm_demo não encontrada!")
        return None
    
    # Muda para o diretório do demo
    os.chdir(caspyorm_path)
    
    # Inicia o servidor
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--reload", "--host", "0.0.0.0", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Volta para o diretório original
    os.chdir("..")
    
    print("   ✅ CaspyORM Demo iniciado em http://localhost:8000")
    return process

def start_cqlengine_demo():
    """Inicia o demo CQLengine"""
    print("🔄 Iniciando CQLengine Demo...")
    
    cqlengine_path = Path("cqlengine_demo")
    if not cqlengine_path.exists():
        print("❌ Pasta cqlengine_demo não encontrada!")
        return None
    
    # Muda para o diretório do demo
    os.chdir(cqlengine_path)
    
    # Inicia o servidor
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--reload", "--host", "0.0.0.0", "--port", "8001"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Volta para o diretório original
    os.chdir("..")
    
    print("   ✅ CQLengine Demo iniciado em http://localhost:8001")
    return process

def print_comparison_guide():
    """Imprime guia de comparação"""
    print("🔍 GUIA DE COMPARAÇÃO:")
    print()
    print("📊 Testes de Performance:")
    print("   CaspyORM: curl http://localhost:8000/api/v1/caspyorm/performance/benchmark")
    print("   CQLengine: curl http://localhost:8001/api/v1/cqlengine/performance/benchmark")
    print()
    print("📈 Comparações:")
    print("   CaspyORM: curl http://localhost:8000/api/v1/caspyorm/performance/compare")
    print("   CQLengine: curl http://localhost:8001/api/v1/cqlengine/performance/compare")
    print()
    print("📚 Demonstrações de Sintaxe:")
    print("   CaspyORM: curl http://localhost:8000/api/v1/caspyorm/demo/syntax")
    print("   CQLengine: curl http://localhost:8001/api/v1/cqlengine/demo/syntax")
    print()
    print("🏥 Health Checks:")
    print("   CaspyORM: curl http://localhost:8000/health")
    print("   CQLengine: curl http://localhost:8001/health")
    print()

def print_example_requests():
    """Imprime exemplos de requests"""
    print("📝 EXEMPLOS DE REQUESTS:")
    print()
    print("🔹 Criar Viagem (CaspyORM):")
    print("   curl -X POST http://localhost:8000/api/v1/caspyorm/trips \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "vendor_id": "1",')
    print('       "pickup_datetime": "2024-01-01T12:00:00",')
    print('       "dropoff_datetime": "2024-01-01T12:30:00",')
    print('       "passenger_count": 2,')
    print('       "trip_distance": 5.5,')
    print('       "rate_code_id": "1",')
    print('       "store_and_fwd_flag": "N",')
    print('       "payment_type": "1",')
    print('       "fare_amount": 15.50,')
    print('       "total_amount": 21.0')
    print("     }'")
    print()
    print("🔹 Buscar Viagens (CaspyORM):")
    print("   curl 'http://localhost:8000/api/v1/caspyorm/trips?vendor_id=1&limit=10'")
    print()
    print("🔹 Estatísticas (CaspyORM):")
    print("   curl http://localhost:8000/api/v1/caspyorm/stats")
    print()

def main():
    """Função principal"""
    print_banner()
    
    # Verifica requisitos
    if not check_requirements():
        print("❌ Requisitos não atendidos. Instale as dependências primeiro.")
        sys.exit(1)
    
    # Instala dependências dos demos
    install_dependencies()
    
    print_info()
    
    # Inicia os demos
    caspyorm_process = start_caspyorm_demo()
    time.sleep(2)  # Aguarda um pouco
    
    cqlengine_process = start_cqlengine_demo()
    time.sleep(2)  # Aguarda um pouco
    
    print()
    print("🎉 AMBOS OS DEMOS INICIADOS!")
    print()
    
    print_comparison_guide()
    print_example_requests()
    
    print("⏳ Pressione Ctrl+C para parar os demos...")
    print()
    
    try:
        # Aguarda indefinidamente
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("🛑 Parando demos...")
        
        # Para os processos
        if caspyorm_process:
            caspyorm_process.terminate()
            print("   ✅ CaspyORM Demo parado")
        
        if cqlengine_process:
            cqlengine_process.terminate()
            print("   ✅ CQLengine Demo parado")
        
        print("👋 Demos finalizados!")

if __name__ == "__main__":
    main() 