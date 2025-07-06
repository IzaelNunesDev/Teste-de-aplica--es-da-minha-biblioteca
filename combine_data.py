#!/usr/bin/env python3
"""
Script para combinar dados do NYC Taxi de múltiplos meses
"""

import pandas as pd
import os
from pathlib import Path

def combine_nyc_taxi_data():
    """Combina dados de múltiplos meses do NYC Taxi"""
    
    data_dir = Path("data/nyc_taxi")
    output_file = data_dir / "yellow_tripdata_combined.parquet"
    
    # Lista todos os arquivos parquet
    parquet_files = list(data_dir.glob("yellow_tripdata_*.parquet"))
    parquet_files = [f for f in parquet_files if "combined" not in f.name]
    
    print(f"📊 Combinando {len(parquet_files)} arquivos de dados...")
    
    # Carrega e combina os dados
    dfs = []
    total_records = 0
    
    for file_path in sorted(parquet_files):
        print(f"   📁 Carregando {file_path.name}...")
        df = pd.read_parquet(file_path)
        total_records += len(df)
        dfs.append(df)
        print(f"      ✅ {len(df):,} registros carregados")
    
    # Combina todos os DataFrames
    print("🔄 Combinando dados...")
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Limpa dados
    print("🧹 Limpando dados...")
    combined_df = combined_df.dropna(subset=['VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime'])
    
    # Remove duplicatas
    combined_df = combined_df.drop_duplicates()
    
    print(f"✅ Dados combinados: {len(combined_df):,} registros únicos")
    print(f"📁 Salvando em: {output_file}")
    
    # Salva arquivo combinado
    combined_df.to_parquet(output_file, index=False)
    
    # Mostra estatísticas
    print(f"\n📈 Estatísticas do Dataset Combinado:")
    print(f"   📊 Total de registros: {len(combined_df):,}")
    print(f"   🗓️  Período: {combined_df['tpep_pickup_datetime'].min()} a {combined_df['tpep_pickup_datetime'].max()}")
    print(f"   💰 Valor médio: ${combined_df['total_amount'].mean():.2f}")
    print(f"   🚗 Distância média: {combined_df['trip_distance'].mean():.2f} milhas")
    print(f"   👥 Passageiros médios: {combined_df['passenger_count'].mean():.1f}")
    
    # Calcula tamanho do arquivo
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"   💾 Tamanho do arquivo: {file_size_mb:.1f} MB")
    
    return str(output_file)

if __name__ == "__main__":
    output_file = combine_nyc_taxi_data()
    print(f"\n🎯 Dataset combinado salvo em: {output_file}")
    print("🚀 Agora você pode executar o benchmark com mais dados!") 