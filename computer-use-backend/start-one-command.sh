#!/bin/bash

# Computer Use Agent Backend - One Command Startup
# This script handles everything: env setup, Docker build, and service startup

set -e

echo "�� Computer Use Agent Backend - One Command Startup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    print_status "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose not found. Please install Docker Compose first."
    print_status "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

print_success "Docker and Docker Compose found"

# Check if .env file exists, create if not
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cat > .env << EOF
# Computer Use Agent Backend Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
API_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-20250514
WIDTH=1024
HEIGHT=768
EOF
    print_success "Created .env file"
    print_warning "Please edit .env and set your ANTHROPIC_API_KEY before continuing"
    print_status "Get your API key from: https://console.anthropic.com/"
    exit 1
fi

# Check if API key is properly set
if grep -q "your_anthropic_api_key_here" .env; then
    print_error "Please set your ANTHROPIC_API_KEY in .env file"
    print_status "Edit .env and replace 'your_anthropic_api_key_here' with your actual API key"
    print_status "Get your key from: https://console.anthropic.com/"
    exit 1
fi

print_success "Environment configuration verified"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data logs
print_success "Directories created"

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down 2>/dev/null || true
print_success "Existing containers stopped"

# Pull latest agent image
print_status "Pulling latest Computer Use Agent image..."
docker pull ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
print_success "Agent image pulled"

# Build backend image
print_status "Building backend Docker image..."
docker-compose build --no-cache
print_success "Backend image built"

# Start all services
print_status "Starting all services..."
docker-compose up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 15

# Check if services are running
print_status "Checking service status..."
if docker-compose ps | grep -q "Up"; then
    print_success "All services are running!"
    
    echo ""
    echo "�� Computer Use Agent Backend is ready!"
    echo "======================================"
    echo ""
    echo "🌐 Access Points:"
    echo "  • Backend API:        http://localhost:8000"
    echo "  • Frontend Interface: http://localhost:8000"
    echo "  • API Documentation:  http://localhost:8000/docs"
    echo "  • VNC Web Interface:  http://localhost:6080"
    echo "  • Agent HTTP Server:  http://localhost:8080"
    echo ""
    echo "�� Useful Commands:"
    echo "  • View logs:          docker-compose logs -f"
    echo "  • Stop services:      docker-compose down"
    echo "  • Restart services:   docker-compose restart"
    echo "  • Rebuild:            docker-compose up --build -d"
    echo ""
    echo "�� Test the API:"
    echo "  • Health check:       curl http://localhost:8000/api/health"
    echo "  • Create session:     curl -X POST http://localhost:8000/api/sessions -H 'Content-Type: application/json' -d '{\"name\":\"Weather Search Dubai\"}'"
    echo ""
    echo "🏆 Ready for weather search demos!"
    echo ""
    print_success "Setup complete! 🚀"
    
else
    print_error "Some services failed to start. Check logs:"
    echo "   docker-compose logs"
    exit 1
fi 