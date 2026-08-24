"""
Natural-language FP&A analyst agent.

Takes a plain-English question about the business (variance, forecast,
pipeline) and answers it using Claude, grounded strictly in the computed
data files -- not general knowledge. This is the real, runnable version of
Section 3; it requires an ANTHROPIC_API_KEY environment variable.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python3 pipeline/qa_agent.py "Why is Mass Spec behind plan this quarter?"
"""

import json
import os
import sys

import anthropic

SYSTEM_PROMPT = """You are an FP&A analyst for the Analytical Sciences Division.
Answer the user's question using ONLY the data provided below. Cite specific
numbers from the data in your answer. If the data doesn't contain enough
information to answer confidently, say so explicitly rather than guessing.
Keep answers to 2-4 sentences, in the plain, specific style of a real
variance commentary -- no filler, no generic advice."""


def load_context():
    with open("data/weekly_review.json") as f:
        weekly_review = json.load(f)
    with open("data/forecast_scenarios.json") as f:
        forecast = json.load(f)
    return {"weekly_review": weekly_review, "forecast": forecast}


def ask(question, context):
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    user_content = (
        f"DATA:\n{json.dumps(context, indent=2)}\n\n"
        f"QUESTION: {question}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 pipeline/qa_agent.py "your question here"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    context = load_context()
    answer = ask(question, context)
    print(answer)


if __name__ == "__main__":
    main()
