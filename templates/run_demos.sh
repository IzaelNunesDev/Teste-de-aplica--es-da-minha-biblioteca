#!/bin/bash

# Script para gerenciar os demos CaspyORM vs CQLengine

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Função para verificar se o Cassandra está rodando
check_cassandra() {
    if pgrep -f cassandra > /dev/null; then
        print_status "Cassandra está rodando"
        return 0
    else
        print_warning "Cassandra não está rodando"
        return 1
    fi
}

# Função para parar demos
stop_demos() {
    print_status "Parando demos..."
    pkill -f "simple_demo.py" || true
    pkill -f "uvicorn.*main:app" || true
    sleep 2
    print_status "Demos parados"
}

# Função para iniciar demos
start_demos() {
    print_status "Iniciando demos..."
    
    # Verifica se as portas estão livres
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Porta 8000 já está em uso"
    fi
    
    if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Porta 8001 já está em uso"
    fi
    
    # Inicia CaspyORM
    print_status "Iniciando CaspyORM Demo (porta 8000)..."
    cd caspyorm_demo
    python simple_demo.py &
    CASPYORM_PID=$!
    cd ..
    
    # Inicia CQLengine
    print_status "Iniciando CQLengine Demo (porta 8001)..."
    cd cqlengine_demo
    python simple_demo.py &
    CQLENGINE_PID=$!
    cd ..
    
    # Aguarda inicialização
    sleep 5
    
    # Testa os demos
    test_demos
    
    print_status "Demos iniciados com sucesso!"
    print_status "CaspyORM PID: $CASPYORM_PID"
    print_status "CQLengine PID: $CQLENGINE_PID"
}

# Função para testar demos
test_demos() {
    print_status "Testando demos..."
    
    # Testa CaspyORM
    if curl -s http://localhost:8000/ > /dev/null; then
        print_status "✅ CaspyORM está funcionando"
    else
        print_error "❌ CaspyORM não está respondendo"
    fi
    
    # Testa CQLengine
    if curl -s http://localhost:8001/ > /dev/null; then
        print_status "✅ CQLengine está funcionando"
    else
        print_error "❌ CQLengine não está respondendo"
    fi
}

# Função para mostrar status
show_status() {
    print_header "Status dos Demos"
    
    # Verifica processos
    if pgrep -f "simple_demo.py" > /dev/null; then
        print_status "Demos estão rodando"
        echo ""
        echo "📊 URLs dos Demos:"
        echo "• CaspyORM Demo: http://localhost:8000"
        echo "• CQLengine Demo: http://localhost:8001"
        echo ""
        echo "📚 Documentação:"
        echo "• CaspyORM Docs: http://localhost:8000/docs"
        echo "• CQLengine Docs: http://localhost:8001/docs"
        echo ""
        echo "🔍 Endpoints de Teste:"
        echo "• CaspyORM Health: http://localhost:8000/health"
        echo "• CQLengine Health: http://localhost:8001/health"
        echo "• CaspyORM Test: http://localhost:8000/test"
        echo "• CQLengine Test: http://localhost:8001/test"
    else
        print_warning "Demos não estão rodando"
    fi
    
    # Verifica Cassandra
    check_cassandra
}

# Função para mostrar ajuda
show_help() {
    print_header "Gerenciador de Demos CaspyORM vs CQLengine"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  start     - Inicia os demos"
    echo "  stop      - Para os demos"
    echo "  restart   - Reinicia os demos"
    echo "  status    - Mostra status dos demos"
    echo "  test      - Testa os demos"
    echo "  help      - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 start    # Inicia os demos"
    echo "  $0 status   # Mostra status"
    echo "  $0 stop     # Para os demos"
}

# Main
case "${1:-help}" in
    start)
        stop_demos
        start_demos
        ;;
    stop)
        stop_demos
        ;;
    restart)
        stop_demos
        start_demos
        ;;
    status)
        show_status
        ;;
    test)
        test_demos
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Comando inválido: $1"
        show_help
        exit 1
        ;;
esac 