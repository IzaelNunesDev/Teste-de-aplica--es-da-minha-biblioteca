#!/usr/bin/env python3
"""
Teste apenas do CQLengine ULTRA
"""

import sys
from pathlib import Path
import time

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from benchmark.config import DATA_CONFIG, ULTRA_BENCHMARK_CONFIG
from benchmark.utils import load_and_concat_ultra, memory_usage_mb, console
from benchmark.core.base_cqlengine import run_cqlengine_benchmark

def main():
    """Testa apenas o CQLengine ULTRA"""
    
    console.print("[bold blue]🧪 TESTE APENAS CQLENGINE ULTRA[/bold blue]")
    
    # Carrega configurações ULTRA
    ultra_config = ULTRA_BENCHMARK_CONFIG
    data_config = DATA_CONFIG
    
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
    
    # Executa benchmark CQLengine ULTRA
    console.print(f"\n[bold green]🚀 Executando Benchmark CQLengine ULTRA...[/bold green]")
    
    try:
        cql_start = time.time()
        cql_results = run_cqlengine_benchmark(df)
        cql_time = time.time() - cql_start
        
        console.print(f"✅ CQLengine ULTRA concluído em {cql_time:.2f}s")
        console.print(f"   📊 Inserção: {cql_results['insert_ops_per_second']:.0f} ops/s")
        console.print(f"   🔍 Consulta: {cql_results['query_ops_per_second']:.0f} ops/s")
        console.print(f"   🧠 Memória: {cql_results['memory_used']:.1f} MB")
        
        # Salva resultados
        from benchmark.utils import save_results
        save_results(cql_results, 'cqlengine_ultra')
        
    except Exception as e:
        console.print(f"[red]❌ Erro no CQLengine ULTRA: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 