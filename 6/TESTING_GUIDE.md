# Testing Guide - Cognitive Teaching System

## 🚀 Quick Test

```bash
cd /home/mahadev/Desktop/dev/education/6
./run_test.sh
```

This will:
1. Start the server (if not running)
2. Run comprehensive automated tests
3. Show results summary

---

## 📋 Manual Testing Steps

### 1. Start Server

```bash
python3 server.py
```

Expected output:
```
🎓 SPECIALIZED TEACHING SYSTEM - INTELLIGENT AGENT ROUTING
...
🧠 COGNITIVE FEATURES:
  • Concept-based limits    (max 3 concepts per response)
  • Sequential tool chains  (each tool builds on previous)
  • Pacing delays           (2s absorption time)
  • Persistent memory       (.claude/CLAUDE.md)
```

### 2. Test Agent Routing

Open browser: `http://localhost:5000`

#### Test Explainer Agent:
- Query: "Explain what variables are"
- Expected: Routes to **explainer** agent
- Look for: 🎓 routing message

#### Test Reviewer Agent:
- Query: "Review this code: def add(x,y): return x+y"
- Expected: Routes to **reviewer** agent
- Look for: 🔍 routing message

#### Test Challenger Agent:
- Query: "Give me a challenge about loops"
- Expected: Routes to **challenger** agent
- Look for: 🎯 routing message

#### Test Assessor Agent:
- Query: "Test my understanding of functions"
- Expected: Routes to **assessor** agent
- Look for: 📊 routing message

### 3. Test Memory Persistence

**Session 1:**
```
Query: "Teach me about variables"
```

Check `.claude/CLAUDE.md`:
```bash
cat .claude/CLAUDE.md
```

Should see:
- Session Count: increased
- Mastered/Learning Concepts: "variables"
- Session Log: entry for this session

**Session 2 (in same browser session):**
```
Query: "Now teach me about loops"
```

Agent should:
- ✅ Reference variables from Session 1
- ✅ Build loop examples using variables
- ✅ NOT re-explain variables

Check `.claude/CLAUDE.md` again:
- Session Count: increased again
- Both "variables" AND "loops" listed

### 4. Test Concept-Based Limits

Query: "Teach me Python basics"

Watch for:
1. **Concept Declaration**: Agent says "This response teaches N concepts: ..."
2. **Tool Count**: Should use 1-4 tools max (for 3 concepts)
3. **Sequential Order**: Tools build on each other

Example good sequence:
```
🔧 generate_concept_diagram (shows concept visually)
  ↓
🔧 show_code_example (demonstrates with code)
  ↓
🔧 create_interactive_challenge (practice)
```

### 5. Test Tool Sequencing

Query: "Explain arrays with examples"

Agent should:
- Use visual tool FIRST (diagram/visualization)
- Follow with code tool (references the diagram)
- Optionally add challenge (uses same code pattern)

❌ BAD: Random unrelated tools
✅ GOOD: Each tool builds on previous

---

## 🧪 Automated Test Suite

Run comprehensive tests:
```bash
python3 test_comprehensive.py
```

Tests include:
1. ✅ Session Creation
2. ✅ Agent Routing (explainer, reviewer, challenger)
3. ✅ Memory Persistence (CLAUDE.md updates)
4. ✅ Concept Declaration
5. ✅ Tool Count Limits
6. ✅ Tool Sequencing

---

## 📊 Success Criteria

### Routing System: ✅
- "Explain X" → Explainer Agent
- "Review code" → Reviewer Agent
- "Challenge me" → Challenger Agent
- "Test me" → Assessor Agent

### Memory System: ✅
- `.claude/CLAUDE.md` exists
- Session count increments
- Concepts tracked (Mastered/Learning/Weak)
- Session history logged
- Agent reads memory before teaching
- Agent doesn't re-teach mastered concepts

### Concept System: ✅
- Agent declares concepts upfront
- Maximum 3 concepts per response
- Tool usage scales with concept count
- Concept declaration format correct

### Tool System: ✅
- Tools used sequentially (not randomly)
- Visual → Code → Practice pattern
- Each tool references previous
- 2-second pacing delays between outputs

---

## 🐛 Troubleshooting

**Server won't start:**
```bash
# Kill existing processes
pkill -9 -f "python3 server.py"

# Check port
lsof -ti:5000 | xargs kill -9

# Restart
python3 server.py
```

**Tests fail:**
```bash
# Check server logs
tail -f /tmp/teaching_server.log

# Check CLAUDE.md
cat .claude/CLAUDE.md

# Reset CLAUDE.md
git checkout .claude/CLAUDE.md
```

**Import errors:**
```bash
pip3 install flask flask-cors anthropic sseclient-py
```

---

## 📈 Expected Test Results

**Passing Score: 80%+**

Example output:
```
📊 TEST SUMMARY
================================================================================
🎯 Agent Routing: 3 tests
  ✅ Explainer routing
  ✅ Reviewer routing
  ✅ Challenger routing

💾 Memory Persistence: 2 tests
  ✅ Session count
  ✅ Concept recorded

🧠 Concept System: 1 tests
  ✅ Declaration

🔧 Tool Management: 2 tests
  ✅ Count
  ✅ Sequencing

================================================================================
📈 FINAL SCORE: 8/8 (100%)
🎉 SYSTEM FULLY OPERATIONAL
```

---

## 🎯 What We're Testing

### 1. Intelligent Agent Routing
- Pattern-based query classification
- Confidence scoring
- Specialist agent selection

### 2. Persistent Memory
- `.claude/CLAUDE.md` read/write
- SDK `setting_sources=["project"]`
- Cross-session knowledge retention

### 3. Cognitive Load Management
- 3-concept maximum per response
- Working memory constraints
- Information density control

### 4. Tool Orchestration
- Sequential chaining validation
- Concept-based tool selection
- Pacing delays for absorption

---

## 📝 Next Steps After Testing

If tests pass (80%+):
✅ System is production-ready
✅ Memory persistence working
✅ Routing working
✅ Concept limits enforced

If tests partially pass (60-79%):
⚠️ Check specific failing tests
⚠️ Review server logs
⚠️ Verify CLAUDE.md permissions

If tests fail (<60%):
❌ Check server is actually running
❌ Verify all dependencies installed
❌ Review error messages
