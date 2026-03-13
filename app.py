import streamlit as st
import random
import pandas as pd
from cache_simulator import (
    simulate_two_level_cache,
    adaptive_cache_from_workload,
    calculate_amat,
    working_set_ratio,
    compare_policies_system
)

st.set_page_config(page_title="Adaptive Cache System", layout="wide")
st.title("Self-Adapting Cache Memory Management System")

st.write("""
This simulator models a **two-level cache hierarchy (L1 + L2)** and dynamically
adjusts cache sizes based on observed CPU memory access behavior.
""")

# --- Session State for Fixed Sequence ---
if 'fixed_seq' not in st.session_state:
    st.session_state.fixed_seq = [random.randint(1, 50) for _ in range(200)]

# ---------------- Sidebar ----------------
st.sidebar.header("System Configuration")
memory_size = st.sidebar.slider("Main Memory Size", 32, 512, 128)
access_length = st.sidebar.slider("Memory Access Length", 50, 400, 150)
policy = st.sidebar.selectbox("Cache Replacement Policy", ["FIFO", "LRU", "LFU", "CLOCK", "PRIORITY"])
workload = st.sidebar.selectbox("CPU Workload Type", ["Random", "Sequential", "Localized", "Fixed Set"])

if workload == "Fixed Set":
    if st.sidebar.button("Regenerate Fixed Set"):
        st.session_state.fixed_seq = [random.randint(1, memory_size) for _ in range(access_length)]

# ---------------- Workload Generator ----------------
def generate_sequence():
    if workload == "Fixed Set":
        return st.session_state.fixed_seq
    elif workload == "Random":
        return [random.randint(1, memory_size) for _ in range(access_length)]
    elif workload == "Sequential":
        return [(i % memory_size) + 1 for i in range(access_length)]
    elif workload == "Localized":
        hot_blocks = [random.randint(1, 15) for _ in range(8)]
        seq = []
        for _ in range(access_length):
            if random.random() < 0.85:
                seq.append(random.choice(hot_blocks))
            else:
                seq.append(random.randint(1, memory_size))
        return seq

# ---------------- Run Simulation ----------------
if st.button("Run Simulation"):
    sequence = generate_sequence()
    l1_rec, l2_rec, working_set = adaptive_cache_from_workload(sequence)
    l1_hit, l2_hit, overall_hit, miss_rate, util = simulate_two_level_cache(sequence, l1_rec, l2_rec, policy)
    amat = calculate_amat(l1_hit, l2_hit)
    ws_ratio = working_set_ratio(sequence, l1_rec)

    # ---------------- Recommendation ----------------
    st.subheader("Adaptive Cache Recommendation")
    c1, c2, c3 = st.columns(3)
    c1.metric("Working Set Size", working_set)
    c2.metric("Recommended L1 Cache", l1_rec)
    c3.metric("Recommended L2 Cache", l2_rec)
    st.divider()

    # ---------------- Performance ----------------
    st.subheader("Cache Performance Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("L1 Hit Rate", f"{l1_hit*100:.2f}%")
    c2.metric("L2 Hit Rate", f"{l2_hit*100:.2f}%")
    c3.metric("Overall Hit Rate", f"{overall_hit*100:.2f}%")
    c4.metric("AMAT", f"{amat:.2f} cycles")
    st.write(f"Working Set Ratio: {ws_ratio:.2f}")
    st.divider()

    # ---------------- Memory Access Visualization ----------------
    st.subheader("Memory Access Sequence")
    cols_per_row = 10
    rows = [sequence[i:i + cols_per_row] for i in range(0, len(sequence), cols_per_row)]
    for row in rows:
        cols = st.columns(len(row))
        for i, addr in enumerate(row):
            cols[i].markdown(f"""<div style="background-color:#0f172a;padding:10px;border-radius:8px;text-align:center;border:1px solid #334155;font-weight:bold;color:#22c55e;">{addr}</div>""", unsafe_allow_html=True)
    st.divider()

    # ---------------- Memory Access Frequency ----------------
    st.subheader("Memory Access Frequency")
    freq = {}
    for block in sequence: freq[block] = freq.get(block, 0) + 1
    freq_df = pd.DataFrame(list(freq.items()), columns=["Memory Block", "Access Count"]).sort_values("Memory Block")
    st.bar_chart(freq_df.set_index("Memory Block"))
    st.divider()

    # ---------------- Cache Size vs Performance ----------------
    st.subheader("Cache Performance vs Cache Size")
    l1_sizes = list(range(1, 21))
    l1_results, l2_results = [], []
    for size in l1_sizes:
        l1_r, l2_r, _, _, _ = simulate_two_level_cache(sequence, size, size * 2, policy)
        l1_results.append(l1_r * 100); l2_results.append(l2_r * 100)
    graph_df = pd.DataFrame({"Cache Size": l1_sizes, "L1 Hit Rate (%)": l1_results, "L2 Hit Rate (%)": l2_results}).set_index("Cache Size")
    st.line_chart(graph_df)
    st.divider()

    # ---------------- System-Level Policy Comparison ----------------
    st.subheader("System-Level Replacement Policy Comparison")
    policy_results = compare_policies_system(sequence, l1_rec, l2_rec)
    policy_df = pd.DataFrame(policy_results)
    st.dataframe(policy_df)

    st.write("### Hit Rate Comparison")
    st.bar_chart(policy_df.set_index("Policy")["Hit Rate"])
    st.write("### Miss Rate Comparison")
    st.bar_chart(policy_df.set_index("Policy")["Miss Rate"])
    st.write("### AMAT Comparison")
    st.bar_chart(policy_df.set_index("Policy")["AMAT"])
