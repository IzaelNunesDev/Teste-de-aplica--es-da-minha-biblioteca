#!/usr/bin/env python3
"""
Modelos CaspyORM - Demonstração de Sintaxe Moderna
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums para validação
class PaymentType(str, Enum):
    CASH = "1"
    CREDIT = "2"
    DEBIT = "3"
    UNKNOWN = "4"

class RateCode(str, Enum):
    STANDARD = "1"
    JFK = "2"
    NEWARK = "3"
    NASSAU = "4"
    NEGOTIATED = "5"
    GROUP_RIDE = "6"

# Modelo principal com validações avançadas
class TaxiTrip(BaseModel):
    """Modelo de viagem de taxi com validações CaspyORM"""
    
    # Campos obrigatórios com validações
    vendor_id: str = Field(..., description="ID do fornecedor", min_length=1, max_length=10)
    pickup_datetime: datetime = Field(..., description="Data/hora de embarque")
    dropoff_datetime: datetime = Field(..., description="Data/hora de desembarque")
    
    # Campos numéricos com validações
    passenger_count: int = Field(..., ge=0, le=10, description="Número de passageiros")
    trip_distance: float = Field(..., ge=0.0, le=1000.0, description="Distância da viagem em milhas")
    rate_code_id: RateCode = Field(..., description="Código da tarifa")
    
    # Campos de texto
    store_and_fwd_flag: str = Field(..., max_length=1, description="Flag de armazenamento")
    payment_type: PaymentType = Field(..., description="Tipo de pagamento")
    
    # Campos monetários
    fare_amount: float = Field(..., ge=0.0, description="Valor da tarifa")
    extra: float = Field(0.0, ge=0.0, description="Taxa extra")
    mta_tax: float = Field(0.0, ge=0.0, description="Imposto MTA")
    tip_amount: float = Field(0.0, ge=0.0, description="Gorjeta")
    tolls_amount: float = Field(0.0, ge=0.0, description="Pedágios")
    improvement_surcharge: float = Field(0.0, ge=0.0, description="Taxa de melhoria")
    total_amount: float = Field(..., ge=0.0, description="Valor total")
    congestion_surcharge: float = Field(0.0, ge=0.0, description="Taxa de congestionamento")
    airport_fee: float = Field(0.0, ge=0.0, description="Taxa de aeroporto")
    
    # Campos opcionais
    pickup_location_id: Optional[int] = Field(None, ge=1, description="ID da localização de embarque")
    dropoff_location_id: Optional[int] = Field(None, ge=1, description="ID da localização de desembarque")
    
    # Validações customizadas
    @validator('dropoff_datetime')
    def dropoff_after_pickup(cls, v, values):
        """Valida se o desembarque é após o embarque"""
        if 'pickup_datetime' in values and v <= values['pickup_datetime']:
            raise ValueError('dropoff_datetime deve ser posterior ao pickup_datetime')
        return v
    
    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        """Valida se o total está correto"""
        if 'fare_amount' in values:
            expected_total = (
                values.get('fare_amount', 0) +
                values.get('extra', 0) +
                values.get('mta_tax', 0) +
                values.get('tip_amount', 0) +
                values.get('tolls_amount', 0) +
                values.get('improvement_surcharge', 0) +
                values.get('congestion_surcharge', 0) +
                values.get('airport_fee', 0)
            )
            if abs(v - expected_total) > 0.01:  # Tolerância de 1 centavo
                raise ValueError(f'Total amount deve ser {expected_total:.2f}, recebido {v:.2f}')
        return v
    
    class Config:
        """Configurações do modelo"""
        # Exemplo de uso
        schema_extra = {
            "example": {
                "vendor_id": "1",
                "pickup_datetime": "2024-01-01T12:00:00",
                "dropoff_datetime": "2024-01-01T12:30:00",
                "passenger_count": 2,
                "trip_distance": 5.5,
                "rate_code_id": "1",
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
        }

# Modelo para criação (sem campos calculados)
class TaxiTripCreate(BaseModel):
    """Modelo para criação de viagem (sem validações de total)"""
    vendor_id: str = Field(..., description="ID do fornecedor")
    pickup_datetime: datetime = Field(..., description="Data/hora de embarque")
    dropoff_datetime: datetime = Field(..., description="Data/hora de desembarque")
    passenger_count: int = Field(..., ge=0, le=10)
    trip_distance: float = Field(..., ge=0.0)
    rate_code_id: RateCode = Field(...)
    store_and_fwd_flag: str = Field(..., max_length=1)
    payment_type: PaymentType = Field(...)
    fare_amount: float = Field(..., ge=0.0)
    extra: float = Field(0.0, ge=0.0)
    mta_tax: float = Field(0.0, ge=0.0)
    tip_amount: float = Field(0.0, ge=0.0)
    tolls_amount: float = Field(0.0, ge=0.0)
    improvement_surcharge: float = Field(0.0, ge=0.0)
    total_amount: float = Field(..., ge=0.0)
    congestion_surcharge: float = Field(0.0, ge=0.0)
    airport_fee: float = Field(0.0, ge=0.0)
    pickup_location_id: Optional[int] = Field(None, ge=1)
    dropoff_location_id: Optional[int] = Field(None, ge=1)

# Modelo para resposta
class TaxiTripResponse(BaseModel):
    """Modelo de resposta com campos calculados"""
    id: str  # ID único da viagem
    vendor_id: str
    pickup_datetime: datetime
    dropoff_datetime: datetime
    passenger_count: int
    trip_distance: float
    rate_code_id: str
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
    pickup_location_id: Optional[int]
    dropoff_location_id: Optional[int]
    trip_duration_minutes: float  # Campo calculado
    created_at: datetime
    updated_at: datetime

# Modelo para estatísticas
class TripStats(BaseModel):
    """Estatísticas de viagens"""
    total_trips: int
    total_revenue: float
    avg_trip_distance: float
    avg_trip_duration: float
    most_common_payment_type: str
    most_common_rate_code: str
    total_passengers: int

# Modelo para consultas
class TripQuery(BaseModel):
    """Parâmetros de consulta"""
    vendor_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_distance: Optional[float] = None
    max_distance: Optional[float] = None
    payment_type: Optional[PaymentType] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

# Modelo para bulk operations
class BulkTripCreate(BaseModel):
    """Modelo para inserção em lote"""
    trips: List[TaxiTripCreate] = Field(..., min_length=1, max_length=1000)
    
    @validator('trips')
    def validate_trips(cls, v):
        """Valida lista de viagens"""
        if len(v) > 1000:
            raise ValueError('Máximo de 1000 viagens por operação em lote')
        return v 