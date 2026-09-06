"""
Tradeoff Lab -- reads results.json (produced by runner.py) and shows the
3 setups side by side on accuracy, cost, and speed.

Run with:  streamlit run app.py
"""

import json

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tradeoff Lab", page_icon="⚖️")

st.title("Tradeoff Lab")
st.caption(
    "Same 10 policy questions, 3 different setups -- compared on accuracy, "
    "cost, and speed."
)

try:
    with open("results.json", encoding="utf-8") as f:
        results = json.load(f)
except FileNotFoundError:
    st.error(
        "No results.json found yet. Run `python runner.py` in this folder "
        "first, then reload this page."
    )
    st.stop()

df = pd.DataFrame(results).rename(
    columns={
        "config": "Setup",
        "model": "Model",
        "accuracy_pct": "Accuracy (%)",
        "avg_latency_sec": "Avg Latency (s)",
        "avg_cost_usd": "Avg Cost ($)",
        "total_cost_usd": "Total Cost ($)",
    }
)

st.subheader("Comparison")
st.dataframe(df.set_index("Setup"), use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Accuracy (%)**")
    st.bar_chart(df.set_index("Setup")["Accuracy (%)"])
with col2:
    st.markdown("**Avg Cost per Question ($)**")
    st.bar_chart(df.set_index("Setup")["Avg Cost ($)"])
with col3:
    st.markdown("**Avg Latency (s)**")
    st.bar_chart(df.set_index("Setup")["Avg Latency (s)"])

st.divider()
st.subheader("Takeaway")

best_acc = df["Accuracy (%)"].max()
best_rows = df[df["Accuracy (%)"] == best_acc].sort_values("Avg Cost ($)")
cheapest_at_best = best_rows.iloc[0]
priciest = df.sort_values("Avg Cost ($)", ascending=False).iloc[0]

if cheapest_at_best["Setup"] == priciest["Setup"]:
    st.write(
        f"**{priciest['Setup']}** was both the most accurate and the most "
        f"expensive setup tested -- no cheaper option matched its accuracy here."
    )
else:
    multiple = priciest["Avg Cost ($)"] / cheapest_at_best["Avg Cost ($)"]
    st.write(
        f"**{cheapest_at_best['Setup']}** matched the best accuracy seen "
        f"({best_acc:.0f}%) at roughly **{multiple:.0f}x lower cost** than "
        f"the priciest setup tested (**{priciest['Setup']}**)."
    )

st.caption(
    "Change a prompt or model in runner.py, run `python runner.py` again, "
    "then refresh this page to compare a new setup."
)
