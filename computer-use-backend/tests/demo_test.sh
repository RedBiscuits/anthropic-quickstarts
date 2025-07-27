#!/bin/bash

echo "🎬 CambioML Backend Demo Test"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if services are running
echo "🔍 Checking services..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    print_status "Backend API is running"
else
    print_error "Backend API is not running"
    echo "Start with: docker-compose up -d"
    exit 1
fi

if curl -s http://localhost:6080 > /dev/null; then
    print_status "VNC server is running"
else
    print_error "VNC server is not running"
    exit 1
fi

# Test session creation
echo -e "\n📝 Testing session creation..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "Demo Weather Search"}')

if echo "$SESSION_RESPONSE" | grep -q "id"; then
    SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    print_status "Session created: $SESSION_ID"
else
    print_error "Failed to create session"
    exit 1
fi

# Test message sending
echo -e "\n💬 Testing message sending..."
MESSAGE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/sessions/$SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Search the weather in Dubai"}')

if echo "$MESSAGE_RESPONSE" | grep -q "id"; then
    print_status "Message sent successfully"
else
    print_error "Failed to send message"
fi

# Test session listing
echo -e "\n📋 Testing session listing..."
SESSIONS_RESPONSE=$(curl -s http://localhost:8000/api/sessions)
SESSION_COUNT=$(echo "$SESSIONS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
print_status "Found $SESSION_COUNT sessions"

# Test VNC accessibility
echo -e "\n🖥️  Testing VNC connection..."
if curl -s http://localhost:6080/vnc.html > /dev/null; then
    print_status "noVNC interface accessible"
else
    print_error "noVNC interface not accessible"
fi

# Test frontend
echo -e "\n🌐 Testing frontend..."
if curl -s http://localhost:8000/ | grep -q "Computer Use Agent"; then
    print_status "Frontend is accessible"
else
    print_error "Frontend not accessible"
fi

# Summary
echo -e "\n�� Demo Test Complete!"
echo -e "\n📊 Access Points:"
echo -e "   • Frontend Interface: ${GREEN}http://localhost:8000${NC}"
echo -e "   • API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   • VNC Web Interface: ${GREEN}http://localhost:6080${NC}"
echo -e "   • Direct VNC: ${GREEN}localhost:5900${NC}"
echo -e "\n🔧 To test the full experience:"
echo -e "   1. Open http://localhost:8000 in your browser"
echo -e "   2. Create a new session"
echo -e "   3. Send a message like 'Search weather in Dubai'"
echo -e "   4. Watch the real-time progress"
echo -e "   5. Click 'Connect VNC' to see the agent desktop" 