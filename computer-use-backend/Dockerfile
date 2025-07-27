FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    gnupg \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo " Computer Use Agent Backend - Starting..."\n\
echo "==========================================="\n\
\n\
# Check if .env file exists, create if not\n\
if [ ! -f .env ]; then\n\
    echo "⚠️  Creating .env file from template..."\n\
    cat > .env << EOF\n\
# Computer Use Agent Backend Configuration\n\
ANTHROPIC_API_KEY=your_anthropic_api_key_here\n\
API_PROVIDER=anthropic\n\
MODEL_NAME=claude-sonnet-4-20250514\n\
WIDTH=1024\n\
HEIGHT=768\n\
EOF\n\
    echo "✅ Created .env file"\n\
    echo "❗ Please set your ANTHROPIC_API_KEY in .env file"\n\
    echo "   Get your key from: https://console.anthropic.com/"\n\
fi\n\
\n\
# Check if API key is properly set\n\
if grep -q "your_anthropic_api_key_here" .env; then\n\
    echo "❌ Please set your ANTHROPIC_API_KEY in .env file"\n\
    echo "   Edit .env and replace with your actual API key"\n\
    exit 1\n\
fi\n\
\n\
echo "✅ Environment configuration verified"\n\
\n\
# Create virtual environment if it doesn exist\n\
if [ ! -d ".venv" ]; then\n\
    echo "📦 Creating virtual environment..."\n\
    python -m venv .venv\n\
    source .venv/bin/activate\n\
    pip install -r requirements.txt\n\
    echo "✅ Dependencies installed"\n\
else\n\
    echo "📦 Using existing virtual environment..."\n\
    source .venv/bin/activate\n\
fi\n\
\n\
# Initialize database\n\
echo "🗄️  Initializing database..."\n\
python -c "from app.database.connection import create_tables; create_tables()"\n\
echo "✅ Database initialized"\n\
\n\
# Start the FastAPI application\n\
echo "🌐 Starting FastAPI backend..."\n\
echo "Access points:"\n\
echo "  • Backend API: http://localhost:8000"\n\
echo "  • Frontend Interface: http://localhost:8000"\n\
echo "  • API Docs: http://localhost:8000/docs"\n\
echo "  • VNC Web Interface: http://localhost:6080"\n\
echo ""\n\
echo "🏆 Ready for weather search demos!"\n\
echo ""\n\
\n\
exec python main.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Use the startup script
CMD ["/app/start.sh"] 