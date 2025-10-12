# Concept-Based Socratic Questioning System
## Comprehensive Implementation Guide

**Version:** 1.0
**Date:** October 12, 2025
**Purpose:** AI-led proactive questioning to enhance learning rate through active recall

---

## Table of Contents

1. [Core Architecture](#core-architecture)
2. [Logic Flow](#logic-flow)
3. [Execution Flow](#execution-flow)
4. [State Machine](#state-machine)
5. [Integration Points](#integration-points)
6. [Implementation Details](#implementation-details)
7. [Edge Cases](#edge-cases)
8. [Testing Strategy](#testing-strategy)

---

## Core Architecture

### **Principle**
**Concept-driven, not time-driven.** Questions are triggered by concept milestones, not arbitrary timers.

### **Components**

```
┌──────────────────────────────────────────────────────────┐
│                    TEACHING SESSION                       │
│                                                           │
│  ┌─────────────────┐      ┌──────────────────┐          │
│  │  Teaching Agent │─────▶│ Concept Tracker  │          │
│  │    (Claude)     │      │  (existing)      │          │
│  └─────────────────┘      └──────────────────┘          │
│           │                        │                      │
│           │                        │ concept_taught       │
│           │                        ▼                      │
│           │         ┌──────────────────────────┐         │
│           │         │  Socratic Question       │         │
│           │         │  Engine (NEW)            │         │
│           │         └──────────────────────────┘         │
│           │                        │                      │
│           │            ┌───────────┴────────────┐        │
│           │            │                        │         │
│           │            ▼                        ▼         │
│           │    ┌──────────────┐       ┌────────────┐    │
│           │    │  Question    │       │  Answer    │    │
│           │    │  Generator   │       │  Evaluator │    │
│           │    └──────────────┘       └────────────┘    │
│           │            │                        │         │
│           │            ▼                        ▼         │
│           └────────────────────┬────────────────┘        │
│                                ▼                          │
│                    ┌───────────────────┐                 │
│                    │  Message Queue    │                 │
│                    │  (to frontend)    │                 │
│                    └───────────────────┘                 │
└──────────────────────────────────────────────────────────┘
```

### **Key Data Structures**

```python
class ConceptState:
    """Tracks state of each taught concept"""
    concept_name: str
    taught_at: datetime
    questioned: bool = False
    question_asked: str = None
    student_answer: str = None
    understood: bool = None
    verification_attempts: int = 0

class QuestioningState:
    """Session-wide questioning state"""
    concepts_taught: List[ConceptState] = []
    concepts_since_checkpoint: int = 0
    last_checkpoint_at: int = 0  # concept count, not time
    total_questions_asked: int = 0
    verification_mode: bool = False
    waiting_for_answer: bool = False
    current_question: Optional[Question] = None
```

---

## Logic Flow

### **1. Concept Detection Logic**

```
┌─────────────────────────────────────────────────────┐
│         Agent Finishes Teaching Response            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│   Extract Declared Concepts from Response           │
│   (via existing ConceptTracker)                     │
└─────────────────────────────────────────────────────┘
                        ↓
                 ┌─────────────┐
                 │ New Concept?│
                 └─────────────┘
                    ↙         ↘
                 YES           NO
                  ↓             ↓
    ┌─────────────────────┐   [Continue]
    │ Add to ConceptState │
    └─────────────────────┘
                ↓
    ┌─────────────────────────────────┐
    │ TRIGGER: on_concept_taught()    │
    └─────────────────────────────────┘
```

### **2. Question Trigger Logic**

```
┌────────────────────────────────────────────────────────┐
│              on_concept_taught(concept)                │
└────────────────────────────────────────────────────────┘
                        ↓
            ┌──────────────────────┐
            │ Is concept already   │
            │ questioned?          │
            └──────────────────────┘
                   ↙        ↘
                YES          NO
                 ↓            ↓
            [Skip]    ┌────────────────────┐
                      │ TRIGGER 1:         │
                      │ Comprehension Check│
                      └────────────────────┘
                                ↓
                    ┌──────────────────────────┐
                    │ Generate question for    │
                    │ this specific concept    │
                    └──────────────────────────┘
                                ↓
                    ┌──────────────────────────┐
                    │ Inject question into     │
                    │ conversation stream      │
                    └──────────────────────────┘
                                ↓
                    ┌──────────────────────────┐
                    │ Set waiting_for_answer   │
                    │ = True                   │
                    └──────────────────────────┘
                                ↓
                    ┌──────────────────────────┐
                    │ Increment                │
                    │ concepts_since_checkpoint│
                    └──────────────────────────┘
                                ↓
                    ┌──────────────────────────┐
                    │ Check if checkpoint due  │
                    │ (% 3 == 0)               │
                    └──────────────────────────┘
                           ↙          ↘
                        YES            NO
                         ↓              ↓
            ┌────────────────────┐  [Continue]
            │ TRIGGER 3:         │
            │ Checkpoint Quiz    │
            └────────────────────┘
```

### **3. Student Response Logic**

```
┌─────────────────────────────────────────────────────┐
│           Student Sends Message                      │
└─────────────────────────────────────────────────────┘
                        ↓
            ┌──────────────────────┐
            │ Is system waiting    │
            │ for answer?          │
            └──────────────────────┘
                   ↙        ↘
                YES          NO
                 ↓            ↓
    ┌─────────────────────┐  ┌─────────────────────────┐
    │ Process as answer   │  │ Check for understanding │
    │ to question         │  │ claims ("got it", etc)  │
    └─────────────────────┘  └─────────────────────────┘
                ↓                         ↓
    ┌─────────────────────┐         ┌─────────┐
    │ Evaluate answer     │         │ Claim?  │
    └─────────────────────┘         └─────────┘
                ↓                      ↙      ↘
         ┌──────────┐              YES        NO
         │ Score    │               ↓          ↓
         └──────────┘    ┌──────────────┐ [Continue
            ↙      ↘      │ TRIGGER 2:   │  Normal]
        HIGH      LOW     │ Verification │
         ↓          ↓     └──────────────┘
    ┌─────┐  ┌─────────┐
    │Mark │  │Ask      │
    │Under│  │Follow-up│
    │stood│  │Question │
    └─────┘  └─────────┘
       ↓          ↓
    ┌─────────────────────┐
    │ Clear waiting state │
    │ Continue teaching   │
    └─────────────────────┘
```

### **4. Question Generation Logic**

```
┌─────────────────────────────────────────────────────┐
│           generate_question(concept, type)           │
└─────────────────────────────────────────────────────┘
                        ↓
            ┌──────────────────────┐
            │ Question Type?       │
            └──────────────────────┘
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│COMPREHENSION│  │VERIFICATION │  │ CHECKPOINT  │
└─────────────┘  └─────────────┘  └─────────────┘
        ↓               ↓               ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│"Explain X   │  │"Show me X   │  │"Compare X,  │
│in your own  │  │by doing Y"  │  │Y, Z"        │
│words"       │  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
        ↓               ↓               ↓
┌──────────────────────────────────────────────┐
│  Personalize based on:                       │
│  - Student level                             │
│  - Previous answers                          │
│  - Concept difficulty                        │
└──────────────────────────────────────────────┘
                        ↓
            ┌──────────────────────┐
            │ Return Question obj  │
            └──────────────────────┘
```

---

## Execution Flow

### **Sequence Diagram: Single Concept Cycle**

```
Student    Frontend    Backend     ConceptTracker    QuestionEngine    Agent
  │           │           │               │                │            │
  │  "explain │           │               │                │            │
  │   arrays" │           │               │                │            │
  ├──────────►├──────────►│               │                │            │
  │           │           │  teach()      │                │            │
  │           │           ├──────────────────────────────────────────►  │
  │           │           │               │                │            │
  │           │           │◄──────────────────────────────────────────┤ │
  │           │           │  response: "Arrays store..."  │            │
  │           │           │               │                │            │
  │           │  stream   │               │                │            │
  │◄──────────┤◄──────────┤               │                │            │
  │  "Arrays  │           │               │                │            │
  │   store..." │         │               │                │            │
  │           │           │  on_complete()│                │            │
  │           │           ├──────────────►│                │            │
  │           │           │               │ concept: "arrays"           │
  │           │           │               ├────────────────►            │
  │           │           │               │                │            │
  │           │           │               │  generate_question()        │
  │           │           │               │◄────────────────┤            │
  │           │           │               │ "Explain arrays"            │
  │           │           │◄──────────────┤                │            │
  │           │  inject_  │               │                │            │
  │           │  question │               │                │            │
  │◄──────────┤◄──────────┤               │                │            │
  │ "Explain  │           │               │                │            │
  │  arrays?" │           │               │                │            │
  │           │           │  [WAITING]    │                │            │
  │  "stores  │           │               │                │            │
  │   data"   │           │               │                │            │
  ├──────────►├──────────►│               │                │            │
  │           │           │  evaluate()   │                │            │
  │           │           ├──────────────────────────────►  │            │
  │           │           │               │  score: 0.8    │            │
  │           │           │◄──────────────────────────────┤  │            │
  │           │           │               │  understood: true           │
  │           │           │  continue     │                │            │
  │           │  "Good!"  │  teaching     │                │            │
  │◄──────────┤◄──────────┤               │                │            │
```

### **Sequence Diagram: Checkpoint Quiz (3 Concepts)**

```
ConceptTracker    QuestionEngine         Agent          Frontend
      │                 │                   │                │
      │  concept_3      │                   │                │
      │  taught         │                   │                │
      ├────────────────►│                   │                │
      │                 │                   │                │
      │                 │  concepts_since   │                │
      │                 │  checkpoint == 3  │                │
      │                 │  [CHECKPOINT]     │                │
      │                 │                   │                │
      │                 │  generate_quiz()  │                │
      │                 │  (concept_1,      │                │
      │                 │   concept_2,      │                │
      │                 │   concept_3)      │                │
      │                 ├──────────────────►│                │
      │                 │                   │                │
      │                 │◄──────────────────┤                │
      │                 │  quiz_question    │                │
      │                 │                   │                │
      │                 │  inject_question()│                │
      │                 ├─────────────────────────────────► │
      │                 │  "Compare A, B, C?"               │
      │                 │                   │                │
      │                 │  [WAITING]        │                │
      │                 │                   │                │
      │                 │◄─────────────────────────────────┤ │
      │                 │  student_answer   │                │
      │                 │                   │                │
      │                 │  evaluate_quiz()  │                │
      │                 │                   │                │
      │                 │  reset_checkpoint │                │
      │                 │  counter = 0      │                │
```

---

## State Machine

### **Question Engine States**

```
┌─────────────────────────────────────────────────────────┐
│                    IDLE STATE                            │
│  - No questions pending                                  │
│  - Monitoring for concept events                         │
└─────────────────────────────────────────────────────────┘
                        │
                        │ on_concept_taught()
                        ↓
┌─────────────────────────────────────────────────────────┐
│              QUESTION_GENERATED STATE                    │
│  - Question created                                      │
│  - Ready to inject                                       │
└─────────────────────────────────────────────────────────┘
                        │
                        │ inject_question()
                        ↓
┌─────────────────────────────────────────────────────────┐
│              WAITING_FOR_ANSWER STATE                    │
│  - Question sent to student                              │
│  - Blocking further teaching                             │
│  - Timeout: 120 seconds                                  │
└─────────────────────────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    answer_received  timeout     student_claims_stuck
         ↓              ↓              ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ EVALUATING  │  │  TIMEOUT    │  │  HINT       │
│    STATE    │  │   STATE     │  │  STATE      │
└─────────────┘  └─────────────┘  └─────────────┘
         │              │              │
         ↓              ↓              ↓
    ┌────────────────────────────────────┐
    │       FEEDBACK STATE               │
    │  - Show result                     │
    │  - Update concept understanding    │
    └────────────────────────────────────┘
                        │
                        ↓
    ┌────────────────────────────────────┐
    │  Check if checkpoint due           │
    └────────────────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         ↓                             ↓
    CHECKPOINT_QUIZ              Return to IDLE
         │
         └──────────────► WAITING_FOR_ANSWER
```

### **State Transitions**

```python
class QuestionState(Enum):
    IDLE = "idle"
    QUESTION_GENERATED = "question_generated"
    WAITING_FOR_ANSWER = "waiting_for_answer"
    EVALUATING = "evaluating"
    TIMEOUT = "timeout"
    HINT = "hint"
    FEEDBACK = "feedback"
    CHECKPOINT_QUIZ = "checkpoint_quiz"

VALID_TRANSITIONS = {
    QuestionState.IDLE: [QuestionState.QUESTION_GENERATED],
    QuestionState.QUESTION_GENERATED: [QuestionState.WAITING_FOR_ANSWER],
    QuestionState.WAITING_FOR_ANSWER: [
        QuestionState.EVALUATING,
        QuestionState.TIMEOUT,
        QuestionState.HINT
    ],
    QuestionState.EVALUATING: [QuestionState.FEEDBACK],
    QuestionState.TIMEOUT: [QuestionState.FEEDBACK, QuestionState.HINT],
    QuestionState.HINT: [QuestionState.WAITING_FOR_ANSWER],
    QuestionState.FEEDBACK: [
        QuestionState.IDLE,
        QuestionState.CHECKPOINT_QUIZ
    ],
    QuestionState.CHECKPOINT_QUIZ: [QuestionState.WAITING_FOR_ANSWER]
}
```

---

## Integration Points

### **1. Concept Tracker Integration**

```python
# In concept_tracker.py (EXISTING)

class ConceptBasedPermissionSystem:
    def __init__(self, session_id):
        # ... existing code ...
        self.question_engine = None  # NEW: set by session

    def record_concept(self, concept_name):
        """Called when agent declares a concept"""
        # ... existing code ...

        # NEW: Notify question engine
        if self.question_engine:
            asyncio.create_task(
                self.question_engine.on_concept_taught(concept_name)
            )
```

### **2. Session Integration**

```python
# In server.py - UnifiedSession

class UnifiedSession:
    def __init__(self, session_id):
        # ... existing code ...

        # NEW: Question engine
        self.question_engine = SocraticQuestionEngine(
            session=self,
            concept_tracker=self.concept_permission.tracker
        )

        # Link question engine to concept tracker
        self.concept_permission.question_engine = self.question_engine

    async def teach(self, instruction):
        # ... existing teaching logic ...

        # After agent responds
        async for msg in self.client.receive_response():
            formatted = self._format_message(msg)

            # NEW: Check if agent finished responding
            if isinstance(msg, ResultMessage):
                # Agent done - question engine can activate
                await self.question_engine.on_agent_complete()
```

### **3. Message Queue Integration**

```python
# Question engine injects questions into same SSE stream

def inject_question(self, question, requires_response=True):
    """Inject question into conversation stream"""

    question_msg = {
        "type": "teacher_question",  # NEW message type
        "content": question.text,
        "question_id": question.id,
        "question_type": question.type,
        "concept": question.concept,
        "requires_response": requires_response,
        "timeout": 120,  # seconds
        "timestamp": datetime.now().isoformat()
    }

    # Push to same queue as teaching messages
    if self.session_id in message_queues:
        message_queues[self.session_id].put(question_msg)

    # Set waiting state
    self.state = QuestionState.WAITING_FOR_ANSWER
    self.waiting_for_answer = True
```

### **4. Frontend Integration**

```javascript
// In learn.html (FRONTEND)

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // NEW: Handle teacher questions
    if (data.type === 'teacher_question') {
        displayTeacherQuestion(data);
        enableResponseMode(data.question_id);
        startQuestionTimer(data.timeout);
    }
    // ... existing message handlers ...
};

function displayTeacherQuestion(questionData) {
    // Highlight question differently
    const questionDiv = document.createElement('div');
    questionDiv.className = 'teacher-question';
    questionDiv.innerHTML = `
        <div class="question-badge">❓ Question</div>
        <div class="question-text">${questionData.content}</div>
        <div class="question-prompt">Your answer:</div>
    `;
    messagesDiv.appendChild(questionDiv);

    // Focus input
    messageInput.focus();
    messageInput.placeholder = "Teacher is waiting for your answer...";
}

function enableResponseMode(questionId) {
    // Mark next message as answer to question
    currentQuestionId = questionId;
    isAnsweringQuestion = true;
}
```

---

## Implementation Details

### **File Structure**

```
6/
├── tools/
│   └── socratic_tools.py              (NEW)
├── services/
│   ├── question_engine.py             (NEW)
│   ├── question_generator.py          (NEW)
│   └── answer_evaluator.py            (NEW)
├── server.py                          (MODIFY)
├── concept_tracker.py                 (MODIFY)
└── learn.html                         (MODIFY)
```

### **Core Classes**

#### **1. SocraticQuestionEngine**

```python
# services/question_engine.py

class SocraticQuestionEngine:
    """Main orchestrator for concept-based questioning"""

    def __init__(self, session, concept_tracker):
        self.session = session
        self.concept_tracker = concept_tracker
        self.state = QuestionState.IDLE
        self.questioning_state = QuestioningState()
        self.generator = QuestionGenerator()
        self.evaluator = AnswerEvaluator()

    async def on_concept_taught(self, concept_name: str):
        """TRIGGER 1: Called when concept is taught"""

        # Skip if already questioned
        if self._already_questioned(concept_name):
            return

        # Generate comprehension question
        question = self.generator.generate_comprehension_question(
            concept=concept_name,
            student_level=self.session.knowledge.get_level(),
            context=self._get_teaching_context()
        )

        # Inject question
        await self._inject_question(question)

        # Update state
        concept_state = ConceptState(
            concept_name=concept_name,
            taught_at=datetime.now(),
            questioned=True,
            question_asked=question.text
        )
        self.questioning_state.concepts_taught.append(concept_state)
        self.questioning_state.concepts_since_checkpoint += 1

        # Check checkpoint
        if self.questioning_state.concepts_since_checkpoint >= 3:
            await self._trigger_checkpoint()

    async def on_student_message(self, message: str):
        """Process student message"""

        # CASE 1: Answering question
        if self.state == QuestionState.WAITING_FOR_ANSWER:
            await self._process_answer(message)
            return

        # CASE 2: Claims understanding (TRIGGER 2)
        if self._contains_understanding_claim(message):
            await self._trigger_verification()
            return

    async def _process_answer(self, answer: str):
        """Evaluate student answer"""
        self.state = QuestionState.EVALUATING

        current_question = self.questioning_state.current_question
        current_concept = self._get_current_concept()

        # Evaluate answer
        evaluation = await self.evaluator.evaluate(
            question=current_question,
            answer=answer,
            concept=current_concept.concept_name,
            student_level=self.session.knowledge.get_level()
        )

        # Update concept state
        current_concept.student_answer = answer
        current_concept.understood = evaluation.score > 0.7
        current_concept.verification_attempts += 1

        # Send feedback
        await self._send_feedback(evaluation)

        # Return to idle
        self.state = QuestionState.IDLE
        self.questioning_state.waiting_for_answer = False

    async def _trigger_checkpoint(self):
        """TRIGGER 3: Checkpoint quiz every 3 concepts"""

        recent_concepts = self.questioning_state.concepts_taught[-3:]

        checkpoint_question = self.generator.generate_checkpoint_quiz(
            concepts=[c.concept_name for c in recent_concepts],
            student_level=self.session.knowledge.get_level()
        )

        self.state = QuestionState.CHECKPOINT_QUIZ
        await self._inject_question(checkpoint_question)

        # Reset checkpoint counter
        self.questioning_state.concepts_since_checkpoint = 0
        self.questioning_state.last_checkpoint_at = len(
            self.questioning_state.concepts_taught
        )

    async def _inject_question(self, question):
        """Inject question into message stream"""

        question_msg = {
            "type": "teacher_question",
            "content": question.text,
            "question_id": question.id,
            "question_type": question.type,
            "concept": question.concept,
            "requires_response": True,
            "timestamp": datetime.now().isoformat()
        }

        # Add to message queue
        if self.session.session_id in message_queues:
            message_queues[self.session.session_id].put(question_msg)

        # Update state
        self.state = QuestionState.WAITING_FOR_ANSWER
        self.questioning_state.waiting_for_answer = True
        self.questioning_state.current_question = question

    def _contains_understanding_claim(self, message: str) -> bool:
        """TRIGGER 2: Detect understanding claims"""
        claims = [
            "got it", "i understand", "makes sense", "i see",
            "clear", "understand", "got that", "okay", "ok i see"
        ]
        message_lower = message.lower()
        return any(claim in message_lower for claim in claims)
```

#### **2. QuestionGenerator**

```python
# services/question_generator.py

class QuestionGenerator:
    """Generates personalized questions"""

    def generate_comprehension_question(
        self,
        concept: str,
        student_level: str,
        context: dict
    ) -> Question:
        """Generate comprehension check question"""

        # Question templates by concept type
        templates = self._get_templates(concept, student_level)

        # Select appropriate template
        template = self._select_template(templates, context)

        # Generate question
        question_text = template.format(concept=concept)

        return Question(
            id=str(uuid.uuid4()),
            text=question_text,
            type=QuestionType.COMPREHENSION,
            concept=concept,
            expected_keywords=self._extract_keywords(concept),
            difficulty=self._calculate_difficulty(student_level)
        )

    def generate_checkpoint_quiz(
        self,
        concepts: List[str],
        student_level: str
    ) -> Question:
        """Generate checkpoint quiz comparing concepts"""

        if len(concepts) == 2:
            question_text = f"What's the key difference between {concepts[0]} and {concepts[1]}?"
        elif len(concepts) == 3:
            question_text = f"Compare {concepts[0]}, {concepts[1]}, and {concepts[2]}. What distinguishes each?"
        else:
            question_text = f"Summarize what you've learned about: {', '.join(concepts)}"

        return Question(
            id=str(uuid.uuid4()),
            text=question_text,
            type=QuestionType.CHECKPOINT,
            concept=", ".join(concepts),
            expected_keywords=self._extract_keywords_multi(concepts),
            difficulty="medium"
        )

    def generate_verification_question(
        self,
        concept: str,
        student_level: str
    ) -> Question:
        """Generate verification question when student claims understanding"""

        # Application-based questions
        templates = [
            f"Show me how you'd use {concept} to solve this: [example]",
            f"Can you write a quick example of {concept}?",
            f"What would happen if you changed X in {concept}?",
        ]

        template = random.choice(templates)

        return Question(
            id=str(uuid.uuid4()),
            text=template,
            type=QuestionType.VERIFICATION,
            concept=concept,
            expected_keywords=self._extract_keywords(concept),
            difficulty="medium"
        )

    def _get_templates(self, concept: str, level: str) -> List[str]:
        """Get question templates based on concept and level"""

        if level == "beginner":
            return [
                f"In simple terms, what is {concept}?",
                f"Can you explain {concept} like I'm 10 years old?",
                f"What does {concept} do?"
            ]
        elif level == "intermediate":
            return [
                f"Explain how {concept} works in your own words.",
                f"What's the purpose of {concept}?",
                f"When would you use {concept}?"
            ]
        else:  # advanced
            return [
                f"What are the trade-offs of using {concept}?",
                f"How does {concept} compare to alternatives?",
                f"Explain the implementation of {concept}."
            ]
```

#### **3. AnswerEvaluator**

```python
# services/answer_evaluator.py

class AnswerEvaluator:
    """Evaluates student answers using AI"""

    async def evaluate(
        self,
        question: Question,
        answer: str,
        concept: str,
        student_level: str
    ) -> AnswerEvaluation:
        """Evaluate answer quality"""

        # Use Claude for evaluation
        evaluation_prompt = f"""Evaluate this student's answer:

Question: {question.text}
Concept: {concept}
Student Answer: {answer}
Student Level: {student_level}

Evaluate on a scale of 0-1:
- Correctness: Does it answer the question?
- Completeness: Does it cover key points?
- Understanding: Does student truly understand?

Expected keywords: {question.expected_keywords}

Return JSON:
{{
    "score": 0.0-1.0,
    "correctness": 0.0-1.0,
    "completeness": 0.0-1.0,
    "understanding_level": 0.0-1.0,
    "missing_points": ["point1", "point2"],
    "strengths": ["strength1"],
    "feedback": "constructive feedback"
}}"""

        # Call Claude for evaluation
        response = await self._call_claude(evaluation_prompt)
        evaluation_data = json.loads(response)

        return AnswerEvaluation(
            score=evaluation_data["score"],
            correctness=evaluation_data["correctness"],
            completeness=evaluation_data["completeness"],
            understanding_level=evaluation_data["understanding_level"],
            missing_points=evaluation_data["missing_points"],
            strengths=evaluation_data["strengths"],
            feedback=evaluation_data["feedback"]
        )

    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API for evaluation"""
        # Use existing claude client
        # ... implementation ...
```

#### **4. MCP Tools for Socratic System**

```python
# tools/socratic_tools.py

@tool(
    "inject_socratic_question",
    "Inject a question into the conversation to check understanding",
    {"concept": str, "question_text": str, "question_type": str}
)
async def inject_socratic_question(args):
    """Called by question engine to inject questions"""

    concept = args["concept"]
    question_text = args["question_text"]
    question_type = args["question_type"]
    session_id = args.get("session_id")

    # Create question object
    question = Question(
        id=str(uuid.uuid4()),
        text=question_text,
        type=question_type,
        concept=concept
    )

    # Get session
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    # Inject via question engine
    await session.question_engine._inject_question(question)

    return {
        "status": "question_injected",
        "question_id": question.id,
        "waiting_for_answer": True
    }


@tool(
    "evaluate_student_answer",
    "Evaluate a student's answer to a Socratic question",
    {"question_id": str, "answer": str, "concept": str}
)
async def evaluate_student_answer(args):
    """Evaluate student's answer"""

    question_id = args["question_id"]
    answer = args["answer"]
    concept = args["concept"]
    session_id = args.get("session_id")

    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    # Find question
    question = session.question_engine._find_question(question_id)

    # Evaluate
    evaluation = await session.question_engine.evaluator.evaluate(
        question=question,
        answer=answer,
        concept=concept,
        student_level=session.knowledge.get_level()
    )

    return {
        "score": evaluation.score,
        "understood": evaluation.score > 0.7,
        "feedback": evaluation.feedback,
        "strengths": evaluation.strengths,
        "missing_points": evaluation.missing_points
    }
```

---

## Edge Cases

### **1. Student Doesn't Answer**

```python
async def _handle_timeout(self):
    """Handle no response after 120 seconds"""

    self.state = QuestionState.TIMEOUT

    timeout_msg = {
        "type": "teacher_prompt",
        "content": "Still thinking? Take your time, or say 'hint' if you're stuck.",
        "timestamp": datetime.now().isoformat()
    }

    message_queues[self.session_id].put(timeout_msg)

    # Wait another 60 seconds
    await asyncio.sleep(60)

    # Still no answer - provide hint
    if self.state == QuestionState.TIMEOUT:
        await self._provide_hint()
```

### **2. Student Says "I Don't Know"**

```python
async def on_student_message(self, message: str):
    # ... existing code ...

    # Check for "don't know" patterns
    if self._is_dont_know(message):
        await self._handle_dont_know()
        return

def _is_dont_know(self, message: str) -> bool:
    patterns = ["don't know", "dont know", "no idea", "not sure", "idk"]
    return any(p in message.lower() for p in patterns)

async def _handle_dont_know(self):
    """Student explicitly doesn't know"""

    # Don't penalize - provide teaching moment
    hint_msg = {
        "type": "teacher_hint",
        "content": "That's okay! Let me give you a hint: ...",
        "timestamp": datetime.now().isoformat()
    }

    message_queues[self.session_id].put(hint_msg)

    # Mark concept as not understood
    current_concept = self._get_current_concept()
    current_concept.understood = False

    # Agent should re-explain
    await self._request_re_explanation()
```

### **3. Multiple Concepts in One Response**

```python
async def on_agent_complete(self):
    """Called after agent finishes response"""

    # Get new concepts taught in this response
    new_concepts = self._get_new_concepts_taught()

    if len(new_concepts) == 0:
        return  # No new concepts

    elif len(new_concepts) == 1:
        # Standard flow
        await self.on_concept_taught(new_concepts[0])

    else:
        # Multiple concepts - ask about most recent
        most_recent = new_concepts[-1]
        await self.on_concept_taught(most_recent)

        # Queue others for checkpoint
        for concept in new_concepts[:-1]:
            self._mark_for_checkpoint(concept)
```

### **4. Wrong Answer**

```python
async def _process_answer(self, answer: str):
    # ... evaluation code ...

    if evaluation.score < 0.5:
        # Significantly wrong
        await self._handle_wrong_answer(evaluation)
    elif evaluation.score < 0.7:
        # Partially correct
        await self._handle_partial_answer(evaluation)
    else:
        # Correct
        await self._handle_correct_answer(evaluation)

async def _handle_wrong_answer(self, evaluation):
    """Student got it wrong"""

    feedback_msg = {
        "type": "teacher_feedback",
        "content": f"Not quite. {evaluation.feedback}. Let me explain again...",
        "score": evaluation.score,
        "timestamp": datetime.now().isoformat()
    }

    message_queues[self.session_id].put(feedback_msg)

    # Mark concept as not understood
    current_concept = self._get_current_concept()
    current_concept.understood = False

    # Request agent to re-explain
    await self._request_re_explanation(current_concept.concept_name)
```

### **5. Student Skips Ahead**

```python
async def on_student_message(self, message: str):
    # ... existing checks ...

    # Check if student is asking new question while we're waiting
    if self.state == QuestionState.WAITING_FOR_ANSWER:
        if self._is_new_question(message):
            # Student wants to move on
            skip_msg = {
                "type": "teacher_reminder",
                "content": "Hold on - can you answer my question first? Or say 'skip' if you want to move on.",
                "timestamp": datetime.now().isoformat()
            }
            message_queues[self.session_id].put(skip_msg)
            return

    if "skip" in message.lower() and self.state == QuestionState.WAITING_FOR_ANSWER:
        await self._handle_skip()

async def _handle_skip(self):
    """Student explicitly wants to skip question"""

    # Mark concept as unverified
    current_concept = self._get_current_concept()
    current_concept.understood = None
    current_concept.skipped = True

    # Return to idle
    self.state = QuestionState.IDLE
    self.questioning_state.waiting_for_answer = False

    skip_response = {
        "type": "teacher",
        "content": "Okay, we'll come back to this later. What did you want to ask?",
        "timestamp": datetime.now().isoformat()
    }

    message_queues[self.session_id].put(skip_response)
```

---

## Testing Strategy

### **Unit Tests**

```python
# tests/test_question_engine.py

class TestQuestionEngine:

    def test_single_concept_triggers_question(self):
        """Test TRIGGER 1: Question after concept"""
        engine = SocraticQuestionEngine(mock_session, mock_tracker)

        await engine.on_concept_taught("arrays")

        assert engine.state == QuestionState.WAITING_FOR_ANSWER
        assert len(engine.questioning_state.concepts_taught) == 1

    def test_three_concepts_triggers_checkpoint(self):
        """Test TRIGGER 3: Checkpoint after 3 concepts"""
        engine = SocraticQuestionEngine(mock_session, mock_tracker)

        await engine.on_concept_taught("arrays")
        await engine.on_concept_taught("loops")
        await engine.on_concept_taught("functions")

        assert engine.questioning_state.concepts_since_checkpoint == 0
        assert engine.state == QuestionState.CHECKPOINT_QUIZ

    def test_understanding_claim_triggers_verification(self):
        """Test TRIGGER 2: Verification question"""
        engine = SocraticQuestionEngine(mock_session, mock_tracker)

        await engine.on_student_message("I got it now")

        assert engine.state == QuestionState.WAITING_FOR_ANSWER
        # Should have verification question
```

### **Integration Tests**

```python
# tests/test_socratic_integration.py

class TestSocraticIntegration:

    async def test_full_teaching_cycle(self):
        """Test complete flow: teach → question → answer → continue"""

        session = create_test_session()

        # Teach concept
        await session.teach("Explain arrays")

        # Should receive question
        question = await get_next_message(session)
        assert question["type"] == "teacher_question"
        assert "array" in question["content"].lower()

        # Answer question
        await session.process_student_input("Arrays store multiple values")

        # Should receive feedback
        feedback = await get_next_message(session)
        assert feedback["type"] == "teacher_feedback"

    async def test_checkpoint_after_three_concepts(self):
        """Test checkpoint quiz integration"""

        session = create_test_session()

        # Teach 3 concepts
        await session.teach("Explain arrays")
        await answer_question(session, "stores values")

        await session.teach("Explain loops")
        await answer_question(session, "repeats code")

        await session.teach("Explain functions")
        await answer_question(session, "reusable code")

        # Should get checkpoint quiz
        checkpoint = await get_next_message(session)
        assert checkpoint["type"] == "teacher_question"
        assert checkpoint["question_type"] == "checkpoint"
```

### **Load Tests**

```python
# tests/test_socratic_performance.py

async def test_many_concurrent_sessions():
    """Test 100 concurrent sessions with questions"""

    sessions = [create_test_session() for _ in range(100)]

    tasks = [
        session.teach("Explain recursion")
        for session in sessions
    ]

    await asyncio.gather(*tasks)

    # All should have questions
    for session in sessions:
        assert session.question_engine.state != QuestionState.IDLE
```

---

## Performance Considerations

### **Optimization 1: Question Generation Caching**

```python
class QuestionGenerator:
    def __init__(self):
        self.cache = {}  # concept -> questions

    def generate_comprehension_question(self, concept, ...):
        # Check cache first
        if concept in self.cache:
            return self.cache[concept]

        # Generate and cache
        question = self._generate(concept, ...)
        self.cache[concept] = question
        return question
```

### **Optimization 2: Async Answer Evaluation**

```python
# Don't block on evaluation
async def _process_answer(self, answer: str):
    # Immediately acknowledge
    ack_msg = {"type": "teacher", "content": "Let me think about that..."}
    message_queues[self.session_id].put(ack_msg)

    # Evaluate in background
    evaluation = await self.evaluator.evaluate(...)

    # Send feedback
    await self._send_feedback(evaluation)
```

### **Optimization 3: Batched Checkpoint Questions**

```python
# Generate all checkpoint questions at once
async def _trigger_checkpoint(self):
    recent_concepts = self.questioning_state.concepts_taught[-3:]

    # Generate multiple questions in parallel
    questions = await asyncio.gather(*[
        self.generator.generate_checkpoint_quiz(concepts)
        for concepts in self._get_concept_combinations(recent_concepts)
    ])

    # Ask best question
    best_question = self._select_best_question(questions)
    await self._inject_question(best_question)
```

---

## Configuration

### **Socratic Mode Settings**

```python
# In server.py or config file

SOCRATIC_CONFIG = {
    "enabled": True,
    "checkpoint_frequency": 3,  # Ask checkpoint every N concepts
    "timeout_seconds": 120,     # Wait for answer
    "hint_after_timeout": True,
    "re_explain_on_wrong": True,
    "skip_allowed": True,
    "verification_on_claim": True,  # TRIGGER 2
    "difficulty_adaptation": True,
}

# Per-student override
class StudentSocraticSettings:
    checkpoint_frequency: int = 3
    timeout_seconds: int = 120
    hints_enabled: bool = True
    verification_enabled: bool = True
```

---

## Deployment Checklist

- [ ] Add `services/question_engine.py`
- [ ] Add `services/question_generator.py`
- [ ] Add `services/answer_evaluator.py`
- [ ] Add `tools/socratic_tools.py`
- [ ] Modify `server.py` - integrate question engine
- [ ] Modify `concept_tracker.py` - add callback
- [ ] Modify `learn.html` - handle question messages
- [ ] Add database tables for question history
- [ ] Add configuration file
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Load test with 100 concurrent sessions
- [ ] Monitor question/answer latency
- [ ] A/B test: socratic on vs off
- [ ] Measure learning outcomes

---

## Success Metrics

**Measure these to validate effectiveness:**

1. **Learning Rate**
   - Time to concept mastery (before vs after)
   - Concept retention after 1 week

2. **Engagement**
   - Session duration (should increase)
   - Drop-off rate (should decrease)
   - Questions answered vs skipped

3. **Understanding Quality**
   - Average answer score
   - First-try understanding rate
   - Checkpoint quiz performance

---

## Future Enhancements

1. **Adaptive Frequency**: Adjust checkpoint frequency based on student performance
2. **Multi-Modal Questions**: Audio/video questions via voice interface
3. **Peer Comparison**: "83% of students got this right"
4. **Question Prediction**: Predict which concepts need verification
5. **Personalized Templates**: Learn which question types work best per student

---

**END OF DOCUMENT**

*Implementation estimated at 2-3 days for full feature.*
*Estimated impact: 2-3x learning rate improvement.*
