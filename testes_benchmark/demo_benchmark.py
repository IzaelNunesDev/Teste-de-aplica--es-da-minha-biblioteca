#!/usr/bin/env python3
"""
Demonstração do benchmark CaspyORM vs CQLengine
(Simulação sem necessidade de Cassandra)
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from benchmark.utils import (
    load_nyc_taxi_data, 
    display_comparison_table, 
    display_feature_comparison,
    create_summary_panel,
    console
)
from benchmark.config import get_data_config, get_benchmark_config

def simulate_benchmark_results():
    """Simula resultados de benchmark para demonstração"""
    
    # Resultados simulados baseados em testes reais
    caspy_results = {
        'library': 'CaspyORM',
        'insert_ops_per_second': 842,
        'query_ops_per_second': 19231,
        'insert_time': 59.4,
        'query_time': 0.052,
        'total_time': 59.452,
        'memory_used': 45.2,
        'records_inserted': 50000,
        'queries_executed': 1000
    }
    
    cql_results = {
        'library': 'CQLengine',
        'insert_ops_per_second': 610,
        'query_ops_per_second': 11212,
        'insert_time': 82.0,
        'query_time': 0.089,
        'total_time': 82.089,
        'memory_used': 67.8,
        'records_inserted': 50000,
        'queries_executed': 1000
    }
    
    return caspy_results, cql_results

def demo_data_loading():
    """Demonstra o carregamento de dados"""
    console.print("[bold blue]📊 DEMONSTRAÇÃO: Carregamento de Dados[/bold blue]")
    console.print("=" * 60)
    
    try:
        data_config = get_data_config()
        parquet_file = data_config['parquet_file']
        
        if not Path(parquet_file).exists():
            console.print(f"[red]❌ Arquivo de dados não encontrado: {parquet_file}[/red]")
            return False
        
        # Carrega uma amostra pequena para demonstração
        df = load_nyc_taxi_data(parquet_file, sample_size=1000)
        
        console.print(f"[green]✅ Dados carregados com sucesso![/green]")
        console.print(f"   📊 Registros: {len(df)}")
        console.print(f"   📋 Colunas: {len(df.columns)}")
        console.print(f"   🗓️  Período: {df['pickup_datetime'].min()} a {df['pickup_datetime'].max()}")
        
        # Mostra algumas estatísticas
        console.print(f"\n[bold]📈 Estatísticas dos Dados:[/bold]")
        console.print(f"   💰 Valor médio da corrida: ${df['total_amount'].mean():.2f}")
        console.print(f"   🚗 Distância média: {df['trip_distance'].mean():.2f} milhas")
        console.print(f"   👥 Passageiros médios: {df['passenger_count'].mean():.1f}")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Erro ao carregar dados: {e}[/red]")
        return False

def demo_benchmark_comparison():
    """Demonstra a comparação de benchmark"""
    console.print("\n[bold blue]🏁 DEMONSTRAÇÃO: Resultados do Benchmark[/bold blue]")
    console.print("=" * 60)
    
    # Simula resultados
    caspy_results, cql_results = simulate_benchmark_results()
    
    # Exibe comparação
    display_comparison_table(caspy_results, cql_results)
    
    # Comparação de features
    console.print("\n[bold]🔧 COMPARAÇÃO DE FEATURES[/bold]")
    display_feature_comparison()
    
    # Resumo final
    console.print("\n[bold]🏆 RESUMO FINAL[/bold]")
    create_summary_panel(caspy_results, cql_results)
    
    return caspy_results, cql_results

def demo_code_comparison():
    """Demonstra a diferença de código entre as bibliotecas"""
    console.print("\n[bold blue]💻 DEMONSTRAÇÃO: Comparação de Código[/bold blue]")
    console.print("=" * 60)
    
    console.print("[bold]🔸 CaspyORM - Modelo e Inserção:[/bold]")
    console.print("""
[green]class NYCYellowTaxiTrip(Model):
    vendor_id: str = fields.Text(primary_key=True)
    pickup_datetime: datetime = fields.Timestamp(primary_key=True)
    dropoff_datetime: datetime = fields.Timestamp(clustering_key=True)
    # ... outros campos
    
    class Meta:
        table_name = "yellow_taxi_trips"
        keyspace = "benchmark_nyc_taxi"

# Inserção async
await self.db.bulk_insert(trip_instances)
await self.db.sync_schema()  # Automático![/green]
""")
    
    console.print("\n[bold]🔸 CQLengine - Modelo e Inserção:[/bold]")
    console.print("""
[yellow]class NYCYellowTaxiTripCQL(Model):
    vendor_id = columns.Text(primary_key=True)
    pickup_datetime = columns.DateTime(primary_key=True)
    dropoff_datetime = columns.DateTime(clustering_order="ASC")
    # ... outros campos
    
    class Meta:
        table_name = "yellow_taxi_trips"
        keyspace = "benchmark_nyc_taxi"

# Inserção síncrona
for instance in trip_instances:
    instance.save()
management.sync_table(NYCYellowTaxiTripCQL)  # Manual![/yellow]
""")

def main():
    """Função principal da demonstração"""
    
    console.print("[bold blue]🎯 DEMONSTRAÇÃO: BENCHMARK CASPYORM vs CQLENGINE[/bold blue]")
    console.print("=" * 70)
    console.print("[italic]Esta é uma demonstração que não requer Cassandra rodando[/italic]")
    console.print("=" * 70)
    
    # Demonstra carregamento de dados
    if not demo_data_loading():
        return
    
    # Demonstra comparação de código
    demo_code_comparison()
    
    # Demonstra resultados de benchmark
    caspy_results, cql_results = demo_benchmark_comparison()
    
    # Salva resultados simulados
    results_dir = Path("benchmark/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    demo_results = {
        'timestamp': datetime.now().isoformat(),
        'demo': True,
        'caspyorm': caspy_results,
        'cqlengine': cql_results,
        'note': 'Estes são resultados simulados para demonstração'
    }
    
    demo_filename = results_dir / f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(demo_filename, 'w') as f:
        json.dump(demo_results, f, indent=2, default=str)
    
    console.print(f"\n[green]✅ Demonstração concluída![/green]")
    console.print(f"📁 Resultados salvos em: {demo_filename}")
    
    console.print("\n[bold]🚀 Para executar o benchmark real:[/bold]")
    console.print("   1. Instale e configure Cassandra")
    console.print("   2. Execute: python benchmark/run_benchmark.py")
    
    console.print("\n[bold]📚 Recursos:[/bold]")
    console.print("   📖 README.md - Documentação completa")
    console.print("   🧪 test_setup.py - Teste de configuração")
    console.print("   ⚙️  benchmark/config.py - Configurações")

if __name__ == "__main__":
    main() 