#!/bin/bash

# Quick Start Script - Even simpler one-liner
# Usage: ./quick-start.sh

set -e

echo "�� Computer Use Agent Backend - Quick Start"
echo "=========================================="

# Check if .env exists and has API key
if [ ! -f .env ] || grep -q "your_anthropic_api_key_here" .env; then
    echo "❌ Please set up your .env file with ANTHROPIC_API_KEY first"
    echo "   Copy .env.example to .env and add your API key"
    echo "   Get your key from: https://console.anthropic.com/"
    exit 1
fi

# Run the full startup script
./start-one-command.sh 