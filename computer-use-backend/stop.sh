#!/bin/bash

# Stop all services
echo "🛑 Stopping Computer Use Agent Backend..."
docker-compose down
echo "✅ All services stopped" 