"""
Benchmark para CQLengine
"""

import time
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns, connection, management
from cassandra.cqlengine.connection import get_session

from ..config import get_connection_config, get_benchmark_config, get_schema_config
from ..utils import benchmark_timer, console

class NYCYellowTaxiTripCQL(Model):
    """Modelo para dados do NYC Yellow Taxi usando CQLengine"""
    
    vendor_id = columns.Text(primary_key=True)
    pickup_datetime = columns.DateTime(primary_key=True)
    dropoff_datetime = columns.DateTime(primary_key=True)
    passenger_count = columns.Integer()
    trip_distance = columns.Float()
    rate_code_id = columns.Integer()
    store_and_fwd_flag = columns.Text()
    payment_type = columns.Text()
    fare_amount = columns.Float()
    extra = columns.Float()
    mta_tax = columns.Float()
    tip_amount = columns.Float()
    tolls_amount = columns.Float()
    improvement_surcharge = columns.Float()
    total_amount = columns.Float()
    congestion_surcharge = columns.Float()
    airport_fee = columns.Float()
    
    class Meta:
        table_name = "yellow_taxi_trips"
        keyspace = "benchmark_nyc_taxi"

class CQLengineBenchmark:
    """Classe para executar benchmark com CQLengine"""
    
    def __init__(self):
        self.config = get_connection_config()
        self.benchmark_config = get_benchmark_config()
        self.session = None
        
    def setup_connection(self):
        """Configura conexão com Cassandra"""
        console.print("[blue]Configurando conexão CQLengine...[/blue]")
        
        try:
            # Configura conexão
            connection.setup(
                hosts=self.config['hosts'],
                port=self.config['port'],
                default_keyspace=self.config['keyspace']
            )
            
            # Obtém sessão
            self.session = get_session()
            
            # Cria keyspace se não existir
            self.session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {self.config['keyspace']}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
            """)
            
            # Sincroniza schema (MANUAL com CQLengine!)
            management.sync_table(NYCYellowTaxiTripCQL)
            
            console.print("[green]✓ Conexão CQLengine configurada[/green]")
            
        except Exception as e:
            console.print(f"[red]Erro ao configurar CQLengine: {e}[/red]")
            raise
    
    def prepare_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepara dados do DataFrame para inserção"""
        records = []
        
        # Mapeamento de colunas do dataset NYC Taxi
        column_mapping = {
            'VendorID': 'vendor_id',
            'tpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime',
            'passenger_count': 'passenger_count',
            'trip_distance': 'trip_distance',
            'RatecodeID': 'rate_code_id',
            'store_and_fwd_flag': 'store_and_fwd_flag',
            'payment_type': 'payment_type',
            'fare_amount': 'fare_amount',
            'extra': 'extra',
            'mta_tax': 'mta_tax',
            'tip_amount': 'tip_amount',
            'tolls_amount': 'tolls_amount',
            'improvement_surcharge': 'improvement_surcharge',
            'total_amount': 'total_amount',
            'congestion_surcharge': 'congestion_surcharge',
            'Airport_fee': 'airport_fee'
        }
        
        for _, row in df.iterrows():
            record = {}
            
            # Mapeia as colunas corretamente
            for source_col, target_col in column_mapping.items():
                if source_col in row.index:
                    value = row[source_col]
                    
                    # Tratamento especial para tipos de dados
                    if pd.isna(value):
                        if target_col in ['passenger_count', 'rate_code_id']:
                            value = 1
                        elif target_col in ['trip_distance', 'fare_amount', 'extra', 'mta_tax', 
                                          'tip_amount', 'tolls_amount', 'improvement_surcharge', 
                                          'total_amount', 'congestion_surcharge', 'airport_fee']:
                            value = 0.0
                        else:
                            value = None
                    else:
                        # Converte tipos
                        if target_col == 'vendor_id':
                            value = str(value)
                        elif target_col in ['passenger_count', 'rate_code_id']:
                            value = int(value)
                        elif target_col in ['trip_distance', 'fare_amount', 'extra', 'mta_tax', 
                                          'tip_amount', 'tolls_amount', 'improvement_surcharge', 
                                          'total_amount', 'congestion_surcharge', 'airport_fee']:
                            value = float(value)
                        elif target_col in ['store_and_fwd_flag', 'payment_type']:
                            value = str(value)
                        elif 'datetime' in target_col:
                            value = pd.to_datetime(value)
                    
                    record[target_col] = value
                else:
                    # Valor padrão se coluna não existir
                    if target_col in ['passenger_count', 'rate_code_id']:
                        record[target_col] = 1
                    elif target_col in ['trip_distance', 'fare_amount', 'extra', 'mta_tax', 
                                      'tip_amount', 'tolls_amount', 'improvement_surcharge', 
                                      'total_amount', 'congestion_surcharge', 'airport_fee']:
                        record[target_col] = 0.0
                    else:
                        record[target_col] = None
            
            records.append(record)
        
        return records
    
    @benchmark_timer
    def benchmark_insert(self, records: List[Dict[str, Any]]) -> List[Any]:
        """Benchmark de inserção com CQLengine"""
        console.print("[blue]Executando benchmark de inserção CQLengine...[/blue]")
        
        batch_size = self.benchmark_config['batch_size']
        inserted_records = []
        
        # Inserção em lotes (síncrono)
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # Cria instâncias do modelo
            trip_instances = [NYCYellowTaxiTripCQL(**record) for record in batch]
            
            # Insere em lote (síncrono)
            for instance in trip_instances:
                instance.save()
                inserted_records.append(instance)
        
        return inserted_records
    
    @benchmark_timer
    def benchmark_query(self, vendor_id: str = "1") -> List[Any]:
        """Benchmark de consulta com CQLengine"""
        console.print("[blue]Executando benchmark de consulta CQLengine...[/blue]")
        
        iterations = self.benchmark_config['query_iterations']
        results = []
        
        for _ in range(iterations):
            # Consulta simples por vendor_id (síncrona)
            query_results = NYCYellowTaxiTripCQL.filter(vendor_id=vendor_id).limit(10)
            results.extend(list(query_results))
        
        return results
    
    def run_benchmark(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Executa benchmark completo com CQLengine"""
        console.print("[bold blue]🚀 Iniciando Benchmark CQLengine[/bold blue]")
        
        # Setup
        self.setup_connection()
        
        # Prepara dados
        records = self.prepare_data(df)
        
        # Benchmark de inserção
        insert_results = self.benchmark_insert(records)
        
        # Aguarda um pouco para estabilizar
        time.sleep(1)
        
        # Benchmark de consulta
        query_results = self.benchmark_query()
        
        # Calcula métricas
        total_time = insert_results['execution_time'] + query_results['execution_time']
        total_memory = insert_results['memory_used'] + query_results['memory_used']
        
        results = {
            'library': 'CQLengine',
            'insert_ops_per_second': insert_results['operations_per_second'],
            'query_ops_per_second': query_results['operations_per_second'],
            'insert_time': insert_results['execution_time'],
            'query_time': query_results['execution_time'],
            'total_time': total_time,
            'memory_used': total_memory,
            'records_inserted': len(insert_results['result']),
            'queries_executed': self.benchmark_config['query_iterations']
        }
        
        console.print("[green]✓ Benchmark CQLengine concluído[/green]")
        return results
    
    def cleanup(self):
        """Limpa recursos"""
        if self.session:
            self.session.shutdown()

# Função de conveniência para execução
def run_cqlengine_benchmark(df: pd.DataFrame) -> Dict[str, Any]:
    """Executa benchmark CQLengine e retorna resultados"""
    benchmark = CQLengineBenchmark()
    try:
        results = benchmark.run_benchmark(df)
        return results
    finally:
        benchmark.cleanup() 