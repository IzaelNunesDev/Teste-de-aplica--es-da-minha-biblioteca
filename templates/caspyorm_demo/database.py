#!/usr/bin/env python3
"""
Configuração do Banco de Dados - CaspyORM
Demonstração de sintaxe moderna e recursos avançados
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

# CaspyORM imports
from caspyorm.connection import connect_async, disconnect_async
from caspyorm import Model
from caspyorm.fields import Text, Integer, Float, Timestamp, Boolean, UUID
from caspyorm.query import Query

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do Cassandra
CASSANDRA_CONFIG = {
    'hosts': ['localhost'],
    'port': 9042,
    'keyspace': 'taxi_demo',
    'protocol_version': 4,
    'connect_timeout': 10,
    'request_timeout': 30,
    'consistency_level': 'QUORUM',
    'retry_policy': 'DEFAULT',
    'load_balancing_policy': 'DEFAULT',
    'reconnection_policy': 'DEFAULT',
    'compression': True,
    'ssl_options': None,
    'auth_provider': None,
    'execution_profiles': {
        'default': {
            'consistency_level': 'QUORUM',
            'request_timeout': 30,
            'retry_policy': 'DEFAULT',
            'load_balancing_policy': 'DEFAULT',
            'speculative_execution_policy': 'DEFAULT'
        },
        'read': {
            'consistency_level': 'ONE',
            'request_timeout': 15
        },
        'write': {
            'consistency_level': 'QUORUM',
            'request_timeout': 30
        }
    }
}

class TaxiTripModel(Model):
    """
    Modelo CaspyORM para viagens de taxi
    Demonstração de sintaxe moderna e recursos avançados
    """
    
    # Chave primária composta
    __primary_key__ = ['trip_id', 'pickup_date']
    __table_name__ = 'taxi_trips'
    
    # Campos da chave primária
    trip_id: UUID = UUID(primary_key=True, default=uuid.uuid4)
    pickup_date: Timestamp = Timestamp(primary_key=True, partition_key=True)
    
    # Campos de dados
    vendor_id: Text = Text(index=True)
    pickup_datetime: Timestamp = Timestamp(index=True)
    dropoff_datetime: Timestamp = Timestamp(index=True)
    passenger_count: Integer = Integer()
    trip_distance: Float = Float(index=True)
    rate_code_id: Text = Text(index=True)
    store_and_fwd_flag: Text = Text()
    payment_type: Text = Text(index=True)
    
    # Campos monetários
    fare_amount: Float = Float()
    extra: Float = Float()
    mta_tax: Float = Float()
    tip_amount: Float = Float()
    tolls_amount: Float = Float()
    improvement_surcharge: Float = Float()
    total_amount: Float = Float(index=True)
    congestion_surcharge: Float = Float()
    airport_fee: Float = Float()
    
    # Campos opcionais
    pickup_location_id: Optional[Integer] = Integer()
    dropoff_location_id: Optional[Integer] = Integer()
    
    # Campos de auditoria
    created_at: Timestamp = Timestamp(default=datetime.utcnow)
    updated_at: Timestamp = Timestamp(default=datetime.utcnow)
    
    # Campos calculados (não persistidos)
    @property
    def trip_duration_minutes(self) -> float:
        """Calcula duração da viagem em minutos"""
        if self.pickup_datetime and self.dropoff_datetime:
            duration = self.dropoff_datetime - self.pickup_datetime
            return duration.total_seconds() / 60
        return 0.0
    
    @property
    def is_long_trip(self) -> bool:
        """Verifica se é uma viagem longa (>10 milhas)"""
        return self.trip_distance > 10.0
    
    @property
    def is_expensive_trip(self) -> bool:
        """Verifica se é uma viagem cara (>$50)"""
        return self.total_amount > 50.0
    
    def __str__(self) -> str:
        return f"TaxiTrip(id={self.trip_id}, vendor={self.vendor_id}, amount=${self.total_amount:.2f})"
    
    def __repr__(self) -> str:
        return self.__str__()

# Manager customizado com métodos avançados
class TaxiTripManager(Manager[TaxiTripModel]):
    """Manager customizado com métodos de negócio"""
    
    async def find_by_vendor(self, vendor_id: str, limit: int = 100) -> List[TaxiTripModel]:
        """Busca viagens por fornecedor"""
        return await self.filter(vendor_id=vendor_id).limit(limit).all()
    
    async def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TaxiTripModel]:
        """Busca viagens por período"""
        return await self.filter(
            pickup_datetime__gte=start_date,
            pickup_datetime__lte=end_date
        ).all()
    
    async def find_expensive_trips(self, min_amount: float = 50.0) -> List[TaxiTripModel]:
        """Busca viagens caras"""
        return await self.filter(total_amount__gte=min_amount).all()
    
    async def find_long_trips(self, min_distance: float = 10.0) -> List[TaxiTripModel]:
        """Busca viagens longas"""
        return await self.filter(trip_distance__gte=min_distance).all()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Calcula estatísticas das viagens"""
        # Usando queries nativas para performance
        query = """
        SELECT 
            COUNT(*) as total_trips,
            SUM(total_amount) as total_revenue,
            AVG(trip_distance) as avg_distance,
            AVG(total_amount) as avg_amount,
            COUNT(DISTINCT vendor_id) as unique_vendors
        FROM taxi_trips
        """
        
        result = await self.raw(query).first()
        return {
            'total_trips': result['total_trips'] if result else 0,
            'total_revenue': float(result['total_revenue']) if result and result['total_revenue'] else 0.0,
            'avg_distance': float(result['avg_distance']) if result and result['avg_distance'] else 0.0,
            'avg_amount': float(result['avg_amount']) if result and result['avg_amount'] else 0.0,
            'unique_vendors': result['unique_vendors'] if result else 0
        }
    
    async def bulk_create(self, trips_data: List[Dict[str, Any]]) -> List[TaxiTripModel]:
        """Cria múltiplas viagens em lote"""
        trips = []
        for data in trips_data:
            # Adiciona pickup_date para partição
            pickup_datetime = data.get('pickup_datetime')
            if pickup_datetime:
                data['pickup_date'] = pickup_datetime.date()
            
            trip = TaxiTripModel(**data)
            trips.append(trip)
        
        # Insere em lote
        await self.bulk_create(trips)
        return trips
    
    async def update_trip(self, trip_id: str, **kwargs) -> Optional[TaxiTripModel]:
        """Atualiza uma viagem"""
        trip = await self.get(trip_id=trip_id)
        if trip:
            for key, value in kwargs.items():
                setattr(trip, key, value)
            trip.updated_at = datetime.utcnow()
            await trip.save()
        return trip
    
    async def delete_trip(self, trip_id: str) -> bool:
        """Deleta uma viagem"""
        trip = await self.get(trip_id=trip_id)
        if trip:
            await trip.delete()
            return True
        return False

# Configuração da conexão
class DatabaseManager:
    """Gerenciador de conexão com o banco"""
    
    def __init__(self):
        self.connection = None
        self.taxi_trips = TaxiTripManager(TaxiTripModel)
    
    async def connect(self) -> None:
        """Conecta ao Cassandra"""
        try:
            logger.info("Conectando ao Cassandra...")
            self.connection = await connect_async(**CASSANDRA_CONFIG)
            logger.info("Conectado com sucesso!")
            
            # Cria keyspace se não existir
            await self._create_keyspace()
            
            # Cria tabela se não existir
            await self._create_table()
            
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Desconecta do Cassandra"""
        if self.connection:
            await disconnect_async()
            logger.info("Desconectado do Cassandra")
    
    async def _create_keyspace(self) -> None:
        """Cria o keyspace se não existir"""
        create_keyspace_query = """
        CREATE KEYSPACE IF NOT EXISTS taxi_demo
        WITH replication = {
            'class': 'SimpleStrategy',
            'replication_factor': 1
        }
        """
        await self.connection.execute(create_keyspace_query)
        logger.info("Keyspace 'taxi_demo' criado/verificado")
    
    async def _create_table(self) -> None:
        """Cria a tabela se não existir"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS taxi_demo.taxi_trips (
            trip_id uuid,
            pickup_date date,
            vendor_id text,
            pickup_datetime timestamp,
            dropoff_datetime timestamp,
            passenger_count int,
            trip_distance float,
            rate_code_id text,
            store_and_fwd_flag text,
            payment_type text,
            fare_amount float,
            extra float,
            mta_tax float,
            tip_amount float,
            tolls_amount float,
            improvement_surcharge float,
            total_amount float,
            congestion_surcharge float,
            airport_fee float,
            pickup_location_id int,
            dropoff_location_id int,
            created_at timestamp,
            updated_at timestamp,
            PRIMARY KEY ((pickup_date), trip_id)
        ) WITH CLUSTERING ORDER BY (trip_id ASC)
        """
        await self.connection.execute(create_table_query)
        logger.info("Tabela 'taxi_trips' criada/verificada")
        
        # Cria índices secundários
        await self._create_indexes()
    
    async def _create_indexes(self) -> None:
        """Cria índices secundários para consultas eficientes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips (vendor_id)",
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips (payment_type)",
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips (rate_code_id)",
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips (total_amount)",
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips (trip_distance)"
        ]
        
        for index_query in indexes:
            try:
                await self.connection.execute(index_query)
                logger.info(f"Índice criado: {index_query.split('(')[1].split(')')[0]}")
            except Exception as e:
                logger.warning(f"Erro ao criar índice: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde da conexão"""
        try:
            # Testa conexão
            result = await self.connection.execute("SELECT release_version FROM system.local")
            version = result.one()['release_version']
            
            # Testa contagem de registros
            count_result = await self.connection.execute("SELECT COUNT(*) FROM taxi_demo.taxi_trips")
            total_trips = count_result.one()['count']
            
            return {
                'status': 'healthy',
                'cassandra_version': version,
                'total_trips': total_trips,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Instância global
db_manager = DatabaseManager()

# Context manager para conexão
class DatabaseContext:
    """Context manager para gerenciar conexão"""
    
    def __init__(self):
        self.db = db_manager
    
    async def __aenter__(self):
        await self.db.connect()
        return self.db
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db.disconnect()

# Função de inicialização
async def init_database() -> DatabaseManager:
    """Inicializa o banco de dados"""
    await db_manager.connect()
    return db_manager

# Função de cleanup
async def cleanup_database() -> None:
    """Limpa recursos do banco"""
    await db_manager.disconnect() 