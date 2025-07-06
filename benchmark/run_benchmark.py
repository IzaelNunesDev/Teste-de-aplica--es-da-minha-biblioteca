#!/usr/bin/env python3
"""
Script principal para executar benchmark CaspyORM vs CQLengine
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark.config import get_data_config, get_benchmark_config
from benchmark.utils import (
    load_nyc_taxi_data, 
    save_results, 
    display_comparison_table, 
    display_feature_comparison,
    create_summary_panel,
    console
)
from benchmark.core.base_caspy import run_caspy_benchmark
from benchmark.core.base_cqlengine import run_cqlengine_benchmark

async def main():
    """Função principal do benchmark"""
    
    console.print("[bold blue]🏁 BENCHMARK CASPYORM vs CQLENGINE[/bold blue]")
    console.print("=" * 60)
    
    # Carrega configurações
    data_config = get_data_config()
    benchmark_config = get_benchmark_config()
    
    # Verifica se o arquivo de dados existe
    parquet_file = data_config['parquet_file']
    if not os.path.exists(parquet_file):
        console.print(f"[red]❌ Arquivo de dados não encontrado: {parquet_file}[/red]")
        console.print("[yellow]Execute: wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet[/yellow]")
        return
    
    # Carrega dados
    console.print("\n[bold]📊 Carregando dados do NYC Taxi...[/bold]")
    df = load_nyc_taxi_data(parquet_file, benchmark_config['sample_size'])
    
    # Cria diretório de resultados se não existir
    results_dir = Path(data_config['results_dir'])
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Executa benchmark CaspyORM
    console.print("\n[bold green]🚀 Executando Benchmark CaspyORM...[/bold green]")
    try:
        caspy_results = await run_caspy_benchmark(df)
        
        # Salva resultados
        caspy_filename = results_dir / f"caspyorm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_results(caspy_results, str(caspy_filename))
        
    except Exception as e:
        console.print(f"[red]❌ Erro no benchmark CaspyORM: {e}[/red]")
        caspy_results = None
    
    # Executa benchmark CQLengine
    console.print("\n[bold yellow]🚀 Executando Benchmark CQLengine...[/bold yellow]")
    try:
        cql_results = run_cqlengine_benchmark(df)
        
        # Salva resultados
        cql_filename = results_dir / f"cqlengine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_results(cql_results, str(cql_filename))
        
    except Exception as e:
        console.print(f"[red]❌ Erro no benchmark CQLengine: {e}[/red]")
        cql_results = None
    
    # Exibe resultados comparativos
    if caspy_results and cql_results:
        console.print("\n" + "=" * 60)
        console.print("[bold]📊 RESULTADOS COMPARATIVOS[/bold]")
        console.print("=" * 60)
        
        # Tabela de comparação
        display_comparison_table(caspy_results, cql_results)
        
        # Comparação de features
        console.print("\n[bold]🔧 COMPARAÇÃO DE FEATURES[/bold]")
        display_feature_comparison()
        
        # Resumo final
        console.print("\n[bold]🏆 RESUMO FINAL[/bold]")
        create_summary_panel(caspy_results, cql_results)
        
        # Salva comparação
        comparison_results = {
            'timestamp': datetime.now().isoformat(),
            'caspyorm': caspy_results,
            'cqlengine': cql_results,
            'dataset_info': {
                'records_processed': len(df),
                'sample_size': benchmark_config['sample_size'],
                'query_iterations': benchmark_config['query_iterations']
            }
        }
        
        comparison_filename = results_dir / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_results(comparison_results, str(comparison_filename))
        
    else:
        console.print("[red]❌ Não foi possível executar ambos os benchmarks[/red]")
    
    console.print("\n[green]✅ Benchmark concluído![/green]")

if __name__ == "__main__":
    # Executa o benchmark
    asyncio.run(main()) 