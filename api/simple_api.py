#!/usr/bin/env python3
"""
API FastAPI Simplificada para Teste
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import time
import psutil
import os
from datetime import datetime

app = FastAPI(
    title="Simple Benchmark API",
    description="API simplificada para teste",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class BenchmarkRequest(BaseModel):
    sample_size: int = 100
    orm_type: str = "both"
    operation: str = "insert"

class BenchmarkResult(BaseModel):
    orm: str
    operation: str
    records_processed: int
    time_seconds: float
    ops_per_second: float
    memory_mb: float
    timestamp: datetime

# Estado global
benchmark_results: List[BenchmarkResult] = []

def get_memory_usage():
    """Obtém uso de memória em MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Simple Benchmark API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Verifica saúde da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "memory_usage_mb": get_memory_usage(),
        "cpu_percent": psutil.cpu_percent()
    }

@app.get("/stats")
async def get_stats():
    """Estatísticas do sistema"""
    return {
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "application": {
            "memory_usage_mb": get_memory_usage(),
            "benchmarks_executed": len(benchmark_results)
        }
    }

@app.post("/benchmark", response_model=List[BenchmarkResult])
async def run_benchmark(request: BenchmarkRequest):
    """Executa benchmark simulado"""
    results = []
    
    # Simula benchmark CaspyORM
    if request.orm_type in ["caspyorm", "both"]:
        start_time = time.time()
        mem_before = get_memory_usage()
        
        # Simula processamento
        time.sleep(0.1)  # Simula trabalho
        
        end_time = time.time()
        mem_after = get_memory_usage()
        
        caspy_result = BenchmarkResult(
            orm="CaspyORM",
            operation=request.operation,
            records_processed=request.sample_size,
            time_seconds=end_time - start_time,
            ops_per_second=request.sample_size / (end_time - start_time),
            memory_mb=mem_after - mem_before,
            timestamp=datetime.now()
        )
        results.append(caspy_result)
    
    # Simula benchmark CQLengine
    if request.orm_type in ["cqlengine", "both"]:
        start_time = time.time()
        mem_before = get_memory_usage()
        
        # Simula processamento mais lento
        time.sleep(0.2)  # Simula trabalho mais lento
        
        end_time = time.time()
        mem_after = get_memory_usage()
        
        cql_result = BenchmarkResult(
            orm="CQLengine",
            operation=request.operation,
            records_processed=request.sample_size,
            time_seconds=end_time - start_time,
            ops_per_second=request.sample_size / (end_time - start_time),
            memory_mb=mem_after - mem_before,
            timestamp=datetime.now()
        )
        results.append(cql_result)
    
    # Armazena resultados
    benchmark_results.extend(results)
    
    return results

@app.get("/results", response_model=List[BenchmarkResult])
async def get_results():
    """Retorna resultados dos benchmarks"""
    return benchmark_results

@app.get("/compare")
async def compare_orms():
    """Compara resultados das ORMs"""
    if not benchmark_results:
        raise HTTPException(status_code=404, detail="Nenhum benchmark executado")
    
    # Agrupa por ORM
    caspy_results = [r for r in benchmark_results if r.orm == "CaspyORM"]
    cql_results = [r for r in benchmark_results if r.orm == "CQLengine"]
    
    comparison = {
        "caspyorm": {
            "total_benchmarks": len(caspy_results),
            "avg_ops_per_second": sum(r.ops_per_second for r in caspy_results) / len(caspy_results) if caspy_results else 0,
            "avg_memory_mb": sum(r.memory_mb for r in caspy_results) / len(caspy_results) if caspy_results else 0,
            "total_records": sum(r.records_processed for r in caspy_results)
        },
        "cqlengine": {
            "total_benchmarks": len(cql_results),
            "avg_ops_per_second": sum(r.ops_per_second for r in cql_results) / len(cql_results) if cql_results else 0,
            "avg_memory_mb": sum(r.memory_mb for r in cql_results) / len(cql_results) if cql_results else 0,
            "total_records": sum(r.records_processed for r in cql_results)
        }
    }
    
    # Calcula diferenças
    if caspy_results and cql_results:
        caspy_avg_ops = comparison["caspyorm"]["avg_ops_per_second"]
        cql_avg_ops = comparison["cqlengine"]["avg_ops_per_second"]
        
        comparison["performance_diff"] = {
            "caspyorm_faster": ((caspy_avg_ops / cql_avg_ops) - 1) * 100 if cql_avg_ops > 0 else 0,
            "memory_efficiency": ((comparison["cqlengine"]["avg_memory_mb"] / comparison["caspyorm"]["avg_memory_mb"]) - 1) * 100 if comparison["caspyorm"]["avg_memory_mb"] > 0 else 0
        }
    
    return comparison

@app.get("/demo")
async def demo_endpoints():
    """Demonstra todos os endpoints"""
    return {
        "endpoints": {
            "GET /": "Informações da API",
            "GET /health": "Status da aplicação",
            "GET /stats": "Estatísticas do sistema",
            "POST /benchmark": "Executar benchmark",
            "GET /results": "Resultados dos benchmarks",
            "GET /compare": "Comparar ORMs",
            "GET /demo": "Esta página"
        },
        "example_benchmark": {
            "sample_size": 1000,
            "orm_type": "both",
            "operation": "both"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando API em http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000) 