"""
Tradeoff Lab — runs the same eval questions through 3 different setups
(different prompt styles and/or different models), scores each answer
with a second "judge" model call, and records accuracy, cost, and speed
for each setup.

Run with:  python runner.py
Output:    results.json  (read by the Streamlit app next)
"""

import json
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

with open("policy_handbook.md", encoding="utf-8") as f:
    HANDBOOK = f.read()

with open("eval_questions.json", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

# Rough per-1,000,000-token pricing in USD. Check platform.openai.com/pricing
# and update these two lines if prices have changed since this was written.
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}

# The 3 setups being compared. Same questions, same handbook — only the
# model and/or the prompt wording changes between them.
CONFIGS = [
    {
        "name": "mini + minimal prompt",
        "model": "gpt-4o-mini",
        "system_prompt": (
            "Answer the question using only the handbook below.\n\n" + HANDBOOK
        ),
    },
    {
        "name": "mini + detailed prompt",
        "model": "gpt-4o-mini",
        "system_prompt": (
            "You are a precise operations policy assistant. Answer strictly "
            "using facts from the handbook below. Always include exact "
            "numbers, times, or percentages when the question asks for them. "
            "Keep answers to one short sentence.\n\n"
            "Example:\nQ: What is the injury reporting window?\n"
            "A: Within 1 hour, regardless of severity.\n\n" + HANDBOOK
        ),
    },
    {
        "name": "gpt-4o + minimal prompt",
        "model": "gpt-4o",
        "system_prompt": (
            "Answer the question using only the handbook below.\n\n" + HANDBOOK
        ),
    },
]


def ask(config, question):
    """Send one question to one setup. Returns (answer, latency_sec, cost_usd)."""
    start = time.time()
    resp = client.chat.completions.create(
        model=config["model"],
        messages=[
            {"role": "system", "content": config["system_prompt"]},
            {"role": "user", "content": question},
        ],
    )
    latency = time.time() - start

    answer = resp.choices[0].message.content.strip()
    usage = resp.usage
    price = PRICING[config["model"]]
    cost = (usage.prompt_tokens / 1_000_000 * price["input"]) + (
        usage.completion_tokens / 1_000_000 * price["output"]
    )
    return answer, latency, cost


def judge(question, reference_answer, model_answer):
    """A second, cheap model call that grades the answer. Returns True/False."""
    judge_prompt = (
        "You are grading a factual answer against a reference answer.\n"
        f"Question: {question}\n"
        f"Reference answer: {reference_answer}\n"
        f"Answer to grade: {model_answer}\n\n"
        "Does the answer to grade correctly and completely match the key "
        "facts in the reference answer? Reply with exactly one word: "
        "CORRECT or INCORRECT."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0,
    )
    verdict = resp.choices[0].message.content.strip().upper()
    return verdict.startswith("CORRECT")


def main():
    results = []

    for config in CONFIGS:
        print(f"\n=== Running: {config['name']} ===")
        correct = 0
        total_cost = 0.0
        total_latency = 0.0

        for item in QUESTIONS:
            answer, latency, cost = ask(config, item["question"])
            is_correct = judge(item["question"], item["reference_answer"], answer)

            correct += is_correct
            total_cost += cost
            total_latency += latency

            print(f"  Q: {item['question'][:60]}...")
            print(f"  A: {answer}")
            status = "CORRECT" if is_correct else "INCORRECT"
            print(f"  {status} | {latency:.2f}s | ${cost:.5f}")

        n = len(QUESTIONS)
        results.append(
            {
                "config": config["name"],
                "model": config["model"],
                "accuracy_pct": round(correct / n * 100, 1),
                "avg_latency_sec": round(total_latency / n, 2),
                "avg_cost_usd": round(total_cost / n, 5),
                "total_cost_usd": round(total_cost, 5),
            }
        )

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n=== Summary ===")
    for r in results:
        print(r)

    print("\nSaved to results.json")


if __name__ == "__main__":
    main()
