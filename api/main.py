#!/usr/bin/env python3
"""
API FastAPI para Benchmark CaspyORM vs CQLengine
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import psutil
import os
import asyncio

from benchmark.core.base_caspy import CaspyORMBenchmark
from benchmark.core.base_cqlengine import CQLengineBenchmark
from benchmark.utils import load_nyc_taxi_data, memory_usage_mb

app = FastAPI(
    title="Benchmark ORM API",
    description="API para demonstrar cenários de uso das ORMs CaspyORM vs CQLengine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class TaxiTrip(BaseModel):
    vendor_id: str
    pickup_datetime: datetime
    dropoff_datetime: datetime
    passenger_count: int
    trip_distance: float
    rate_code_id: int
    store_and_fwd_flag: str
    payment_type: str
    fare_amount: float
    extra: float
    mta_tax: float
    tip_amount: float
    tolls_amount: float
    improvement_surcharge: float
    total_amount: float
    congestion_surcharge: float
    airport_fee: float

class BenchmarkRequest(BaseModel):
    sample_size: int = 1000
    orm_type: str = "both"  # "caspyorm", "cqlengine", "both"
    operation: str = "insert"  # "insert", "query", "both"

class BenchmarkResult(BaseModel):
    orm: str
    operation: str
    records_processed: int
    time_seconds: float
    ops_per_second: float
    memory_mb: float
    timestamp: datetime

# Estado global para armazenar resultados
benchmark_results: List[BenchmarkResult] = []
current_benchmark = None

@app.get("/")
async def root():
    return {
        "message": "Benchmark ORM API",
        "version": "1.0.0",
        "description": "API para demonstrar cenários de uso das ORMs",
        "docs": "/docs",
        "endpoints": [
            "/health", "/stats", "/benchmark", "/results", "/taxis", "/compare"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "memory_usage_mb": memory_usage_mb(),
        "cpu_percent": psutil.cpu_percent()
    }

@app.get("/stats")
async def get_stats():
    return {
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "application": {
            "memory_usage_mb": memory_usage_mb(),
            "benchmarks_executed": len(benchmark_results)
        }
    }

@app.post("/benchmark", response_model=List[BenchmarkResult])
async def run_benchmark(request: BenchmarkRequest, background_tasks: BackgroundTasks):
    global current_benchmark
    if current_benchmark:
        raise HTTPException(status_code=400, detail="Benchmark já está em execução")
    try:
        current_benchmark = True
        results = []
        df = load_nyc_taxi_data("data/nyc_taxi/yellow_tripdata_combined.parquet", request.sample_size)
        if request.orm_type in ["caspyorm", "both"]:
            caspy_result = await run_caspyorm_benchmark(df, request.operation)
            results.append(caspy_result)
        if request.orm_type in ["cqlengine", "both"]:
            cql_result = await run_cqlengine_benchmark(df, request.operation)
            results.append(cql_result)
        benchmark_results.extend(results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no benchmark: {str(e)}")
    finally:
        current_benchmark = False

async def run_caspyorm_benchmark(df, operation: str) -> BenchmarkResult:
    start_time = psutil.Process(os.getpid()).cpu_times().user
    mem_before = memory_usage_mb()
    benchmark = CaspyORMBenchmark()
    await benchmark.setup_connection()
    try:
        records = benchmark.prepare_data(df)
        if operation in ["insert", "both"]:
            await benchmark.benchmark_insert(records)
        if operation in ["query", "both"]:
            await benchmark.benchmark_query()
        end_time = psutil.Process(os.getpid()).cpu_times().user
        mem_after = memory_usage_mb()
        return BenchmarkResult(
            orm="CaspyORM",
            operation=operation,
            records_processed=len(records),
            time_seconds=end_time - start_time,
            ops_per_second=len(records) / (end_time - start_time) if (end_time - start_time) > 0 else 0,
            memory_mb=mem_after - mem_before,
            timestamp=datetime.now()
        )
    finally:
        await benchmark.cleanup()

def run_cqlengine_benchmark(df, operation: str) -> BenchmarkResult:
    start_time = psutil.Process(os.getpid()).cpu_times().user
    mem_before = memory_usage_mb()
    benchmark = CQLengineBenchmark()
    benchmark.setup_connection()
    try:
        records = benchmark.prepare_data(df)
        if operation in ["insert", "both"]:
            benchmark.benchmark_insert(records)
        if operation in ["query", "both"]:
            benchmark.benchmark_query()
        end_time = psutil.Process(os.getpid()).cpu_times().user
        mem_after = memory_usage_mb()
        return BenchmarkResult(
            orm="CQLengine",
            operation=operation,
            records_processed=len(records),
            time_seconds=end_time - start_time,
            ops_per_second=len(records) / (end_time - start_time) if (end_time - start_time) > 0 else 0,
            memory_mb=mem_after - mem_before,
            timestamp=datetime.now()
        )
    finally:
        benchmark.cleanup()

@app.get("/results", response_model=List[BenchmarkResult])
async def get_results():
    return benchmark_results

@app.get("/compare")
async def compare_orms():
    if not benchmark_results:
        raise HTTPException(status_code=404, detail="Nenhum benchmark executado")
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
    if caspy_results and cql_results:
        caspy_avg_ops = comparison["caspyorm"]["avg_ops_per_second"]
        cql_avg_ops = comparison["cqlengine"]["avg_ops_per_second"]
        comparison["performance_diff"] = {
            "caspyorm_faster": ((caspy_avg_ops / cql_avg_ops) - 1) * 100 if cql_avg_ops > 0 else 0,
            "memory_efficiency": ((comparison["cqlengine"]["avg_memory_mb"] / comparison["caspyorm"]["avg_memory_mb"]) - 1) * 100 if comparison["caspyorm"]["avg_memory_mb"] > 0 else 0
        }
    return comparison

@app.get("/taxis/{vendor_id}")
async def get_taxi_trips(vendor_id: str, limit: int = 10):
    try:
        benchmark = CaspyORMBenchmark()
        await benchmark.setup_connection()
        try:
            results = await benchmark.benchmark_query(vendor_id)
            return {
                "vendor_id": vendor_id,
                "trips_found": len(results),
                "trips": results[:limit]
            }
        finally:
            await benchmark.cleanup()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(e)}")

@app.post("/taxis/bulk")
async def bulk_insert_taxis(trips: List[TaxiTrip]):
    try:
        records = [trip.dict() for trip in trips]
        benchmark = CaspyORMBenchmark()
        await benchmark.setup_connection()
        try:
            await benchmark.benchmark_insert(records)
            return {
                "message": "Viagens inseridas com sucesso",
                "records_inserted": len(records)
            }
        finally:
            await benchmark.cleanup()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na inserção: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando API em http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 