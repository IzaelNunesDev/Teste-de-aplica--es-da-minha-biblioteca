#!/usr/bin/env python3
"""
Modelos CQLengine - Demonstração de Sintaxe Tradicional
"""

from cassandra.cqlengine import columns, models
from cassandra.cqlengine.management import sync_table, drop_table
from cassandra.cqlengine.query import DoesNotExist
from datetime import datetime
import uuid

class TaxiTrip(models.Model):
    """
    Modelo CQLengine para viagens de taxi
    Demonstração de sintaxe tradicional e mais verbosa
    """
    
    # Configuração da tabela
    __keyspace__ = 'taxi_demo'
    __table_name__ = 'taxi_trips_cqlengine'
    
    # Chave primária composta
    trip_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    pickup_date = columns.Date(primary_key=True, partition_key=True)
    
    # Campos de dados
    vendor_id = columns.Text(index=True)
    pickup_datetime = columns.DateTime(index=True)
    dropoff_datetime = columns.DateTime(index=True)
    passenger_count = columns.Integer()
    trip_distance = columns.Float(index=True)
    rate_code_id = columns.Text(index=True)
    store_and_fwd_flag = columns.Text()
    payment_type = columns.Text(index=True)
    
    # Campos monetários
    fare_amount = columns.Float()
    extra = columns.Float()
    mta_tax = columns.Float()
    tip_amount = columns.Float()
    tolls_amount = columns.Float()
    improvement_surcharge = columns.Float()
    total_amount = columns.Float(index=True)
    congestion_surcharge = columns.Float()
    airport_fee = columns.Float()
    
    # Campos opcionais
    pickup_location_id = columns.Integer(required=False)
    dropoff_location_id = columns.Integer(required=False)
    
    # Campos de auditoria
    created_at = columns.DateTime(default=datetime.utcnow)
    updated_at = columns.DateTime(default=datetime.utcnow)
    
    # Métodos customizados
    def trip_duration_minutes(self):
        """Calcula duração da viagem em minutos"""
        if self.pickup_datetime and self.dropoff_datetime:
            duration = self.dropoff_datetime - self.pickup_datetime
            return duration.total_seconds() / 60
        return 0.0
    
    def is_long_trip(self):
        """Verifica se é uma viagem longa (>10 milhas)"""
        return self.trip_distance > 10.0
    
    def is_expensive_trip(self):
        """Verifica se é uma viagem cara (>$50)"""
        return self.total_amount > 50.0
    
    def save(self, *args, **kwargs):
        """Override do save para atualizar timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"TaxiTrip(id={self.trip_id}, vendor={self.vendor_id}, amount=${self.total_amount:.2f})"
    
    def __repr__(self):
        return self.__str__()

# Modelos para estatísticas
class TripStats(models.Model):
    """Modelo para estatísticas de viagens"""
    __keyspace__ = 'taxi_demo'
    __table_name__ = 'trip_stats_cqlengine'
    
    date = columns.Date(primary_key=True)
    vendor_id = columns.Text(primary_key=True)
    total_trips = columns.Integer()
    total_revenue = columns.Float()
    avg_trip_distance = columns.Float()
    avg_trip_duration = columns.Float()
    most_common_payment_type = columns.Text()
    most_common_rate_code = columns.Text()
    total_passengers = columns.Integer()
    created_at = columns.DateTime(default=datetime.utcnow)

# Modelos para performance tracking
class PerformanceMetrics(models.Model):
    """Modelo para métricas de performance"""
    __keyspace__ = 'taxi_demo'
    __table_name__ = 'performance_metrics_cqlengine'
    
    timestamp = columns.DateTime(primary_key=True)
    operation_type = columns.Text(primary_key=True)
    sample_size = columns.Integer()
    duration_ms = columns.Float()
    memory_mb = columns.Float()
    operations_per_second = columns.Float()
    framework = columns.Text()
    created_at = columns.DateTime(default=datetime.utcnow)

# Funções utilitárias para CQLengine
def create_tables():
    """Cria as tabelas necessárias"""
    sync_table(TaxiTrip)
    sync_table(TripStats)
    sync_table(PerformanceMetrics)

def drop_tables():
    """Remove as tabelas"""
    drop_table(TaxiTrip)
    drop_table(TripStats)
    drop_table(PerformanceMetrics)

def get_trip_by_id(trip_id):
    """Busca viagem por ID"""
    try:
        return TaxiTrip.objects.get(trip_id=trip_id)
    except DoesNotExist:
        return None

def get_trips_by_vendor(vendor_id, limit=100):
    """Busca viagens por fornecedor"""
    return TaxiTrip.objects.filter(vendor_id=vendor_id).limit(limit)

def get_trips_by_date_range(start_date, end_date):
    """Busca viagens por período"""
    return TaxiTrip.objects.filter(
        pickup_datetime__gte=start_date,
        pickup_datetime__lte=end_date
    )

def get_expensive_trips(min_amount=50.0, limit=100):
    """Busca viagens caras"""
    return TaxiTrip.objects.filter(total_amount__gte=min_amount).limit(limit)

def get_long_trips(min_distance=10.0, limit=100):
    """Busca viagens longas"""
    return TaxiTrip.objects.filter(trip_distance__gte=min_distance).limit(limit)

def bulk_create_trips(trips_data):
    """Cria múltiplas viagens em lote"""
    trips = []
    for data in trips_data:
        # Adiciona pickup_date para partição
        pickup_datetime = data.get('pickup_datetime')
        if pickup_datetime:
            data['pickup_date'] = pickup_datetime.date()
        
        trip = TaxiTrip(**data)
        trips.append(trip)
    
    # Insere em lote
    TaxiTrip.objects.batch_insert(trips)
    return trips

def update_trip(trip_id, **kwargs):
    """Atualiza uma viagem"""
    try:
        trip = TaxiTrip.objects.get(trip_id=trip_id)
        for key, value in kwargs.items():
            setattr(trip, key, value)
        trip.save()
        return trip
    except DoesNotExist:
        return None

def delete_trip(trip_id):
    """Deleta uma viagem"""
    try:
        trip = TaxiTrip.objects.get(trip_id=trip_id)
        trip.delete()
        return True
    except DoesNotExist:
        return False

def get_stats():
    """Calcula estatísticas das viagens"""
    # Usando queries nativas para performance
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

def get_daily_stats(start_date, end_date):
    """Calcula estatísticas diárias"""
    from cassandra.cqlengine.connection import get_session
    
    session = get_session()
    query = """
    SELECT 
        pickup_date,
        COUNT(*) as trips,
        SUM(total_amount) as revenue,
        AVG(trip_distance) as avg_distance,
        AVG(total_amount) as avg_amount
    FROM taxi_demo.taxi_trips_cqlengine 
    WHERE pickup_date >= %s AND pickup_date <= %s
    GROUP BY pickup_date
    ALLOW FILTERING
    """
    
    result = session.execute(query, [start_date.date(), end_date.date()])
    
    return [
        {
            'date': row.pickup_date.isoformat(),
            'trips': row.trips,
            'revenue': float(row.revenue) if row.revenue else 0.0,
            'avg_distance': float(row.avg_distance) if row.avg_distance else 0.0,
            'avg_amount': float(row.avg_amount) if row.avg_amount else 0.0
        }
        for row in result
    ]

def get_vendor_stats(vendor_id):
    """Calcula estatísticas por fornecedor"""
    from cassandra.cqlengine.connection import get_session
    
    session = get_session()
    query = """
    SELECT 
        COUNT(*) as total_trips,
        SUM(total_amount) as total_revenue,
        AVG(trip_distance) as avg_distance,
        AVG(total_amount) as avg_amount,
        MIN(pickup_datetime) as first_trip,
        MAX(pickup_datetime) as last_trip
    FROM taxi_demo.taxi_trips_cqlengine 
    WHERE vendor_id = %s
    ALLOW FILTERING
    """
    
    result = session.execute(query, [vendor_id]).one()
    
    if result:
        return {
            'vendor_id': vendor_id,
            'total_trips': result.total_trips,
            'total_revenue': float(result.total_revenue) if result.total_revenue else 0.0,
            'avg_distance': float(result.avg_distance) if result.avg_distance else 0.0,
            'avg_amount': float(result.avg_amount) if result.avg_amount else 0.0,
            'first_trip': result.first_trip.isoformat() if result.first_trip else None,
            'last_trip': result.last_trip.isoformat() if result.last_trip else None
        }
    
    return {'vendor_id': vendor_id, 'total_trips': 0} 