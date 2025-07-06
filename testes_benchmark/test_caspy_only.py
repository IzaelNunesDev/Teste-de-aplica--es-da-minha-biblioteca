#!/usr/bin/env python3
"""
Teste apenas da CaspyORM
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from benchmark.config import get_data_config, get_benchmark_config
from benchmark.utils import load_nyc_taxi_data, console
from benchmark.core.base_caspy import run_caspy_benchmark

async def main():
    """Testa apenas a CaspyORM"""
    
    console.print("[bold blue]🧪 TESTE APENAS CASPYORM[/bold blue]")
    
    # Carrega configurações
    data_config = get_data_config()
    benchmark_config = get_benchmark_config()
    
    # Reduz ainda mais para teste rápido
    benchmark_config['sample_size'] = 1000
    benchmark_config['query_iterations'] = 100
    
    # Carrega dados
    console.print("\n[bold]📊 Carregando dados...[/bold]")
    df = load_nyc_taxi_data(data_config['parquet_file'], benchmark_config['sample_size'])
    
    # Executa benchmark CaspyORM
    console.print("\n[bold green]🚀 Executando Benchmark CaspyORM...[/bold green]")
    try:
        caspy_results = await run_caspy_benchmark(df)
        console.print(f"[green]✅ CaspyORM concluído![/green]")
        console.print(f"   📊 Inserção: {caspy_results['insert_ops_per_second']:.0f} ops/s")
        console.print(f"   🔍 Consulta: {caspy_results['query_ops_per_second']:.0f} ops/s")
        console.print(f"   ⏱️ Tempo total: {caspy_results['total_time']:.2f}s")
        console.print(f"   🧠 Memória: {caspy_results['memory_used']:.1f} MB")
        
    except Exception as e:
        console.print(f"[red]❌ Erro no CaspyORM: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 