#!/usr/bin/env python3
"""Direct test of teacher agent without Flask"""

import asyncio
from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)

# Same teacher agent
TEACHER_AGENT = AgentDefinition(
    description="Interactive coding teacher",
    prompt="""You are an expert programming instructor.

Explain concepts clearly with inline code examples using markdown.
DO NOT create files. Show all code inline.

Example: Teach Python list comprehensions in 2-3 sentences with one code example.""",
    tools=[],
    model="sonnet",
)

async def test():
    print("Testing teacher agent directly...")
    print("="*60)

    options = ClaudeAgentOptions(
        agents={"teacher": TEACHER_AGENT},
    )

    async with ClaudeSDKClient(options=options) as client:
        print("✓ Client connected")

        # Send query
        query = "Use the teacher agent: Explain Python list comprehensions in 2 sentences with one code example"
        print(f"Query: {query}\n")

        await client.query(query)
        print("✓ Query sent")
        print("\nReceiving responses:")
        print("-"*60)

        message_count = 0
        async for msg in client.receive_response():
            message_count += 1
            print(f"\nMessage #{message_count}: {type(msg).__name__}")

            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Content: {block.text[:100]}...")
                        print(f"Full content:\n{block.text}")

            elif isinstance(msg, ResultMessage):
                print(f"Result: Done")
                if msg.total_cost_usd:
                    print(f"Cost: ${msg.total_cost_usd:.4f}")

        print(f"\n✓ Total messages: {message_count}")

if __name__ == "__main__":
    asyncio.run(test())
