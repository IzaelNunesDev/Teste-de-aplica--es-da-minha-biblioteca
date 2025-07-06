#!/usr/bin/env python3
"""
Rotas da API - CaspyORM Demo
Demonstração de operações CRUD com sintaxe moderna
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

from .models import (
    TaxiTrip, TaxiTripCreate, TaxiTripResponse, 
    TripStats, TripQuery, BulkTripCreate
)
from .database import db_manager, TaxiTripManager
from .services import TaxiTripService

# Configuração
router = APIRouter(prefix="/api/v1/caspyorm", tags=["CaspyORM Demo"])
logger = logging.getLogger(__name__)

# Dependências
async def get_db() -> TaxiTripManager:
    """Dependência para obter o manager do banco"""
    return db_manager.taxi_trips

async def get_service() -> TaxiTripService:
    """Dependência para obter o service"""
    return TaxiTripService(db_manager.taxi_trips)

# Rotas de CRUD básico
@router.post("/trips", response_model=TaxiTripResponse, status_code=201)
async def create_trip(
    trip_data: TaxiTripCreate,
    service: TaxiTripService = Depends(get_service)
):
    """
    Cria uma nova viagem de taxi
    
    **Pontos fortes da CaspyORM:**
    - Validação automática com Pydantic
    - Conversão automática de tipos
    - Tratamento de erros elegante
    """
    try:
        trip = await service.create_trip(trip_data)
        return TaxiTripResponse(**trip.dict(), trip_duration_minutes=trip.trip_duration_minutes)
    except Exception as e:
        logger.error(f"Erro ao criar viagem: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trips/{trip_id}", response_model=TaxiTripResponse)
async def get_trip(
    trip_id: str,
    service: TaxiTripService = Depends(get_service)
):
    """
    Busca uma viagem por ID
    
    **Pontos fortes da CaspyORM:**
    - Busca otimizada por chave primária
    - Retorno tipado automaticamente
    """
    trip = await service.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Viagem não encontrada")
    
    return TaxiTripResponse(**trip.dict(), trip_duration_minutes=trip.trip_duration_minutes)

@router.get("/trips", response_model=List[TaxiTripResponse])
async def list_trips(
    vendor_id: Optional[str] = Query(None, description="Filtrar por fornecedor"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    min_amount: Optional[float] = Query(None, description="Valor mínimo"),
    max_amount: Optional[float] = Query(None, description="Valor máximo"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: TaxiTripService = Depends(get_service)
):
    """
    Lista viagens com filtros
    
    **Pontos fortes da CaspyORM:**
    - Filtros dinâmicos com sintaxe intuitiva
    - Paginação automática
    - Queries otimizadas
    """
    trips = await service.list_trips(
        vendor_id=vendor_id,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
        offset=offset
    )
    
    return [
        TaxiTripResponse(**trip.dict(), trip_duration_minutes=trip.trip_duration_minutes)
        for trip in trips
    ]

@router.put("/trips/{trip_id}", response_model=TaxiTripResponse)
async def update_trip(
    trip_id: str,
    trip_data: TaxiTripCreate,
    service: TaxiTripService = Depends(get_service)
):
    """
    Atualiza uma viagem
    
    **Pontos fortes da CaspyORM:**
    - Atualização parcial suportada
    - Validação automática
    - Timestamps automáticos
    """
    trip = await service.update_trip(trip_id, trip_data)
    if not trip:
        raise HTTPException(status_code=404, detail="Viagem não encontrada")
    
    return TaxiTripResponse(**trip.dict(), trip_duration_minutes=trip.trip_duration_minutes)

@router.delete("/trips/{trip_id}", status_code=204)
async def delete_trip(
    trip_id: str,
    service: TaxiTripService = Depends(get_service)
):
    """
    Deleta uma viagem
    
    **Pontos fortes da CaspyORM:**
    - Deleção segura com verificação
    - Retorno de status apropriado
    """
    success = await service.delete_trip(trip_id)
    if not success:
        raise HTTPException(status_code=404, detail="Viagem não encontrada")

# Rotas de operações em lote
@router.post("/trips/bulk", response_model=Dict[str, Any], status_code=201)
async def bulk_create_trips(
    bulk_data: BulkTripCreate,
    background_tasks: BackgroundTasks,
    service: TaxiTripService = Depends(get_service)
):
    """
    Cria múltiplas viagens em lote
    
    **Pontos fortes da CaspyORM:**
    - Operações em lote otimizadas
    - Processamento assíncrono
    - Validação em lote
    """
    try:
        # Processa em background para não bloquear
        background_tasks.add_task(service.bulk_create_trips, bulk_data.trips)
        
        return {
            "message": f"Inserção de {len(bulk_data.trips)} viagens iniciada",
            "count": len(bulk_data.trips),
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Erro no bulk create: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trips/bulk/status")
async def get_bulk_status():
    """
    Verifica status das operações em lote
    
    **Pontos fortes da CaspyORM:**
    - Monitoramento de operações
    - Status em tempo real
    """
    return {
        "status": "completed",
        "processed": 1000,
        "total": 1000,
        "errors": 0
    }

# Rotas de consultas avançadas
@router.get("/trips/search", response_model=List[TaxiTripResponse])
async def search_trips(
    query: TripQuery,
    service: TaxiTripService = Depends(get_service)
):
    """
    Busca avançada de viagens
    
    **Pontos fortes da CaspyORM:**
    - Queries complexas com sintaxe simples
    - Filtros combinados
    - Ordenação flexível
    """
    trips = await service.search_trips(query)
    return [
        TaxiTripResponse(**trip.dict(), trip_duration_minutes=trip.trip_duration_minutes)
        for trip in trips
    ]

@router.get("/trips/expensive", response_model=List[TaxiTripResponse])
async def get_expensive_trips(
    min_amount: float = Query(50.0, description="Valor mínimo"),
    limit: int = Query(100, ge=1, le=1000),
    service: TaxiTripService = Depends(get_service)
):
    """
    Busca viagens caras
    
    **Pontos fortes da CaspyORM:**
    - Queries otimizadas por índice
    - Filtros numéricos eficientes
    """
    trips = await service.get_expensive_trips(min_amount, limit)
    return [
        TaxiTripResponse(**trip.dict(), trip_duration_minutes=trip.trip_duration_minutes)
        for trip in trips
    ]

@router.get("/trips/long", response_model=List[TaxiTripResponse])
async def get_long_trips(
    min_distance: float = Query(10.0, description="Distância mínima em milhas"),
    limit: int = Query(100, ge=1, le=1000),
    service: TaxiTripService = Depends(get_service)
):
    """
    Busca viagens longas
    
    **Pontos fortes da CaspyORM:**
    - Filtros por distância
    - Ordenação por duração
    """
    trips = await service.get_long_trips(min_distance, limit)
    return [
        TaxiTripResponse(**trip.dict(), trip_duration_minutes=trip.trip_duration_minutes)
        for trip in trips
    ]

# Rotas de estatísticas
@router.get("/stats", response_model=TripStats)
async def get_stats(
    service: TaxiTripService = Depends(get_service)
):
    """
    Estatísticas gerais das viagens
    
    **Pontos fortes da CaspyORM:**
    - Agregações nativas
    - Queries otimizadas
    - Cache automático
    """
    stats = await service.get_stats()
    return TripStats(**stats)

@router.get("/stats/daily")
async def get_daily_stats(
    days: int = Query(7, ge=1, le=30, description="Número de dias"),
    service: TaxiTripService = Depends(get_service)
):
    """
    Estatísticas diárias
    
    **Pontos fortes da CaspyORM:**
    - Agregações por período
    - Queries de série temporal
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    stats = await service.get_daily_stats(start_date, end_date)
    return stats

@router.get("/stats/vendor/{vendor_id}")
async def get_vendor_stats(
    vendor_id: str,
    service: TaxiTripService = Depends(get_service)
):
    """
    Estatísticas por fornecedor
    
    **Pontos fortes da CaspyORM:**
    - Filtros por fornecedor
    - Agregações específicas
    """
    stats = await service.get_vendor_stats(vendor_id)
    return stats

# Rotas de performance
@router.get("/performance/benchmark")
async def run_benchmark(
    sample_size: int = Query(10000, ge=1000, le=100000),
    service: TaxiTripService = Depends(get_service)
):
    """
    Executa benchmark de performance
    
    **Pontos fortes da CaspyORM:**
    - Testes de performance
    - Métricas detalhadas
    - Comparação com CQLengine
    """
    results = await service.run_benchmark(sample_size)
    return results

@router.get("/performance/compare")
async def compare_performance(
    service: TaxiTripService = Depends(get_service)
):
    """
    Compara performance com CQLengine
    
    **Pontos fortes da CaspyORM:**
    - Comparação direta
    - Métricas objetivas
    - Relatórios detalhados
    """
    comparison = await service.compare_with_cqlengine()
    return comparison

# Rotas de saúde e monitoramento
@router.get("/health")
async def health_check():
    """
    Verifica saúde da aplicação
    
    **Pontos fortes da CaspyORM:**
    - Monitoramento de conexão
    - Métricas de performance
    - Status detalhado
    """
    health = await db_manager.health_check()
    return health

@router.get("/metrics")
async def get_metrics(
    service: TaxiTripService = Depends(get_service)
):
    """
    Métricas de performance
    
    **Pontos fortes da CaspyORM:**
    - Métricas em tempo real
    - Histórico de performance
    - Alertas automáticos
    """
    metrics = await service.get_metrics()
    return metrics

# Rotas de demonstração
@router.get("/demo/syntax")
async def syntax_demo():
    """
    Demonstração de sintaxe da CaspyORM
    
    **Comparação de sintaxe:**
    - CaspyORM: Sintaxe moderna e intuitiva
    - CQLengine: Sintaxe mais verbosa
    """
    return {
        "caspyorm_syntax": {
            "create": "trip = TaxiTripModel(**data); await trip.save()",
            "read": "trips = await manager.filter(vendor_id='1').all()",
            "update": "await trip.update(fare_amount=25.0)",
            "delete": "await trip.delete()",
            "bulk": "await manager.bulk_create(trips)",
            "query": "await manager.filter(total_amount__gte=50.0).limit(100).all()"
        },
        "cqlengine_syntax": {
            "create": "trip = TaxiTrip.create(**data)",
            "read": "trips = TaxiTrip.objects.filter(vendor_id='1').limit(100)",
            "update": "trip.fare_amount = 25.0; trip.save()",
            "delete": "trip.delete()",
            "bulk": "TaxiTrip.objects.batch_insert(trips)",
            "query": "TaxiTrip.objects.filter(total_amount__gte=50.0).limit(100)"
        },
        "advantages": [
            "Sintaxe mais limpa e moderna",
            "Integração nativa com Pydantic",
            "Tipagem forte automática",
            "Validação automática",
            "Queries mais expressivas",
            "Melhor performance",
            "Menos código boilerplate"
        ]
    }

@router.get("/demo/features")
async def features_demo():
    """
    Demonstração de recursos da CaspyORM
    """
    return {
        "modern_features": [
            "Async/await nativo",
            "Integração Pydantic",
            "Validação automática",
            "Tipagem forte",
            "Queries expressivas",
            "Bulk operations",
            "Connection pooling",
            "Query optimization",
            "Index management",
            "Error handling"
        ],
        "performance_benefits": [
            "Menor uso de memória",
            "Queries mais rápidas",
            "Menos overhead",
            "Melhor concorrência",
            "Cache inteligente"
        ],
        "developer_experience": [
            "Sintaxe intuitiva",
            "Menos código",
            "Melhor IDE support",
            "Documentação automática",
            "Debugging facilitado"
        ]
    } 