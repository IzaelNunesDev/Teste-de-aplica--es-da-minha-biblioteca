#!/usr/bin/env python3
"""
Demo Simplificado - CQLengine
Versão básica para testar a funcionalidade
"""

import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criação da aplicação FastAPI
app = FastAPI(
    title="CQLengine Simple Demo",
    description="Demo simplificado da CQLengine",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Página inicial"""
    return {
        "message": "🔄 CQLengine Simple Demo",
        "description": "Demo simplificado da CQLengine",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Verificação de saúde"""
    return {
        "status": "healthy",
        "framework": "CQLengine",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test():
    """Teste básico"""
    return {
        "message": "CQLengine está funcionando!",
        "limitations": [
            "Sintaxe verbosa",
            "Performance inferior",
            "Mais código",
            "Async limitado"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 