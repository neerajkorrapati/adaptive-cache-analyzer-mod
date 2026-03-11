import streamlit as st
import random
import pandas as pd
from cache_simulator import analyze_cache_sizes, adaptive_cache

st.set_page_config(page_title="Adaptive Cache System", layout="wide")

st.title("Self-Adapting Cache Memory Management System")

st.write("""
This simulator analyzes memory access workloads and dynamically determines
the optimal cache size that maximizes cache hit rate.

The system evaluates cache performance across different cache sizes and
adapts the cache configuration based on workload characteristics.
""")

# Sidebar controls

st.sidebar.header("Simulation Settings")

sequence_length = st.sidebar.slider(
    "Memory Access Length",
    50,
    400,
    150
)

max_cache_size = st.sidebar.slider(
    "Maximum Cache Size Tested",
    5,
    50,
    20
)

workload = st.sidebar.selectbox(
    "Memory Access Pattern",
    ["Random", "Sequential", "Localized"]
)


# Memory sequence generator

def generate_sequence():

    if workload == "Random":

        return [random.randint(1, 60) for _ in range(sequence_length)]

    if workload == "Sequential":

        base_pattern = list(range(10))
        sequence = []

        for i in range(sequence_length):
            sequence.append(base_pattern[i % len(base_pattern)])

        return sequence

    if workload == "Localized":

        hot_region = [random.randint(1, 10) for _ in range(int(sequence_length * 0.7))]
        noise = [random.randint(1, 60) for _ in range(int(sequence_length * 0.3))]

        return hot_region + noise


if st.button("Run Adaptive Cache Analysis"):

    sequence = generate_sequence()

    results = analyze_cache_sizes(sequence, max_cache_size)

    adaptive_size, adaptive_hit, history = adaptive_cache(sequence, max_cache_size)

    df = pd.DataFrame({
        "Cache Size": list(results.keys()),
        "Hit Rate": list(results.values())
    })

    df["Hit Rate %"] = df["Hit Rate"] * 100

    st.subheader("System Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Memory Accesses", sequence_length)
    col2.metric("Recommended Cache Size", adaptive_size)
    col3.metric("Expected Hit Rate", f"{adaptive_hit*100:.2f}%")

    st.divider()

    st.subheader("Memory Access Sequence")

    st.markdown("<div style='height:250px; overflow-y:scroll;'>", unsafe_allow_html=True)

    cols_per_row = 8
    rows = [sequence[i:i + cols_per_row] for i in range(0, len(sequence), cols_per_row)]

    for row in rows:

        cols = st.columns(cols_per_row)

        for i, addr in enumerate(row):

            cols[i].markdown(
                f"""
                <div style="
                background-color:#0f172a;
                padding:12px;
                border-radius:10px;
                text-align:center;
                border:1px solid #334155;
                font-weight:bold;
                color:#22c55e;">
                ADDR<br>{addr}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.subheader("Cache Performance vs Cache Size")

    chart_data = df.set_index("Cache Size")["Hit Rate %"]

    st.line_chart(chart_data)

    st.divider()

    st.subheader("Detailed Performance Table")

    st.dataframe(df)

    st.divider()

    st.subheader("Adaptive Cache Decision")

    st.write(f"""
The system evaluated cache sizes from **1 to {max_cache_size}**.

The optimal cache size for this workload is **{adaptive_size}**, which produces
the highest hit rate of **{adaptive_hit*100:.2f}%**.

This demonstrates adaptive cache allocation where cache resources are tuned
based on observed workload behavior.
""")
