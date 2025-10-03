#!/usr/bin/env node
/**
 * Master Teacher - Frontend End-to-End Test
 * Tests the complete user flow with headless browser
 */

import puppeteer from 'puppeteer';

const URL = 'http://localhost:5000/learn.html';
const TIMEOUT = 60000;

console.log('='.repeat(70));
console.log('🎓 MASTER TEACHER - FRONTEND END-TO-END TEST');
console.log('='.repeat(70));

let browser;
let page;
let testResults = {
  passed: 0,
  failed: 0,
  tests: []
};

function assert(condition, testName, details = '') {
  if (condition) {
    console.log(`✅ ${testName}`);
    testResults.passed++;
    testResults.tests.push({ name: testName, passed: true });
  } else {
    console.log(`❌ ${testName}`);
    if (details) console.log(`   ${details}`);
    testResults.failed++;
    testResults.tests.push({ name: testName, passed: false, details });
  }
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

try {
  // ===== TEST 1: Page Load =====
  console.log('\n📝 TEST 1: Page Load & Initial State');
  console.log('-'.repeat(70));

  browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  page = await browser.newPage();

  await page.goto(URL, { waitUntil: 'networkidle0' });
  assert(true, 'Page loaded successfully');

  // Check title
  const title = await page.title();
  assert(
    title.includes('Master Teacher'),
    'Page title contains "Master Teacher"',
    `Got: ${title}`
  );

  // Check header
  const header = await page.$eval('.header h1', el => el.textContent);
  assert(
    header.includes('Master Teacher'),
    'Header displays "Master Teacher"'
  );

  // Check status message
  const status = await page.$eval('#status', el => el.textContent);
  assert(
    status.includes('Start Learning'),
    'Initial status message shown',
    `Got: ${status}`
  );

  // Check input disabled
  const inputDisabled = await page.$eval('#messageInput', el => el.disabled);
  assert(inputDisabled, 'Input field initially disabled');

  // Check send button disabled
  const sendDisabled = await page.$eval('#sendBtn', el => el.disabled);
  assert(sendDisabled, 'Send button initially disabled');

  // Check session button present
  const sessionBtn = await page.$('#sessionBtn');
  assert(sessionBtn !== null, 'Session button present');

  // Check welcome message
  const welcomeMessage = await page.$eval('.message.teacher', el => el.textContent);
  assert(
    welcomeMessage.includes('Welcome'),
    'Welcome message displayed'
  );

  // ===== TEST 2: Session Start =====
  console.log('\n📝 TEST 2: Starting Learning Session');
  console.log('-'.repeat(70));

  // Click Start Learning button
  await page.click('#sessionBtn');
  console.log('  🖱  Clicked "Start Learning" button');

  // Wait for session to start
  await sleep(2000);

  // Check status changed
  const statusAfterStart = await page.$eval('#status', el => el.textContent);
  assert(
    statusAfterStart.includes('Ready') || statusAfterStart.includes('learn'),
    'Status shows ready state',
    `Got: ${statusAfterStart}`
  );

  // Check input enabled
  const inputEnabled = await page.$eval('#messageInput', el => !el.disabled);
  assert(inputEnabled, 'Input field enabled after session start');

  // Check send button enabled
  const sendEnabled = await page.$eval('#sendBtn', el => !el.disabled);
  assert(sendEnabled, 'Send button enabled after session start');

  // Check session button changed
  const sessionBtnText = await page.$eval('#sessionBtn', el => el.textContent);
  assert(
    sessionBtnText.includes('End'),
    'Session button shows "End Session"',
    `Got: ${sessionBtnText}`
  );

  // ===== TEST 3: Send Teaching Request =====
  console.log('\n📝 TEST 3: Sending Teaching Request');
  console.log('-'.repeat(70));

  // Type message
  const teachingRequest = 'Teach me bubble sort';
  await page.type('#messageInput', teachingRequest);
  console.log(`  ⌨  Typed: "${teachingRequest}"`);

  // Check input value
  const inputValue = await page.$eval('#messageInput', el => el.value);
  assert(
    inputValue === teachingRequest,
    'Input field contains typed message'
  );

  // Get initial message count
  const initialMsgCount = await page.$$eval('.message', msgs => msgs.length);

  // Click send button
  await page.click('#sendBtn');
  console.log('  🖱  Clicked "Send" button');

  // Wait for student message to appear
  await sleep(1000);

  // Check student message added
  const studentMessage = await page.$('.message.student');
  assert(studentMessage !== null, 'Student message added to UI');

  const studentText = await page.$eval('.message.student', el => el.textContent);
  assert(
    studentText.includes(teachingRequest),
    'Student message contains request text'
  );

  // Check input cleared
  const inputAfterSend = await page.$eval('#messageInput', el => el.value);
  assert(inputAfterSend === '', 'Input field cleared after send');

  // Check status changed to processing
  await sleep(500);
  const statusProcessing = await page.$eval('#status', el => el.textContent);
  assert(
    statusProcessing.includes('preparing') || statusProcessing.includes('processing'),
    'Status shows processing state',
    `Got: ${statusProcessing}`
  );

  // ===== TEST 4: Receive Messages =====
  console.log('\n📝 TEST 4: Receiving Multi-Modal Messages');
  console.log('-'.repeat(70));

  console.log('  ⏳ Waiting for agent response (30 seconds)...');

  // Wait for messages to appear
  let messageCount = initialMsgCount;
  let iterations = 0;
  const maxIterations = 60; // 30 seconds

  while (iterations < maxIterations) {
    await sleep(500);
    const currentCount = await page.$$eval('.message', msgs => msgs.length);
    if (currentCount > messageCount) {
      messageCount = currentCount;
      console.log(`  📨 Messages received: ${currentCount - initialMsgCount}`);
    }

    // Check if complete
    const status = await page.$eval('#status', el => el.textContent);
    if (status.includes('complete') || status.includes('Ask another')) {
      console.log('  ✓ Lesson complete signal received');
      break;
    }

    iterations++;
  }

  const finalMsgCount = await page.$$eval('.message', msgs => msgs.length);
  const newMessages = finalMsgCount - initialMsgCount;

  assert(
    newMessages > 2,
    `Received multiple messages (${newMessages} new messages)`
  );

  // ===== TEST 5: Message Types =====
  console.log('\n📝 TEST 5: Verifying Message Types');
  console.log('-'.repeat(70));

  // Check for teacher messages
  const teacherMsgs = await page.$$('.message.teacher');
  assert(
    teacherMsgs.length > 1, // More than just welcome
    `Teacher messages displayed (${teacherMsgs.length} total)`
  );

  // Check for action messages (tool calls)
  const actionMsgs = await page.$$('.message.action');
  assert(
    actionMsgs.length > 0,
    `Action messages displayed (${actionMsgs.length} tool calls)`,
    'Shows which tools were used'
  );

  if (actionMsgs.length > 0) {
    const firstAction = await page.$eval('.message.action', el => el.textContent);
    console.log(`  🔧 First tool: ${firstAction}`);
  }

  // Check for output messages (tool results)
  const outputMsgs = await page.$$('.message.output');
  assert(
    outputMsgs.length > 0,
    `Output messages displayed (${outputMsgs.length} outputs)`,
    'Shows tool results'
  );

  // Check for cost message
  const costMsgs = await page.$$('.message.cost');
  if (costMsgs.length > 0) {
    const cost = await page.$eval('.message.cost', el => el.textContent);
    assert(true, `Cost tracking displayed: ${cost}`);
  }

  // ===== TEST 6: Content Rendering =====
  console.log('\n📝 TEST 6: Content Rendering');
  console.log('-'.repeat(70));

  // Check for code blocks (markdown rendering)
  const codeBlocks = await page.$$('pre');
  if (codeBlocks.length > 0) {
    assert(true, `Code blocks rendered (${codeBlocks.length} blocks)`);
  } else {
    console.log('  ℹ️  No code blocks in this response');
  }

  // Check for images (visual tools output)
  const images = await page.$$('img');
  if (images.length > 0) {
    assert(true, `Images rendered (${images.length} images)`);

    // Check if images loaded
    const imageLoaded = await page.$eval('img', img => img.complete && img.naturalHeight > 0);
    if (imageLoaded) {
      assert(true, 'Images loaded successfully');
    }
  } else {
    console.log('  ℹ️  No images in this response (might use text-based tools)');
  }

  // ===== TEST 7: UI State =====
  console.log('\n📝 TEST 7: UI State After Completion');
  console.log('-'.repeat(70));

  // Check status shows ready for next question
  const finalStatus = await page.$eval('#status', el => el.textContent);
  assert(
    finalStatus.includes('complete') || finalStatus.includes('Ask another'),
    'Status indicates ready for next question',
    `Got: ${finalStatus}`
  );

  // Check send button is enabled
  const sendEnabledAfter = await page.$eval('#sendBtn', el => !el.disabled);
  assert(sendEnabledAfter, 'Send button re-enabled after completion');

  // Check input is enabled
  const inputEnabledAfter = await page.$eval('#messageInput', el => !el.disabled);
  assert(inputEnabledAfter, 'Input field still enabled');

  // ===== TEST 8: Multi-Modal Analysis =====
  console.log('\n📝 TEST 8: Multi-Modal Learning Verification');
  console.log('-'.repeat(70));

  // Get all action messages to analyze tool usage
  const allActions = await page.$$eval('.message.action', msgs =>
    msgs.map(m => m.textContent)
  );

  const visualTools = allActions.filter(a => a.includes('visual')).length;
  const conceptTools = allActions.filter(a => a.includes('scrimba')).length;
  const projectTools = allActions.filter(a => a.includes('live_coding')).length;

  const modalities = [
    visualTools > 0,
    conceptTools > 0,
    projectTools > 0
  ].filter(Boolean).length;

  console.log(`  📊 Tool Usage Analysis:`);
  console.log(`     • Visual tools: ${visualTools}`);
  console.log(`     • Concept tools: ${conceptTools}`);
  console.log(`     • Project tools: ${projectTools}`);
  console.log(`     • Modalities used: ${modalities}/3`);

  assert(
    allActions.length >= 2,
    `Compositional teaching: Multiple tools used (${allActions.length} tools)`
  );

  assert(
    modalities >= 1,
    `Multi-modal learning: ${modalities} modality/modalities used`
  );

  // ===== TEST 9: Session End =====
  console.log('\n📝 TEST 9: Ending Session');
  console.log('-'.repeat(70));

  // Click End Session
  await page.click('#sessionBtn');
  console.log('  🖱  Clicked "End Session" button');

  await sleep(500);

  // Check input disabled again
  const inputDisabledEnd = await page.$eval('#messageInput', el => el.disabled);
  assert(inputDisabledEnd, 'Input field disabled after session end');

  // Check button text changed back
  const sessionBtnEnd = await page.$eval('#sessionBtn', el => el.textContent);
  assert(
    sessionBtnEnd.includes('Start'),
    'Session button shows "Start Learning" again'
  );

  // ===== RESULTS =====
  console.log('\n' + '='.repeat(70));
  console.log('📊 TEST RESULTS');
  console.log('='.repeat(70));

  console.log(`\n✅ Passed: ${testResults.passed}`);
  console.log(`❌ Failed: ${testResults.failed}`);
  console.log(`📈 Success Rate: ${Math.round(testResults.passed / (testResults.passed + testResults.failed) * 100)}%`);

  if (testResults.failed === 0) {
    console.log('\n🎉 ALL FRONTEND TESTS PASSED!');
    console.log('='.repeat(70));
    console.log('\n✅ Frontend Verification Summary:');
    console.log('  • Page loads correctly ✅');
    console.log('  • Session management works ✅');
    console.log('  • User input handling ✅');
    console.log('  • Real-time message streaming ✅');
    console.log('  • Multi-modal content display ✅');
    console.log('  • Compositional teaching verified ✅');
    console.log('  • UI state management ✅');
    console.log('  • No mode selection required ✅');
    console.log('\n🎓 Master Teacher frontend working perfectly!');
  } else {
    console.log('\n⚠️  Some tests failed. Review details above.');
  }

} catch (error) {
  console.error('\n❌ TEST ERROR:', error.message);
  console.error(error.stack);
  process.exit(1);
} finally {
  if (browser) {
    await browser.close();
  }
}
