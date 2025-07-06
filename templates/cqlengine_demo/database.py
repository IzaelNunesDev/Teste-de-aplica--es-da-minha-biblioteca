#!/usr/bin/env python3
"""
Configuração do Banco de Dados - CQLengine
Demonstração de sintaxe tradicional e mais verbosa
"""

import logging
from datetime import datetime, timedelta
import time
import psutil
import uuid

# CQLengine imports
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table, drop_table
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

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

class DatabaseManager:
    """
    Gerenciador de conexão com o banco - CQLengine
    Demonstração de sintaxe tradicional
    """
    
    def __init__(self):
        self.cluster = None
        self.session = None
        self.process = psutil.Process()
    
    def connect(self):
        """Conecta ao Cassandra usando CQLengine"""
        try:
            logger.info("Conectando ao Cassandra com CQLengine...")
            
            # Cria cluster
            self.cluster = Cluster(
                contact_points=CASSANDRA_CONFIG['hosts'],
                port=CASSANDRA_CONFIG['port'],
                protocol_version=CASSANDRA_CONFIG['protocol_version'],
                connect_timeout=CASSANDRA_CONFIG['connect_timeout'],
                compression=CASSANDRA_CONFIG['compression']
            )
            
            # Conecta ao cluster
            self.session = self.cluster.connect()
            
            # Configura CQLengine
            connection.setup(
                hosts=CASSANDRA_CONFIG['hosts'],
                default_keyspace=CASSANDRA_CONFIG['keyspace'],
                protocol_version=CASSANDRA_CONFIG['protocol_version']
            )
            
            # Cria keyspace se não existir
            self._create_keyspace()
            
            # Cria tabelas se não existirem
            self._create_tables()
            
            logger.info("Conectado com sucesso usando CQLengine!")
            
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            raise
    
    def disconnect(self):
        """Desconecta do Cassandra"""
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
        logger.info("Desconectado do Cassandra")
    
    def _create_keyspace(self):
        """Cria o keyspace se não existir"""
        create_keyspace_query = """
        CREATE KEYSPACE IF NOT EXISTS taxi_demo
        WITH replication = {
            'class': 'SimpleStrategy',
            'replication_factor': 1
        }
        """
        self.session.execute(create_keyspace_query)
        logger.info("Keyspace 'taxi_demo' criado/verificado")
    
    def _create_tables(self):
        """Cria as tabelas se não existirem"""
        from .models import TaxiTrip, TripStats, PerformanceMetrics
        
        # Sincroniza tabelas
        sync_table(TaxiTrip)
        sync_table(TripStats)
        sync_table(PerformanceMetrics)
        
        logger.info("Tabelas CQLengine criadas/verificadas")
        
        # Cria índices secundários
        self._create_indexes()
    
    def _create_indexes(self):
        """Cria índices secundários para consultas eficientes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips_cqlengine (vendor_id)",
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips_cqlengine (payment_type)",
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips_cqlengine (rate_code_id)",
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips_cqlengine (total_amount)",
            "CREATE INDEX IF NOT EXISTS ON taxi_demo.taxi_trips_cqlengine (trip_distance)"
        ]
        
        for index_query in indexes:
            try:
                self.session.execute(index_query)
                logger.info(f"Índice criado: {index_query.split('(')[1].split(')')[0]}")
            except Exception as e:
                logger.warning(f"Erro ao criar índice: {e}")
    
    def health_check(self):
        """Verifica saúde da conexão"""
        try:
            # Testa conexão
            result = self.session.execute("SELECT release_version FROM system.local")
            version = result.one().release_version
            
            # Testa contagem de registros
            count_result = self.session.execute("SELECT COUNT(*) FROM taxi_demo.taxi_trips_cqlengine")
            total_trips = count_result.one().count
            
            return {
                'status': 'healthy',
                'cassandra_version': version,
                'total_trips': total_trips,
                'framework': 'CQLengine',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'framework': 'CQLengine',
                'timestamp': datetime.utcnow().isoformat()
            }

# Manager customizado para CQLengine
class TaxiTripManager:
    """Manager customizado para CQLengine com métodos de negócio"""
    
    def __init__(self):
        from .models import TaxiTrip
        self.model = TaxiTrip
    
    def find_by_vendor(self, vendor_id, limit=100):
        """Busca viagens por fornecedor"""
        return self.model.objects.filter(vendor_id=vendor_id).limit(limit)
    
    def find_by_date_range(self, start_date, end_date):
        """Busca viagens por período"""
        return self.model.objects.filter(
            pickup_datetime__gte=start_date,
            pickup_datetime__lte=end_date
        )
    
    def find_expensive_trips(self, min_amount=50.0):
        """Busca viagens caras"""
        return self.model.objects.filter(total_amount__gte=min_amount)
    
    def find_long_trips(self, min_distance=10.0):
        """Busca viagens longas"""
        return self.model.objects.filter(trip_distance__gte=min_distance)
    
    def get_stats(self):
        """Calcula estatísticas das viagens"""
        from cassandra.cqlengine.connection import get_session
        
        session = get_session()
        query = """
        SELECT 
            COUNT(*) as total_trips,
            SUM(total_amount) as total_revenue,
            AVG(trip_distance) as avg_distance,
            AVG(total_amount) as avg_amount,
            COUNT(DISTINCT vendor_id) as unique_vendors
        FROM taxi_demo.taxi_trips_cqlengine
        """
        
        result = session.execute(query).one()
        return {
            'total_trips': result.total_trips if result else 0,
            'total_revenue': float(result.total_revenue) if result and result.total_revenue else 0.0,
            'avg_distance': float(result.avg_distance) if result and result.avg_distance else 0.0,
            'avg_amount': float(result.avg_amount) if result and result.avg_amount else 0.0,
            'unique_vendors': result.unique_vendors if result else 0
        }
    
    def bulk_create(self, trips_data):
        """Cria múltiplas viagens em lote"""
        trips = []
        for data in trips_data:
            # Adiciona pickup_date para partição
            pickup_datetime = data.get('pickup_datetime')
            if pickup_datetime:
                data['pickup_date'] = pickup_datetime.date()
            
            trip = self.model(**data)
            trips.append(trip)
        
        # Insere em lote
        self.model.objects.batch_insert(trips)
        return trips
    
    def update_trip(self, trip_id, **kwargs):
        """Atualiza uma viagem"""
        try:
            trip = self.model.objects.get(trip_id=trip_id)
            for key, value in kwargs.items():
                setattr(trip, key, value)
            trip.save()
            return trip
        except DoesNotExist:
            return None
    
    def delete_trip(self, trip_id):
        """Deleta uma viagem"""
        try:
            trip = self.model.objects.get(trip_id=trip_id)
            trip.delete()
            return True
        except DoesNotExist:
            return False

# Context manager para conexão
class DatabaseContext:
    """Context manager para gerenciar conexão CQLengine"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def __enter__(self):
        self.db.connect()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()

# Instância global
db_manager = DatabaseManager()

# Função de inicialização
def init_database():
    """Inicializa o banco de dados CQLengine"""
    db_manager.connect()
    return db_manager

# Função de cleanup
def cleanup_database():
    """Limpa recursos do banco CQLengine"""
    db_manager.disconnect()

# Funções utilitárias para performance
def run_benchmark(sample_size=10000):
    """Executa benchmark de performance CQLengine"""
    try:
        start_time = time.time()
        start_memory = db_manager.process.memory_info().rss / 1024 / 1024  # MB
        
        from .models import TaxiTrip
        
        # Teste de inserção
        insert_start = time.time()
        trips = []
        for i in range(sample_size):
            trip_data = {
                'vendor_id': '1',
                'pickup_datetime': datetime.utcnow() + timedelta(minutes=i),
                'dropoff_datetime': datetime.utcnow() + timedelta(minutes=i+30),
                'passenger_count': 2,
                'trip_distance': 5.5,
                'rate_code_id': '1',
                'store_and_fwd_flag': 'N',
                'payment_type': '1',
                'fare_amount': 15.50,
                'total_amount': 21.0
            }
            trips.append(TaxiTrip(**trip_data))
        
        TaxiTrip.objects.batch_insert(trips)
        insert_time = time.time() - insert_start
        
        # Teste de leitura
        read_start = time.time()
        read_trips = list(TaxiTrip.objects.filter(vendor_id='1').limit(sample_size))
        read_time = time.time() - read_start
        
        end_time = time.time()
        end_memory = db_manager.process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'sample_size': sample_size,
            'total_time': end_time - start_time,
            'insert_time': insert_time,
            'read_time': read_time,
            'memory_usage': end_memory - start_memory,
            'inserts_per_second': sample_size / insert_time if insert_time > 0 else 0,
            'reads_per_second': sample_size / read_time if read_time > 0 else 0,
            'framework': 'CQLengine'
        }
        
    except Exception as e:
        logger.error(f"Erro no benchmark CQLengine: {e}")
        return {'error': str(e)}

def get_metrics():
    """Métricas de performance CQLengine em tempo real"""
    try:
        current_memory = db_manager.process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = db_manager.process.cpu_percent()
        
        # Conta registros
        from .models import TaxiTrip
        total_trips = TaxiTrip.objects.count()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'memory_usage_mb': current_memory,
            'cpu_percent': cpu_percent,
            'total_trips': total_trips,
            'active_connections': 1,  # Simplificado
            'framework': 'CQLengine',
            'status': 'healthy'
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas CQLengine: {e}")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'framework': 'CQLengine',
            'status': 'error',
            'error': str(e)
        } 