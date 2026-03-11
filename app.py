import streamlit as st
import random
import pandas as pd
from cache_simulator import analyze_cache_sizes

st.set_page_config(page_title="Adaptive Cache Analyzer", layout="wide")

st.title("Memory Hierarchy Cache Analyzer")

st.write(
"""
Analyze cache performance across different cache sizes and workloads.
This simulator demonstrates cache hit rates and identifies the ideal cache size.
"""
)

# Sidebar controls

st.sidebar.header("Simulation Settings")

sequence_length = st.sidebar.slider("Memory Access Length", 50, 400, 150)

max_cache_size = st.sidebar.slider("Maximum Cache Size Tested", 5, 64, 20)

workload = st.sidebar.selectbox(
    "Memory Access Pattern",
    ["Random", "Sequential", "Localized"]
)


def generate_sequence():

    if workload == "Random":
        return [random.randint(1, 60) for _ in range(sequence_length)]

    if workload == "Sequential":
        return [i % 60 for i in range(sequence_length)]

    if workload == "Localized":

        hot_region = [random.randint(1, 10) for _ in range(sequence_length//2)]
        noise = [random.randint(1, 60) for _ in range(sequence_length//2)]

        return hot_region + noise


if st.button("Run Cache Analysis"):

    sequence = generate_sequence()

    results = analyze_cache_sizes(sequence, max_cache_size)

    df = pd.DataFrame({
        "Cache Size": list(results.keys()),
        "Hit Rate": list(results.values())
    })

    df["Hit Rate %"] = df["Hit Rate"] * 100

    ideal_size = df.loc[df["Hit Rate"].idxmax()]["Cache Size"]
    best_hit = df["Hit Rate %"].max()

    st.subheader("Key Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Memory Accesses", sequence_length)
    col2.metric("Ideal Cache Size", int(ideal_size))
    col3.metric("Best Hit Rate", f"{best_hit:.2f}%")

    st.divider()

    # Memory access visualization

    st.subheader("Memory Access Sequence")

    st.markdown(
        "<div style='height:260px; overflow-y:scroll;'>",
        unsafe_allow_html=True
    )

    cols_per_row = 8
    rows = [sequence[i:i+cols_per_row] for i in range(0, len(sequence), cols_per_row)]

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

    # Graph

    st.subheader("Cache Performance vs Cache Size")

    chart_data = df.set_index("Cache Size")["Hit Rate %"]

    st.line_chart(chart_data)

    st.divider()

    # Table

    st.subheader("Detailed Cache Performance")

    st.dataframe(df)

    st.divider()

    # Analytics

    st.subheader("Performance Insights")

    st.write(f"""
    **Ideal Cache Size:** {ideal_size}

    **Maximum Hit Rate:** {best_hit:.2f} %

    Interpretation:
    - Increasing cache size initially improves hit rate significantly.
    - Beyond the optimal size, performance improvements slow down.
    - Workloads with locality benefit more from larger caches.
    - This demonstrates the importance of choosing an appropriate cache size in computer architecture design.
    """)