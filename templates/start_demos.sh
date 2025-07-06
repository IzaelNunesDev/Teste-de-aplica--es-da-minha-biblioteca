#!/bin/bash

# Script para iniciar os demos CaspyORM vs CQLengine
# Uso: ./start_demos.sh [docker|local]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
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
    echo -e "${BLUE}  CASPYORM vs CQLENGINE DEMOS${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

# Função para verificar se o comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para verificar se a porta está em uso
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Função para aguardar serviço
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    print_message "Aguardando $service_name em $host:$port..."
    
    for i in {1..30}; do
        if nc -z $host $port 2>/dev/null; then
            print_message "$service_name está pronto!"
            return 0
        fi
        sleep 2
    done
    
    print_error "$service_name não está respondendo após 60 segundos"
    return 1
}

# Função para iniciar com Docker
start_with_docker() {
    print_message "Iniciando demos com Docker Compose..."
    
    if ! command_exists docker; then
        print_error "Docker não está instalado"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose não está instalado"
        exit 1
    fi
    
    # Verifica se as portas estão livres
    if port_in_use 8000; then
        print_warning "Porta 8000 já está em uso"
    fi
    
    if port_in_use 8001; then
        print_warning "Porta 8001 já está em uso"
    fi
    
    if port_in_use 9042; then
        print_warning "Porta 9042 já está em uso"
    fi
    
    # Inicia os serviços
    docker-compose up -d
    
    # Aguarda Cassandra
    wait_for_service localhost 9042 "Cassandra"
    
    # Aguarda CaspyORM
    wait_for_service localhost 8000 "CaspyORM Demo"
    
    # Aguarda CQLengine
    wait_for_service localhost 8001 "CQLengine Demo"
    
    print_message "Todos os serviços iniciados!"
    print_message "CaspyORM Demo: http://localhost:8000"
    print_message "CQLengine Demo: http://localhost:8001"
    print_message "Documentação CaspyORM: http://localhost:8000/docs"
    print_message "Documentação CQLengine: http://localhost:8001/docs"
}

# Função para iniciar localmente
start_locally() {
    print_message "Iniciando demos localmente..."
    
    # Verifica se Python está instalado
    if ! command_exists python3; then
        print_error "Python 3 não está instalado"
        exit 1
    fi
    
    # Verifica se pip está instalado
    if ! command_exists pip; then
        print_error "pip não está instalado"
        exit 1
    fi
    
    # Verifica se as portas estão livres
    if port_in_use 8000; then
        print_error "Porta 8000 já está em uso"
        exit 1
    fi
    
    if port_in_use 8001; then
        print_error "Porta 8001 já está em uso"
        exit 1
    fi
    
    # Verifica se Cassandra está rodando
    if ! port_in_use 9042; then
        print_warning "Cassandra não está rodando na porta 9042"
        print_message "Inicie o Cassandra primeiro: cassandra"
    fi
    
    # Instala dependências do CaspyORM
    print_message "Instalando dependências CaspyORM..."
    cd caspyorm_demo
    pip install -r requirements.txt
    cd ..
    
    # Instala dependências do CQLengine
    print_message "Instalando dependências CQLengine..."
    cd cqlengine_demo
    pip install -r requirements.txt
    cd ..
    
    # Inicia CaspyORM em background
    print_message "Iniciando CaspyORM Demo..."
    cd caspyorm_demo
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../caspyorm.log 2>&1 &
    CASPYORM_PID=$!
    cd ..
    
    # Inicia CQLengine em background
    print_message "Iniciando CQLengine Demo..."
    cd cqlengine_demo
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../cqlengine.log 2>&1 &
    CQLENGINE_PID=$!
    cd ..
    
    # Aguarda os serviços
    wait_for_service localhost 8000 "CaspyORM Demo"
    wait_for_service localhost 8001 "CQLengine Demo"
    
    print_message "Todos os serviços iniciados!"
    print_message "CaspyORM Demo: http://localhost:8000"
    print_message "CQLengine Demo: http://localhost:8001"
    print_message "Documentação CaspyORM: http://localhost:8000/docs"
    print_message "Documentação CQLengine: http://localhost:8001/docs"
    print_message "Logs CaspyORM: tail -f caspyorm.log"
    print_message "Logs CQLengine: tail -f cqlengine.log"
    
    # Salva PIDs para parar depois
    echo $CASPYORM_PID > caspyorm.pid
    echo $CQLENGINE_PID > cqlengine.pid
    
    print_message "Para parar os demos: ./stop_demos.sh"
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 [docker|local]"
    echo
    echo "Opções:"
    echo "  docker    Inicia os demos usando Docker Compose"
    echo "  local     Inicia os demos localmente"
    echo "  help      Mostra esta ajuda"
    echo
    echo "Exemplos:"
    echo "  $0 docker    # Inicia com Docker"
    echo "  $0 local     # Inicia localmente"
    echo
    echo "Requisitos:"
    echo "  Docker: docker, docker-compose"
    echo "  Local: python3, pip, cassandra"
}

# Função principal
main() {
    print_header
    
    case "${1:-local}" in
        docker)
            start_with_docker
            ;;
        local)
            start_locally
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Opção inválida: $1"
            show_help
            exit 1
            ;;
    esac
}

# Executa função principal
main "$@" 