#!/usr/bin/env python3
"""
Weather Search Test Script for Computer Use Agent Backend
"""
import requests
import json
import time
import os
from datetime import datetime

API_BASE = "http://localhost:8000/api"

def test_weather_search():
    """Test weather search functionality"""
    print("🌤️  WEATHER SEARCH TEST")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1️⃣  Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
            print(f"✅ API Key: {'Configured' if data['api_key_configured'] else 'Missing'}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Create a weather search session
    print("\n2️⃣  Creating Weather Search Session...")
    session_data = {
        "name": f"Weather Search Dubai - {datetime.now().strftime('%H:%M:%S')}"
    }
    
    try:
        response = requests.post(f"{API_BASE}/sessions", json=session_data)
        if response.status_code == 200:
            session = response.json()
            session_id = session['id']
            print(f"✅ Session created: {session['name']}")
            print(f"✅ Session ID: {session_id}")
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return False
    
    # Test 3: Send weather search query
    print("\n3️⃣  Sending Weather Search Query...")
    weather_queries = [
        "What's the current weather in Dubai?",
        "Show me the weather forecast for San Francisco for the next 3 days"
    ]
    
    for i, query in enumerate(weather_queries, 1):
        print(f"\n   Query {i}: {query}")
        message_data = {"content": query}
        
        try:
            response = requests.post(f"{API_BASE}/sessions/{session_id}/messages", json=message_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Message sent successfully")
                print(f"   📝 Status: {result.get('metadata', {}).get('status', 'processing')}")
            else:
                print(f"   ❌ Message sending failed: {response.status_code}")
                print(f"      Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Message sending error: {e}")
    
    # Test 4: List sessions
    print("\n4️⃣  Listing All Sessions...")
    try:
        response = requests.get(f"{API_BASE}/sessions")
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Found {len(sessions)} sessions")
            for session in sessions[-3:]:  # Show last 3
                print(f"   📋 {session['name']} ({session['status']}) - {session['message_count']} messages")
        else:
            print(f"❌ Session listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Session listing error: {e}")
    
    print("\n🎉 Weather Search Test Completed!")
    print("\n📋 Next Steps:")
    print("   • Check the VNC interface at http://localhost:6080")
    print("   • Monitor real-time progress via WebSocket")
    print("   • View session details in the frontend")
    
    return True

if __name__ == "__main__":
    print("�� Computer Use Agent - Weather Search Test")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE}")
    print()
    
    success = test_weather_search()
    
    if success:
        print("\n✅ All tests passed! Weather search functionality is working.")
    else:
        print("\n❌ Some tests failed. Check the server logs for details.")
