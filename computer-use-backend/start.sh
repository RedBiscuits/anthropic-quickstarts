#!/bin/bash

# Computer Use Agent Backend - Quick Start Script
set -e

echo "🚀 Computer Use Agent Backend - Quick Start"
echo "==========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOF
# Computer Use Agent Backend Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
API_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-20250514
WIDTH=1024
HEIGHT=768
EOF
    echo "✅ Created .env file"
    echo "❗ Please edit .env and set your ANTHROPIC_API_KEY before continuing"
    echo "   Get your API key from: https://console.anthropic.com/"
    exit 1
fi

# Check if API key is set
if grep -q "your_anthropic_api_key_here" .env; then
    echo "❌ Please set your ANTHROPIC_API_KEY in .env file"
    echo "   Edit .env and replace 'your_anthropic_api_key_here' with your actual API key"
    echo "   Get your key from: https://console.anthropic.com/"
    exit 1
fi

echo "✅ Environment configuration found"

# Choose startup mode
echo ""
echo "Choose startup mode:"
echo "  1) Development mode (recommended for testing)"
echo "  2) Docker Compose (full production setup)"
echo "  3) Run API tests only"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🛠️  Starting in Development Mode"
        echo "================================"
        
        # Check if Python is available
        if ! command -v python3 &> /dev/null; then
            echo "❌ Python 3 not found. Please install Python 3.11+"
            exit 1
        fi
        
        # Install requirements if needed
        if [ ! -d ".venv" ]; then
            echo "📦 Creating virtual environment..."
            python3 -m venv .venv
            source .venv/bin/activate
            pip install -r requirements.txt
            echo "✅ Dependencies installed"
        else
            echo "📦 Using existing virtual environment..."
            source .venv/bin/activate
        fi
        
        # Start agent container if not running
        if ! docker ps | grep -q computer-use-agent; then
            echo "🐳 Starting Computer Use Agent container..."
            docker run -d \
                --name computer-use-agent \
                -p 5900:5900 -p 6080:6080 -p 8080:8080 \
                --env-file .env \
                ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
            echo "✅ Agent container started"
        else
            echo "✅ Agent container already running"
        fi
        
        echo ""
        echo "🌐 Starting FastAPI backend..."
        echo "Access points:"
        echo "  • Backend API: http://localhost:8000"
        echo "  • Frontend Interface: http://localhost:8000"
        echo "  • API Docs: http://localhost:8000/docs"
        echo "  • VNC Web Interface: http://localhost:6080"
        echo ""
        echo "Press Ctrl+C to stop the server"
        echo ""
        
        python main.py
        ;;
        
    2)
        echo ""
        echo "🐳 Starting with Docker Compose"
        echo "==============================="
        
        # Check if Docker is available
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not found. Please install Docker"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            echo "❌ Docker Compose not found. Please install Docker Compose"
            exit 1
        fi
        
        # Pull latest images
        echo "📥 Pulling latest images..."
        docker-compose pull
        
        # Start services
        echo "🚀 Starting all services..."
        docker-compose up -d
        
        # Wait for services to start
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            echo ""
            echo "✅ All services are running!"
            echo ""
            echo "🌐 Access points:"
            echo "  • Backend API: http://localhost:8000"
            echo "  • Frontend Interface: http://localhost:8000"
            echo "  • API Docs: http://localhost:8000/docs"
            echo "  • VNC Web Interface: http://localhost:6080"
            echo ""
            echo "📋 Useful commands:"
            echo "  • View logs: docker-compose logs -f"
            echo "  • Stop services: docker-compose down"
            echo "  • Restart: docker-compose restart"
            echo ""
            echo "🏆 Ready for weather search demos!"
        else
            echo "❌ Some services failed to start. Check logs:"
            echo "   docker-compose logs"
        fi
        ;;
        
    3)
        echo ""
        echo "🧪 Running API Tests"
        echo "==================="
        
        # Check if server is running
        if ! curl -s http://localhost:8000/api/health > /dev/null; then
            echo "❌ Backend server not running. Please start it first:"
            echo "   python main.py"
            exit 1
        fi
        
        # Install test dependencies
        pip install requests websockets 2>/dev/null || echo "Installing test dependencies..."
        
        # Run tests
        python test_api.py
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac 