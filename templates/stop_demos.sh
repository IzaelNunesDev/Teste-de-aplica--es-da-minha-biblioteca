#!/bin/bash

# Script para parar os demos CaspyORM vs CQLengine
# Uso: ./stop_demos.sh [docker|local]

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
    echo -e "${BLUE}  PARANDO DEMOS${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

# Função para verificar se o comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para parar com Docker
stop_with_docker() {
    print_message "Parando demos com Docker Compose..."
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose não está instalado"
        exit 1
    fi
    
    # Para os serviços
    docker-compose down
    
    print_message "Demos parados com sucesso!"
}

# Função para parar localmente
stop_locally() {
    print_message "Parando demos locais..."
    
    # Para CaspyORM se o PID existir
    if [ -f caspyorm.pid ]; then
        CASPYORM_PID=$(cat caspyorm.pid)
        if kill -0 $CASPYORM_PID 2>/dev/null; then
            print_message "Parando CaspyORM Demo (PID: $CASPYORM_PID)..."
            kill $CASPYORM_PID
            rm caspyorm.pid
        else
            print_warning "CaspyORM Demo já não está rodando"
            rm -f caspyorm.pid
        fi
    else
        print_warning "Arquivo caspyorm.pid não encontrado"
    fi
    
    # Para CQLengine se o PID existir
    if [ -f cqlengine.pid ]; then
        CQLENGINE_PID=$(cat cqlengine.pid)
        if kill -0 $CQLENGINE_PID 2>/dev/null; then
            print_message "Parando CQLengine Demo (PID: $CQLENGINE_PID)..."
            kill $CQLENGINE_PID
            rm cqlengine.pid
        else
            print_warning "CQLengine Demo já não está rodando"
            rm -f cqlengine.pid
        fi
    else
        print_warning "Arquivo cqlengine.pid não encontrado"
    fi
    
    # Remove arquivos de log se existirem
    if [ -f caspyorm.log ]; then
        print_message "Log CaspyORM: caspyorm.log"
    fi
    
    if [ -f cqlengine.log ]; then
        print_message "Log CQLengine: cqlengine.log"
    fi
    
    print_message "Demos parados com sucesso!"
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 [docker|local]"
    echo
    echo "Opções:"
    echo "  docker    Para os demos usando Docker Compose"
    echo "  local     Para os demos iniciados localmente"
    echo "  help      Mostra esta ajuda"
    echo
    echo "Exemplos:"
    echo "  $0 docker    # Para com Docker"
    echo "  $0 local     # Para localmente"
}

# Função principal
main() {
    print_header
    
    case "${1:-local}" in
        docker)
            stop_with_docker
            ;;
        local)
            stop_locally
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