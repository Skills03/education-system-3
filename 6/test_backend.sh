#!/bin/bash
# End-to-end backend test for Master Teacher

API_URL="http://localhost:5000"

echo "======================================================================="
echo "🎓 MASTER TEACHER - END-TO-END BACKEND TEST"
echo "======================================================================="

# TEST 1: Session Creation (No Mode Parameter)
echo -e "\nTEST 1: Session Creation (No Mode Parameter)"
echo "-----------------------------------------------------------------------"

response=$(curl -s -X POST "$API_URL/api/session/start" -H "Content-Type: application/json" -d '{}')
session_id=$(echo "$response" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$session_id" ]; then
    echo "❌ FAILED: Could not create session"
    exit 1
fi

# Verify no mode parameter in response
if echo "$response" | grep -q '"mode"'; then
    echo "❌ FAILED: Response should not contain 'mode' parameter"
    exit 1
fi

echo "✅ Session created: ${session_id:0:8}..."
echo "✅ No mode parameter (unified master agent)"

# TEST 2: Compositional Teaching
echo -e "\nTEST 2: Compositional Teaching - 'Teach me quicksort'"
echo "-----------------------------------------------------------------------"

# Send teaching request
teach_response=$(curl -s -X POST "$API_URL/api/teach" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$session_id\", \"message\": \"Teach me quicksort\"}")

if ! echo "$teach_response" | grep -q '"processing"'; then
    echo "❌ FAILED: Teaching request not processing"
    exit 1
fi

echo "✅ Request sent and processing"

# Monitor SSE stream for 45 seconds
echo -e "\n🔧 Monitoring tool usage..."

timeout 45 curl -s -N "$API_URL/api/stream/$session_id" > stream_output.txt 2>&1 &
curl_pid=$!

sleep 40
kill $curl_pid 2>/dev/null || true

# Parse results
tools_used=$(grep -o '"type": "action"' stream_output.txt | wc -l)
has_teacher=$(grep -q '"type": "teacher"' stream_output.txt && echo "yes" || echo "no")
has_output=$(grep -q '"type": "output"' stream_output.txt && echo "yes" || echo "no")
has_complete=$(grep -q '"type": "complete"' stream_output.txt && echo "yes" || echo "no")

# Count tool types
visual_tools=$(grep -o 'mcp__visual__' stream_output.txt | wc -l)
concept_tools=$(grep -o 'mcp__scrimba__' stream_output.txt | wc -l)
project_tools=$(grep -o 'mcp__live_coding__' stream_output.txt | wc -l)

modalities=0
[ $visual_tools -gt 0 ] && ((modalities++))
[ $concept_tools -gt 0 ] && ((modalities++))
[ $project_tools -gt 0 ] && ((modalities++))

# Display tool calls
echo ""
grep '"type": "action"' stream_output.txt | grep -o 'mcp__[^"]*' | nl | sed 's/^/  🔧 Tool /'

echo -e "\n📊 Multi-Modal Analysis:"
echo "  • Visual tools: $visual_tools"
echo "  • Concept tools: $concept_tools"
echo "  • Project tools: $project_tools"
echo "  • Modalities used: $modalities/3"

# Verify results
if [ $tools_used -lt 3 ]; then
    echo -e "\n❌ FAILED: Expected 3+ tools, got $tools_used"
    exit 1
fi

if [ "$has_teacher" != "yes" ]; then
    echo -e "\n❌ FAILED: No teacher response"
    exit 1
fi

if [ "$has_output" != "yes" ]; then
    echo -e "\n❌ FAILED: No tool output"
    exit 1
fi

if [ $modalities -lt 2 ]; then
    echo -e "\n❌ FAILED: Expected 2+ modalities, got $modalities"
    exit 1
fi

echo "✅ Compositional teaching verified! ($modalities modalities)"

# Extract cost if present
cost=$(grep '"type": "cost"' stream_output.txt | grep -o '\$[0-9.]*' | tail -1)
if [ -n "$cost" ]; then
    echo "💰 Cost: $cost"
fi

# Final summary
echo ""
echo "======================================================================="
echo "✅ ALL TESTS PASSED!"
echo "======================================================================="
echo ""
echo "📈 Summary:"
echo "  • Session creation: ✅ (no mode parameter)"
echo "  • Compositional teaching: ✅ ($tools_used tools)"
echo "  • Multi-modal learning: ✅ ($modalities modalities)"
echo "  • Teacher responses: ✅"
echo "  • Tool outputs: ✅"
if [ "$has_complete" = "yes" ]; then
    echo "  • Completion signal: ✅"
fi
echo ""
echo "🎉 Master Teacher backend working perfectly!"

# Cleanup
rm -f stream_output.txt
