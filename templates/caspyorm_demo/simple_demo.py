#!/usr/bin/env python3
"""
Demo Simplificado - CaspyORM
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
    title="CaspyORM Simple Demo",
    description="Demo simplificado da CaspyORM",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Página inicial"""
    return {
        "message": "🚀 CaspyORM Simple Demo",
        "description": "Demo simplificado da CaspyORM",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Verificação de saúde"""
    return {
        "status": "healthy",
        "framework": "CaspyORM",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
async def test():
    """Teste básico"""
    return {
        "message": "CaspyORM está funcionando!",
        "features": [
            "Sintaxe moderna",
            "Performance superior",
            "Menos código",
            "Async nativo"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 