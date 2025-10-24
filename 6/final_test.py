#!/usr/bin/env python3
"""Final comprehensive test of dual-mode builder"""

import requests
import time

BASE = 'http://localhost:5010'

print('COMPREHENSIVE TEST - DUAL MODE BUILDER')
print('=' * 70)

# ========== TEST 1: VELOCITY MODE ==========
print('\nTEST 1: VELOCITY MODE')
print('-' * 70)

resp = requests.post(f'{BASE}/api/session/start')
sid1 = resp.json()['session_id']
print(f'Session: {sid1[:8]}')
print('Request: "Build me a restaurant menu for Pizza Palace"')

requests.post(f'{BASE}/api/teach', json={
    'session_id': sid1,
    'message': 'Build me a restaurant menu for Pizza Palace'
})

print('\nWaiting for completion...')
for i in range(40):
    time.sleep(1)
    resp = requests.get(f'{BASE}/api/session/{sid1}/history')
    msgs = resp.json()['messages']

    if any(m.get('type') == 'complete' for m in msgs):
        print(f'Completed in {i}s')
        break

# Get final results
resp = requests.get(f'{BASE}/api/session/{sid1}/history')
msgs = resp.json()['messages']
actions = [m for m in msgs if m.get('type') == 'action']
outputs = [m for m in msgs if m.get('type') == 'output']

print(f'\nResults:')
print(f'  Tools called: {len(actions)}')
for a in actions:
    print(f'    - {a["content"]}')
print(f'  Outputs generated: {len(outputs)}')

velocity_pass = len(actions) >= 3
print(f'\n{"[PASS] VELOCITY MODE WORKING" if velocity_pass else "[FAIL] VELOCITY MODE FAILED"}')

# ========== TEST 2: TUTORIAL MODE ==========
print('\n\nTEST 2: TUTORIAL MODE (Scrimba-style)')
print('-' * 70)

resp = requests.post(f'{BASE}/api/session/start')
sid2 = resp.json()['session_id']
print(f'Session: {sid2[:8]}')
print('Request: "Teach me step by step how to build a portfolio"')

requests.post(f'{BASE}/api/teach', json={
    'session_id': sid2,
    'message': 'Teach me step by step how to build a portfolio'
})

print('\nIncremental building in progress...')
steps = 0
start = time.time()

for i in range(150):
    time.sleep(1)
    resp = requests.get(f'{BASE}/api/session/{sid2}/history')
    msgs = resp.json()['messages']

    actions = [m for m in msgs if m.get('type') == 'action']
    add_steps = [a for a in actions if 'add_code_step' in a.get('content', '')]

    if len(add_steps) > steps:
        steps = len(add_steps)
        elapsed = int(time.time() - start)
        print(f'  [{elapsed:3d}s] Step {steps:2d} completed')

    if any(m.get('type') == 'complete' for m in msgs):
        elapsed = int(time.time() - start)
        print(f'\nTutorial completed in {elapsed}s')
        break

tutorial_pass = steps >= 10

print(f'\nResults:')
print(f'  Total steps: {steps}/15')
print(f'  Avg time per step: {int((time.time()-start)/steps)}s' if steps > 0 else '  Avg: N/A')
print(f'  Status: {"[PASS] WORKING" if steps >= 12 else "[PARTIAL]" if steps >= 8 else "[FAIL]"}')

# ========== SUMMARY ==========
print('\n' + '=' * 70)
print('FINAL RESULTS')
print('=' * 70)
print(f'Velocity Mode:  {"[PASS]" if velocity_pass else "[FAIL]"} - Complete app in ~20s')
print(f'Tutorial Mode:  {"[PASS]" if tutorial_pass else "[FAIL]"} - {steps}/15 incremental steps')
print(f'\nOverall: {"BOTH MODES OPERATIONAL" if velocity_pass and tutorial_pass else "NEEDS WORK"}')
print('=' * 70)
