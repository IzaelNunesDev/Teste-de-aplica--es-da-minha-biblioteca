"""
Utilitários para o benchmark CaspyORM vs CQLengine
"""

import time
import json
import psutil
import pandas as pd
import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
import os
from functools import wraps

console = Console()

def load_nyc_taxi_data(parquet_file: str, sample_size: int = 50000) -> pd.DataFrame:
    """
    Carrega dados do arquivo parquet do NYC Taxi
    """
    console.print(f"[blue]Carregando dados de {parquet_file}...[/blue]")
    
    try:
        # Lê o arquivo parquet
        df = pd.read_parquet(parquet_file)
        
        # Seleciona uma amostra
        if len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42)
        
        # Mapeia nomes das colunas
        column_mapping = {
            'VendorID': 'vendor_id',
            'tpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime',
            'RatecodeID': 'rate_code_id',
            'Airport_fee': 'airport_fee'
        }
        
        # Renomeia colunas
        df = df.rename(columns=column_mapping)
        
        # Limpa e prepara os dados
        df = df.dropna(subset=['vendor_id', 'pickup_datetime', 'dropoff_datetime'])
        
        # Converte tipos de dados
        df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
        df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])
        df['vendor_id'] = df['vendor_id'].astype(str)
        
        console.print(f"[green]✓ Dados carregados: {len(df)} registros[/green]")
        return df
        
    except Exception as e:
        console.print(f"[red]Erro ao carregar dados: {e}[/red]")
        raise

def measure_memory_usage() -> float:
    """
    Mede o uso de memória atual do processo
    """
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # MB

def benchmark_timer(func):
    """
    Decorator para medir tempo de execução de funções
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = measure_memory_usage()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = measure_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        return {
            'result': result,
            'execution_time': execution_time,
            'memory_used': memory_used,
            'operations_per_second': len(result) / execution_time if result else 0
        }
    
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = measure_memory_usage()
        
        result = await func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = measure_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        return {
            'result': result,
            'execution_time': execution_time,
            'memory_used': memory_used,
            'operations_per_second': len(result) / execution_time if result else 0
        }
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper

def save_results(results: Dict[str, Any], filename: str):
    """
    Salva resultados do benchmark em arquivo JSON
    """
    results['timestamp'] = datetime.now().isoformat()
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    console.print(f"[green]✓ Resultados salvos em {filename}[/green]")

def display_comparison_table(caspy_results: Dict[str, Any], cql_results: Dict[str, Any]):
    """
    Exibe tabela comparativa dos resultados
    """
    table = Table(title="📊 Comparação CaspyORM vs CQLengine")
    
    table.add_column("Métrica", style="cyan", no_wrap=True)
    table.add_column("CaspyORM", style="green")
    table.add_column("CQLengine", style="yellow")
    table.add_column("Diferença", style="magenta")
    
    # Inserção
    caspy_insert_ops = caspy_results.get('insert_ops_per_second', 0)
    cql_insert_ops = cql_results.get('insert_ops_per_second', 0)
    insert_diff = ((caspy_insert_ops - cql_insert_ops) / cql_insert_ops * 100) if cql_insert_ops > 0 else 0
    
    table.add_row(
        "🚀 Inserção (ops/s)",
        f"{caspy_insert_ops:.0f}",
        f"{cql_insert_ops:.0f}",
        f"{insert_diff:+.1f}%"
    )
    
    # Consulta
    caspy_query_ops = caspy_results.get('query_ops_per_second', 0)
    cql_query_ops = cql_results.get('query_ops_per_second', 0)
    query_diff = ((caspy_query_ops - cql_query_ops) / cql_query_ops * 100) if cql_query_ops > 0 else 0
    
    table.add_row(
        "🔍 Consulta (ops/s)",
        f"{caspy_query_ops:.0f}",
        f"{cql_query_ops:.0f}",
        f"{query_diff:+.1f}%"
    )
    
    # Memória
    caspy_memory = caspy_results.get('memory_used', 0)
    cql_memory = cql_results.get('memory_used', 0)
    memory_diff = ((cql_memory - caspy_memory) / cql_memory * 100) if cql_memory > 0 else 0
    
    table.add_row(
        "🧠 Memória (MB)",
        f"{caspy_memory:.1f}",
        f"{cql_memory:.1f}",
        f"{memory_diff:+.1f}%"
    )
    
    # Tempo total
    caspy_total_time = caspy_results.get('total_time', 0)
    cql_total_time = cql_results.get('total_time', 0)
    time_diff = ((cql_total_time - caspy_total_time) / cql_total_time * 100) if cql_total_time > 0 else 0
    
    table.add_row(
        "⏱️ Tempo Total (s)",
        f"{caspy_total_time:.2f}",
        f"{cql_total_time:.2f}",
        f"{time_diff:+.1f}%"
    )
    
    console.print(table)

def display_feature_comparison():
    """
    Exibe comparação de features entre as bibliotecas
    """
    table = Table(title="🔧 Comparação de Features")
    
    table.add_column("Feature", style="cyan", no_wrap=True)
    table.add_column("CaspyORM", style="green")
    table.add_column("CQLengine", style="yellow")
    
    features = [
        ("⚙️ Suporte Async", "✅ Presente", "❌ Ausente"),
        ("🔧 Schema Sync", "✅ Automático", "❌ Manual"),
        ("📦 Integração Pydantic", "✅ Nativa", "❌ Ausente"),
        ("🚀 CLI Tools", "✅ Presente", "❌ Ausente"),
        ("🔍 Validação Automática", "✅ Presente", "❌ Manual"),
        ("📝 Type Hints", "✅ Completo", "⚠️ Parcial")
    ]
    
    for feature, caspy, cql in features:
        table.add_row(feature, caspy, cql)
    
    console.print(table)

def create_summary_panel(caspy_results: Dict[str, Any], cql_results: Dict[str, Any]):
    """
    Cria painel resumo dos resultados
    """
    caspy_faster_insert = caspy_results.get('insert_ops_per_second', 0) > cql_results.get('insert_ops_per_second', 0)
    caspy_faster_query = caspy_results.get('query_ops_per_second', 0) > cql_results.get('query_ops_per_second', 0)
    
    summary = f"""
    🏆 [bold]RESULTADO FINAL[/bold]
    
    🚀 [bold]Inserção:[/bold] {'CaspyORM mais rápido' if caspy_faster_insert else 'CQLengine mais rápido'}
    🔍 [bold]Consulta:[/bold] {'CaspyORM mais rápido' if caspy_faster_query else 'CQLengine mais rápido'}
    
    💡 [bold]Vencedor Geral:[/bold] {'CaspyORM' if (caspy_faster_insert and caspy_faster_query) else 'CQLengine' if (not caspy_faster_insert and not caspy_faster_query) else 'Empate'}
    """
    
    panel = Panel(summary, title="📊 Resumo do Benchmark", border_style="blue")
    console.print(panel)

def memory_usage_mb() -> float:
    """Monitora uso de memória em tempo real"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def load_and_concat_ultra(files: List[str], target_gb: float = 0.5) -> pd.DataFrame:
    """
    Carrega e concatena múltiplos arquivos parquet de forma otimizada
    """
    console.print(f"[bold blue]📊 Carregando {len(files)} arquivos parquet...[/bold blue]")
    
    dfs = []
    total_size = 0
    
    for file in files:
        if os.path.exists(file):
            console.print(f"  📁 Carregando {file}...")
            df = pd.read_parquet(file)
            dfs.append(df)
            total_size += len(df)
            console.print(f"    ✓ {len(df):,} registros carregados")
        else:
            console.print(f"  ⚠️ Arquivo não encontrado: {file}")
    
    if not dfs:
        raise FileNotFoundError("Nenhum arquivo parquet encontrado")
    
    # Concatena todos os DataFrames
    console.print(f"[bold green]🔄 Concatenando {len(dfs)} DataFrames...[/bold green]")
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Calcula tamanho em GB
    size_gb = combined_df.memory_usage(deep=True).sum() / 1024 / 1024 / 1024
    
    console.print(f"✓ Dataset combinado: {len(combined_df):,} registros ({size_gb:.2f} GB)")
    console.print(f"✓ Memória atual: {memory_usage_mb():.1f} MB")
    
    return combined_df

def convert_chunk_to_models(chunk: pd.DataFrame, model_class) -> List[Any]:
    """
    Converte chunk do DataFrame para modelos com fallback seguro
    """
    models = []
    
    for _, row in chunk.iterrows():
        try:
            # Converte tipos de dados com fallback
            model_data = {}
            for col in row.index:
                value = row[col]
                
                # Tratamento especial para tipos de dados
                if pd.isna(value):
                    if col in ['passenger_count', 'rate_code_id']:
                        value = 1
                    elif col in ['trip_distance', 'fare_amount', 'extra', 'mta_tax', 
                               'tip_amount', 'tolls_amount', 'improvement_surcharge', 
                               'total_amount', 'congestion_surcharge', 'airport_fee']:
                        value = 0.0
                    else:
                        value = None
                
                # Converte timestamps
                elif 'datetime' in col and pd.notna(value):
                    if isinstance(value, str):
                        value = pd.to_datetime(value)
                
                model_data[col] = value
            
            # Cria instância do modelo
            model = model_class(**model_data)
            models.append(model)
            
        except Exception as e:
            console.print(f"[yellow]⚠️ Erro ao converter linha: {e}[/yellow]")
            continue
    
    return models

def process_in_chunks_ultra(df: pd.DataFrame, chunk_size: int = 50000, 
                          process_func=None, **kwargs) -> List[Dict[str, Any]]:
    """
    Processa DataFrame em chunks otimizados com monitoramento
    """
    total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size > 0 else 0)
    results = []
    
    console.print(f"[bold blue]🔄 Processando {len(df):,} registros em {total_chunks} chunks...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("Processando chunks...", total=total_chunks)
        
        for i in range(0, len(df), chunk_size):
            chunk_start = time.time()
            chunk = df.iloc[i:i+chunk_size]
            
            # Monitora memória antes do processamento
            mem_before = memory_usage_mb()
            
            # Processa o chunk
            if process_func:
                chunk_result = process_func(chunk, **kwargs)
                results.append(chunk_result)
            
            # Monitora memória após processamento
            mem_after = memory_usage_mb()
            chunk_time = time.time() - chunk_start
            
            # Log progressivo detalhado
            progress.update(task, advance=1)
            console.print(f"  Chunk {i//chunk_size + 1}/{total_chunks}: "
                         f"{len(chunk):,} registros em {chunk_time:.1f}s, "
                         f"Memória: {mem_before:.1f}MB → {mem_after:.1f}MB "
                         f"(Δ{mem_after-mem_before:+.1f}MB)")
    
    return results

def bulk_create_models(models: List[Any], batch_size: int = 50) -> int:
    """
    Cria múltiplos modelos em batches otimizados
    """
    total_created = 0
    
    for i in range(0, len(models), batch_size):
        batch = models[i:i+batch_size]
        try:
            # Aqui você implementaria a lógica de bulk_create específica
            # para cada ORM (CaspyORM ou CQLengine)
            total_created += len(batch)
        except Exception as e:
            console.print(f"[red]❌ Erro no batch {i//batch_size + 1}: {e}[/red]")
    
    return total_created

def optimized_query_execution(query_func, iterations: int, 
                            batch_size: int = 50) -> Dict[str, Any]:
    """
    Executa queries otimizadas em batches
    """
    start_time = time.time()
    mem_before = memory_usage_mb()
    
    results = []
    
    for i in range(0, iterations, batch_size):
        batch_iterations = min(batch_size, iterations - i)
        
        for _ in range(batch_iterations):
            try:
                result = query_func()
                results.append(result)
            except Exception as e:
                console.print(f"[yellow]⚠️ Erro na query {i+_}: {e}[/yellow]")
    
    end_time = time.time()
    mem_after = memory_usage_mb()
    
    return {
        'total_time': end_time - start_time,
        'memory_used': mem_after - mem_before,
        'queries_executed': len(results),
        'ops_per_second': len(results) / (end_time - start_time)
    } 