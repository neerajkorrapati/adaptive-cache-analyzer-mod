import streamlit as st
import random
import pandas as pd
from cache_simulator import (
    simulate_two_level_cache,
    adaptive_cache_from_workload,
    calculate_amat,
    compare_policies_system
)

st.set_page_config(page_title="Adaptive Cache System", layout="wide")
st.title("Self-Adapting Cache Memory Management System")

st.write("""
This simulator models a **two-level cache hierarchy (L1 + L2)** and dynamically
adjusts cache sizes based on observed CPU memory access behavior.
""")

if 'fixed_seq' not in st.session_state:
    st.session_state.fixed_seq = [random.randint(1, 50) for _ in range(200)]

st.sidebar.header("System Configuration")
memory_size = st.sidebar.slider("Main Memory Size", 32, 512, 128)
access_length = st.sidebar.slider("Memory Access Length", 50, 400, 150)
policy = st.sidebar.selectbox("Cache Replacement Policy", ["FIFO", "LRU", "LFU", "CLOCK", "PRIORITY"])
workload = st.sidebar.selectbox("CPU Workload Type", ["Sequential", "Localized", "Fixed Set"])

if workload == "Fixed Set":
    if st.sidebar.button("Regenerate Fixed Set"):
        st.session_state.fixed_seq = [random.randint(1, memory_size) for _ in range(access_length)]

def generate_sequence():
    if workload == "Fixed Set":
        return st.session_state.fixed_seq
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

if st.button("Run Simulation"):
    sequence = generate_sequence()
    l1_rec, l2_rec, working_set = adaptive_cache_from_workload(sequence)

    l1_hit, l2_hit, overall_hit, miss_rate, util = simulate_two_level_cache(
        sequence, l1_rec, l2_rec, policy
    )

    amat = calculate_amat(l1_hit, l2_hit)

    st.subheader("Adaptive Cache Recommendation")
    c1, c2, c3 = st.columns(3)
    c1.metric("Working Set Size", working_set)
    c2.metric("Recommended L1 Cache", l1_rec)
    c3.metric("Recommended L2 Cache", l2_rec)
    st.divider()

    st.subheader("Cache Performance Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("L1 Hit Rate", f"{l1_hit*100:.2f}%")
    c2.metric("L2 Hit Rate", f"{l2_hit*100:.2f}%")
    c3.metric("Overall Hit Rate", f"{overall_hit*100:.2f}%")
    c4.metric("AMAT", f"{amat:.2f} cycles")
    st.divider()

    st.subheader("System-Level Replacement Policy Comparison")
    policy_results = compare_policies_system(sequence, l1_rec, l2_rec)
    policy_df = pd.DataFrame(policy_results)

    st.dataframe(policy_df)

    st.write("### Hit Rate Comparison")
    st.bar_chart(policy_df.set_index("Policy")["Hit Rate"])
