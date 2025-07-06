#!/usr/bin/env python3
"""
Benchmark ULTRA - Versão Otimizada
Implementa todas as otimizações para máximo desempenho
"""

import asyncio
import sys
from pathlib import Path
import time
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark.config import get_data_config, get_benchmark_config, ULTRA_BENCHMARK_CONFIG, DATA_CONFIG
from benchmark.utils import (
    load_and_concat_ultra, convert_chunk_to_models, process_in_chunks_ultra,
    memory_usage_mb, optimized_query_execution, console, save_results,
    display_comparison_table
)
from rich.panel import Panel
from benchmark.core.base_caspy import run_caspy_benchmark
from benchmark.core.base_cqlengine import run_cqlengine_benchmark

async def run_ultra_benchmark():
    """Executa benchmark ULTRA com todas as otimizações"""
    
    console.print(Panel.fit("[bold red]🚀 BENCHMARK ULTRA - VERSÃO OTIMIZADA[/bold red]"))
    console.print("=" * 60)
    
    # Carrega configurações ULTRA
    ultra_config = ULTRA_BENCHMARK_CONFIG
    data_config = DATA_CONFIG
    
    console.print(f"[bold blue]⚙️ Configurações ULTRA:[/bold blue]")
    console.print(f"  📦 Chunk Size: {ultra_config['chunk_size']:,}")
    console.print(f"  🔄 Batch Size: {ultra_config['batch_size']}")
    console.print(f"  🎯 Target Size: {ultra_config['target_size_gb']} GB")
    console.print(f"  📊 Target Records: {data_config['target_records']:,}")
    console.print(f"  🧠 Memory Monitoring: {'✅' if ultra_config['memory_monitoring'] else '❌'}")
    
    # Carrega dados otimizados
    console.print(f"\n[bold green]📊 Carregando dados ULTRA...[/bold green]")
    start_time = time.time()
    mem_before = memory_usage_mb()
    
    try:
        # Tenta carregar múltiplos arquivos primeiro
        df = load_and_concat_ultra(data_config['parquet_files'], ultra_config['target_size_gb'])
    except FileNotFoundError:
        # Fallback para arquivo combinado
        console.print("[yellow]⚠️ Arquivos individuais não encontrados, usando arquivo combinado...[/yellow]")
        from benchmark.utils import load_nyc_taxi_data
        df = load_nyc_taxi_data(data_config['parquet_file'], data_config['target_records'])
    
    # Amostra os dados se necessário
    if len(df) > data_config['target_records']:
        df = df.sample(n=data_config['target_records'], random_state=42)
    
    load_time = time.time() - start_time
    mem_after = memory_usage_mb()
    
    console.print(f"✓ Dados carregados: {len(df):,} registros")
    console.print(f"✓ Tempo de carregamento: {load_time:.2f}s")
    console.print(f"✓ Memória utilizada: {mem_after-mem_before:.1f} MB")
    console.print(f"✓ Memória atual: {mem_after:.1f} MB")
    
    # Executa benchmark CaspyORM ULTRA
    console.print(f"\n[bold green]🚀 Executando Benchmark CaspyORM ULTRA...[/bold green]")
    caspy_results = None
    
    try:
        caspy_start = time.time()
        caspy_results = await run_caspy_benchmark(df)
        caspy_time = time.time() - caspy_start
        
        console.print(f"✅ CaspyORM ULTRA concluído em {caspy_time:.2f}s")
        console.print(f"   📊 Inserção: {caspy_results['insert_ops_per_second']:.0f} ops/s")
        console.print(f"   🔍 Consulta: {caspy_results['query_ops_per_second']:.0f} ops/s")
        console.print(f"   🧠 Memória: {caspy_results['memory_used']:.1f} MB")
        
        # Salva resultados
        save_results(caspy_results, 'caspyorm_ultra')
        
    except Exception as e:
        console.print(f"[red]❌ Erro no CaspyORM ULTRA: {e}[/red]")
        import traceback
        traceback.print_exc()
    
    # Executa benchmark CQLengine ULTRA
    console.print(f"\n[bold green]🚀 Executando Benchmark CQLengine ULTRA...[/bold green]")
    cql_results = None
    
    try:
        cql_start = time.time()
        cql_results = run_cqlengine_benchmark(df)
        cql_time = time.time() - cql_start
        
        console.print(f"✅ CQLengine ULTRA concluído em {cql_time:.2f}s")
        console.print(f"   📊 Inserção: {cql_results['insert_ops_per_second']:.0f} ops/s")
        console.print(f"   🔍 Consulta: {cql_results['query_ops_per_second']:.0f} ops/s")
        console.print(f"   🧠 Memória: {cql_results['memory_used']:.1f} MB")
        
        # Salva resultados
        save_results(cql_results, 'cqlengine_ultra')
        
    except Exception as e:
        console.print(f"[red]❌ Erro no CQLengine ULTRA: {e}[/red]")
        import traceback
        traceback.print_exc()
    
    # Comparação final
    if caspy_results and cql_results:
        console.print(f"\n[bold blue]📊 RESULTADOS ULTRA COMPARATIVOS[/bold blue]")
        console.print("=" * 60)
        
        display_comparison_table(caspy_results, cql_results)
        
        # Salva comparação
        comparison_data = {
            'timestamp': datetime.now().isoformat(),
            'caspyorm': caspy_results,
            'cqlengine': cql_results,
            'ultra_config': ultra_config,
            'dataset_info': {
                'records_processed': len(df),
                'chunk_size': ultra_config['chunk_size'],
                'batch_size': ultra_config['batch_size'],
                'target_size_gb': ultra_config['target_size_gb']
            }
        }
        
        save_results(comparison_data, 'comparison_ultra')
        
    else:
        console.print(f"\n[red]❌ Não foi possível executar ambos os benchmarks ULTRA[/red]")
    
    # Resumo final
    total_time = time.time() - start_time
    final_memory = memory_usage_mb()
    
    console.print(f"\n[bold green]🏁 BENCHMARK ULTRA CONCLUÍDO[/bold green]")
    console.print(f"⏱️ Tempo total: {total_time:.2f}s")
    console.print(f"🧠 Memória final: {final_memory:.1f} MB")
    console.print(f"📊 Registros processados: {len(df):,}")
    
    console.print(f"\n[bold blue]🚀 Otimizações ULTRA aplicadas:[/bold blue]")
    console.print(f"  ✅ Chunks maiores ({ultra_config['chunk_size']:,} registros)")
    console.print(f"  ✅ Batches otimizados ({ultra_config['batch_size']} por batch)")
    console.print(f"  ✅ Pré-processamento eficiente")
    console.print(f"  ✅ Conversão em memória")
    console.print(f"  ✅ Monitoramento de memória em tempo real")
    console.print(f"  ✅ Log progressivo detalhado")
    
    console.print(f"\n[bold green]✅ Benchmark ULTRA finalizado![/bold green]")

if __name__ == "__main__":
    asyncio.run(run_ultra_benchmark()) 