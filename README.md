# Tradeoff Lab

A small eval harness that answers the same 10 policy questions using 3 different setups (different models and/or prompt styles), grades each answer automatically with a second "judge" model call, and compares the results on **accuracy, cost, and speed**.

Built to demonstrate a core AI deployment skill: knowing when a bigger/more expensive model is actually worth it, and when it isn't.

## What it does

1. `runner.py` loads a fictional company policy handbook (`policy_handbook.md`) and 10 Q&A pairs (`eval_questions.json`).
2. For each of 3 configs, it asks every question, times the response, calculates the exact dollar cost from token usage, and uses a second `gpt-4o-mini` call to grade the answer as correct/incorrect against the reference answer.
3. Results are saved to `results.json`.
4. `app.py` (a Streamlit app) reads `results.json` and shows a comparison table, bar charts, and an auto-generated takeaway sentence.

## The 3 setups compared

| Setup | Model | Prompt style |
|---|---|---|
| mini + minimal prompt | gpt-4o-mini | Bare-bones instructions |
| mini + detailed prompt | gpt-4o-mini | Detailed instructions + one example |
| gpt-4o + minimal prompt | gpt-4o | Bare-bones instructions |

## Results

| Setup | Model | Accuracy | Avg Cost/Question | Total Cost |
|---|---|---|---|---|
| mini + minimal prompt | gpt-4o-mini | 100% | $0.00005 | $0.0005 |
| mini + detailed prompt | gpt-4o-mini | 100% | $0.00005 | $0.0005 |
| gpt-4o + minimal prompt | gpt-4o | 100% | $0.00079 | $0.0079 |

**Takeaway:** all 3 setups hit 100% accuracy on this test, but `gpt-4o` cost roughly **16x more per question** than `gpt-4o-mini` for no accuracy gain. On this task, the smaller, cheaper model with a well-written prompt matched the larger model's accuracy at a fraction of the cost — a good example of why "always use the biggest model" isn't the right default in production.

*(Caveat: this is a 10-question sample, so I wouldn't treat the latency numbers as statistically meaningful — but the cost comparison is exact, since it's calculated directly from token usage and published pricing.)*

## Running it yourself

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env         # then paste your own OpenAI API key into .env
python runner.py              # runs the eval, writes results.json
streamlit run app.py          # view the comparison dashboard
```

## Why this project

Comparing model/prompt configs on accuracy, cost, and latency is exactly the kind of tradeoff analysis an AI deployment role requires — this project is a small, self-contained demonstration of that skill.
