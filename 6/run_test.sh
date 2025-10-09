#!/bin/bash

echo "=================================="
echo "🚀 STARTING TEACHING SYSTEM TEST"
echo "=================================="
echo ""

# Check if server is running
if curl -s http://localhost:5000/ > /dev/null 2>&1; then
    echo "✅ Server is already running"
else
    echo "⚠️  Server not running. Starting server..."
    python3 server.py > /tmp/teaching_server.log 2>&1 &
    SERVER_PID=$!
    echo "   Server PID: $SERVER_PID"
    echo "   Waiting for server to start..."
    sleep 8

    if curl -s http://localhost:5000/ > /dev/null 2>&1; then
        echo "✅ Server started successfully"
    else
        echo "❌ Server failed to start. Check /tmp/teaching_server.log"
        exit 1
    fi
fi

echo ""
echo "=================================="
echo "🧪 RUNNING COMPREHENSIVE TESTS"
echo "=================================="
echo ""

# Run the test
python3 test_comprehensive.py

echo ""
echo "=================================="
echo "📋 CHECK RESULTS ABOVE"
echo "=================================="
echo ""
echo "To stop the server: pkill -f 'python3 server.py'"
echo "To view server logs: tail -f /tmp/teaching_server.log"
