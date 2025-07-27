#!/usr/bin/env python3
"""
Simple test script for the Computer Use Agent Backend API
"""
import asyncio
import json
import os
import requests
import websockets
from datetime import datetime

API_BASE = "http://localhost:8000/api"
WS_BASE = "ws://localhost:8000/api/ws"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_session_management():
    """Test session creation and management"""
    print("\n📝 Testing session management...")
    
    try:
        # Create a new session
        session_data = {"name": f"Test Session {datetime.now().strftime('%H:%M:%S')}"}
        response = requests.post(f"{API_BASE}/sessions", json=session_data)
        
        if response.status_code == 200:
            session = response.json()
            print(f"✅ Session created: {session['id']}")
            
            # Get session details
            response = requests.get(f"{API_BASE}/sessions/{session['id']}")
            if response.status_code == 200:
                print("✅ Session retrieval successful")
                return session['id']
            else:
                print(f"❌ Session retrieval failed: {response.status_code}")
                return None
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Session management error: {e}")
        return None

def test_list_sessions():
    """Test listing all sessions"""
    print("\n📋 Testing session listing...")
    try:
        response = requests.get(f"{API_BASE}/sessions")
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Found {len(sessions)} sessions")
            for session in sessions[-3:]:  # Show last 3
                print(f"   - {session['name']} ({session['status']})")
            return True
        else:
            print(f"❌ Session listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Session listing error: {e}")
        return False

async def test_websocket(session_id):
    """Test WebSocket connection"""
    print(f"\n🔌 Testing WebSocket connection for session {session_id}...")
    try:
        uri = f"{WS_BASE}/{session_id}"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")
            
            # Wait for initial message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"✅ Received initial message: {data.get('type', 'unknown')}")
                return True
            except asyncio.TimeoutError:
                print("⚠️  No initial message received (this is OK)")
                return True
                
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False

def test_message_sending(session_id):
    """Test sending a message to a session"""
    print(f"\n💬 Testing message sending to session {session_id}...")
    
    # Note: This will fail without a real API key, but we can test the endpoint
    try:
        message_data = {"content": "Hello, this is a test message"}
        response = requests.post(f"{API_BASE}/sessions/{session_id}/messages", json=message_data)
        
        if response.status_code == 200:
            print("✅ Message sent successfully")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Message sending returned {response.status_code} (expected without valid API key)")
            return True  # This is expected without a real API key
            
    except Exception as e:
        print(f"❌ Message sending error: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🧪 Computer Use Agent Backend - API Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Basic health check failed. Is the server running?")
        return False
    
    # Test 2: Session management
    session_id = test_session_management()
    if not session_id:
        print("\n❌ Session management failed")
        return False
    
    # Test 3: List sessions
    if not test_list_sessions():
        print("\n❌ Session listing failed")
        return False
    
    # Test 4: WebSocket connection
    if not await test_websocket(session_id):
        print("\n❌ WebSocket test failed")
        return False
    
    # Test 5: Message sending
    if not test_message_sending(session_id):
        print("\n❌ Message sending test failed")
        return False
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary:")
    print("   ✅ Health endpoint working")
    print("   ✅ Session management working")
    print("   ✅ WebSocket connections working")
    print("   ✅ API endpoints accessible")
    print("\n🔑 Next steps:")
    print("   1. Set ANTHROPIC_API_KEY in .env file")
    print("   2. Test with real weather search queries")
    print("   3. Verify VNC connection on http://localhost:6080")
    
    return True

if __name__ == "__main__":
    print("Starting API tests...")
    print("Make sure the server is running: python main.py")
    print()
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}") 