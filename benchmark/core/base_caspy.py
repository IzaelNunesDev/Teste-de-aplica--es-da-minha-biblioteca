"""
Benchmark para CaspyORM
"""

import asyncio
import time
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

from caspyorm import Model, fields
from caspyorm.connection import connect_async, disconnect_async, execute_async

from ..config import get_connection_config, get_benchmark_config, get_schema_config
from ..utils import benchmark_timer, console

# Modelo removido - usando queries diretas para compatibilidade

class CaspyORMBenchmark:
    """Classe para executar benchmark com CaspyORM"""
    
    def __init__(self):
        self.config = get_connection_config()
        self.benchmark_config = get_benchmark_config()
        self.db = None
        self.connection = None
        
    async def setup_connection(self):
        """Configura conexão com Cassandra"""
        console.print("[blue]Configurando conexão CaspyORM...[/blue]")
        
        try:
            # Conecta ao Cassandra
            await connect_async(
                contact_points=self.config['hosts'],
                port=self.config['port']
            )
            
            # Cria keyspace se não existir
            await execute_async(f"""
                CREATE KEYSPACE IF NOT EXISTS {self.config['keyspace']}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
            """)
            
            # Usa o keyspace
            await execute_async(f"USE {self.config['keyspace']}")
            
            # Cria tabela se não existir
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self.config['keyspace']}.yellow_taxi_trips (
                vendor_id text,
                pickup_datetime timestamp,
                dropoff_datetime timestamp,
                passenger_count int,
                trip_distance float,
                rate_code_id int,
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
                PRIMARY KEY (vendor_id, pickup_datetime, dropoff_datetime)
            )
            """
            await execute_async(create_table_query)
            
            console.print("[green]✓ Conexão CaspyORM configurada[/green]")
            
        except Exception as e:
            console.print(f"[red]Erro ao configurar CaspyORM: {e}[/red]")
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
    async def benchmark_insert(self, records: List[Dict[str, Any]]) -> List[Any]:
        """Benchmark de inserção com CaspyORM"""
        console.print("[blue]Executando benchmark de inserção CaspyORM...[/blue]")
        
        batch_size = self.benchmark_config['batch_size']
        inserted_records = []
        
        # Inserção em lotes
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # Prepara queries de inserção
            insert_queries = []
            for record in batch:
                query = f"""
                INSERT INTO {self.config['keyspace']}.yellow_taxi_trips (
                    vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
                    trip_distance, rate_code_id, store_and_fwd_flag, payment_type,
                    fare_amount, extra, mta_tax, tip_amount, tolls_amount,
                    improvement_surcharge, total_amount, congestion_surcharge, airport_fee
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    record['vendor_id'], 
                    record['pickup_datetime'].strftime('%Y-%m-%d %H:%M:%S'), 
                    record['dropoff_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                    record['passenger_count'], record['trip_distance'], record['rate_code_id'],
                    record['store_and_fwd_flag'], record['payment_type'], record['fare_amount'],
                    record['extra'], record['mta_tax'], record['tip_amount'], record['tolls_amount'],
                    record['improvement_surcharge'], record['total_amount'], 
                    record['congestion_surcharge'], record['airport_fee']
                )
                insert_queries.append((query, values))
            
            # Executa queries em lote
            for query, values in insert_queries:
                await execute_async(query, values)
                inserted_records.append(record)
        
        return inserted_records
    
    @benchmark_timer
    async def benchmark_query(self, vendor_id: str = "1") -> List[Any]:
        """Benchmark de consulta com CaspyORM"""
        console.print("[blue]Executando benchmark de consulta CaspyORM...[/blue]")
        
        iterations = self.benchmark_config['query_iterations']
        results = []
        
        for _ in range(iterations):
            # Consulta simples por vendor_id
            query = f"SELECT * FROM {self.config['keyspace']}.yellow_taxi_trips WHERE vendor_id = %s LIMIT 10"
            result = await execute_async(query, (vendor_id,))
            results.extend(result)
        
        return results
    
    async def run_benchmark(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Executa benchmark completo com CaspyORM"""
        console.print("[bold blue]🚀 Iniciando Benchmark CaspyORM[/bold blue]")
        
        # Setup
        await self.setup_connection()
        
        # Prepara dados
        records = self.prepare_data(df)
        
        # Benchmark de inserção
        insert_results = await self.benchmark_insert(records)
        
        # Aguarda um pouco para estabilizar
        await asyncio.sleep(1)
        
        # Benchmark de consulta
        query_results = await self.benchmark_query()
        
        # Calcula métricas
        total_time = insert_results['execution_time'] + query_results['execution_time']
        total_memory = insert_results['memory_used'] + query_results['memory_used']
        
        results = {
            'library': 'CaspyORM',
            'insert_ops_per_second': insert_results['operations_per_second'],
            'query_ops_per_second': query_results['operations_per_second'],
            'insert_time': insert_results['execution_time'],
            'query_time': query_results['execution_time'],
            'total_time': total_time,
            'memory_used': total_memory,
            'records_inserted': len(insert_results['result']),
            'queries_executed': self.benchmark_config['query_iterations']
        }
        
        console.print("[green]✓ Benchmark CaspyORM concluído[/green]")
        return results
    
    async def cleanup(self):
        """Limpa recursos"""
        await disconnect_async()

# Função de conveniência para execução
async def run_caspy_benchmark(df: pd.DataFrame) -> Dict[str, Any]:
    """Executa benchmark CaspyORM e retorna resultados"""
    benchmark = CaspyORMBenchmark()
    try:
        results = await benchmark.run_benchmark(df)
        return results
    finally:
        await benchmark.cleanup() 