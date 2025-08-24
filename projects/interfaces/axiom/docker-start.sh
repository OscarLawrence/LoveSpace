#!/bin/bash
# Docker management script for Axiom Chat

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        log_warning ".env file not found!"
        if [ -f .env.template ]; then
            log_info "Creating .env from template..."
            cp .env.template .env
            log_warning "Please edit .env and add your ANTHROPIC_API_KEY"
            exit 1
        else
            log_error "No .env.template found. Please create .env with ANTHROPIC_API_KEY"
            exit 1
        fi
    fi
    
    if ! grep -q "ANTHROPIC_API_KEY=" .env || grep -q "ANTHROPIC_API_KEY=$" .env || grep -q "ANTHROPIC_API_KEY=your_" .env; then
        log_error "ANTHROPIC_API_KEY not set in .env file"
        log_info "Please edit .env and add your actual Anthropic API key"
        exit 1
    fi
}

# Main command handling
case "${1:-start}" in
    "start"|"up")
        log_info "Starting Axiom Chat with Docker..."
        check_env
        docker-compose up -d
        log_success "Axiom Chat started!"
        log_info "🌐 Access at: http://localhost:8000"
        log_info "📊 Check status: ./docker-start.sh status"
        log_info "📋 View logs: ./docker-start.sh logs"
        ;;
    
    "stop"|"down")
        log_info "Stopping Axiom Chat..."
        docker-compose down
        log_success "Axiom Chat stopped!"
        ;;
    
    "restart")
        log_info "Restarting Axiom Chat..."
        docker compose down
        docker compose up -d
        log_success "Axiom Chat restarted!"
        ;;
    
    "build")
        log_info "Building Axiom Chat image..."
        docker-compose build
        log_success "Build complete!"
        ;;
    
    "rebuild")
        log_info "Rebuilding Axiom Chat (no cache)..."
        docker compose build --no-cache
        log_success "Rebuild complete!"
        ;;
    
    "logs")
        log_info "Showing Axiom Chat logs..."
        docker compose logs -f axiom-chat
        ;;
    
    "status")
        log_info "Axiom Chat status:"
        docker compose ps
        echo
        if docker compose ps | grep -q "Up"; then
            log_success "Axiom Chat is running!"
            log_info "🌐 Access at: http://localhost:8000"
        else
            log_warning "Axiom Chat is not running"
        fi
        ;;
    
    "shell")
        log_info "Opening shell in Axiom Chat container..."
        docker compose exec axiom-chat /bin/bash
        ;;
    
    "clean")
        log_info "Cleaning up Docker resources..."
        docker compose down -v
        docker system prune -f
        log_success "Cleanup complete!"
        ;;
    
    "help"|"-h"|"--help")
        echo "Axiom Chat Docker Management"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  start, up     Start Axiom Chat (default)"
        echo "  stop, down    Stop Axiom Chat"
        echo "  restart       Restart Axiom Chat"
        echo "  build         Build the Docker image"
        echo "  rebuild       Rebuild image without cache"
        echo "  logs          Show and follow logs"
        echo "  status        Show container status"
        echo "  shell         Open shell in container"
        echo "  clean         Stop and clean up resources"
        echo "  help          Show this help"
        ;;
    
    *)
        log_error "Unknown command: $1"
        log_info "Use '$0 help' for available commands"
        exit 1
        ;;
esac