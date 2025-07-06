#!/usr/bin/env python3
"""
Teste simples da CaspyORM
"""

import asyncio

async def test_caspyorm():
    """Testa conexão básica com CaspyORM"""
    
    try:
        from caspyorm.connection import connect_async, execute_async, disconnect_async
        
        print("🔍 Testando CaspyORM...")
        
        # Tenta conectar
        await connect_async(contact_points=['localhost'], port=9042)
        print("✅ Conectado com sucesso!")
        
        # Testa uma query simples
        result = await execute_async("SELECT release_version FROM system.local")
        print(f"📋 Versão do Cassandra: {result[0].release_version}")
        
        # Desconecta
        await disconnect_async()
        print("✅ Desconectado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_caspyorm()) 