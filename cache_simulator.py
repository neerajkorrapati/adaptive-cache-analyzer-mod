import random
from collections import defaultdict


# ---------------- Replacement Logic ----------------

def replace_block(cache, policy, freq):

    if len(cache) == 0:
        return

    if policy == "FIFO":
        cache.pop(0)

    elif policy == "LRU":
        cache.pop(0)

    elif policy == "Random":
        idx = random.randint(0, len(cache) - 1)
        cache.pop(idx)

    elif policy == "LFU":
        least = min(cache, key=lambda x: freq[x])
        cache.remove(least)


# ---------------- Cache Simulation ----------------

def simulate_two_level_cache(sequence, l1_size, l2_size, policy):

    l1 = []
    l2 = []

    freq = defaultdict(int)

    l1_hits = 0
    l2_hits = 0
    misses = 0

    for block in sequence:

        # ---------- L1 ----------
        if block in l1:

            l1_hits += 1

            if policy == "LRU":
                l1.remove(block)
                l1.append(block)

        # ---------- L2 ----------
        elif block in l2:

            l2_hits += 1

            if policy == "LRU":
                l2.remove(block)
                l2.append(block)

            if len(l1) >= l1_size:
                replace_block(l1, policy, freq)

            l1.append(block)

        # ---------- MISS ----------
        else:

            misses += 1

            if len(l2) >= l2_size:
                replace_block(l2, policy, freq)

            l2.append(block)

            if len(l1) >= l1_size:
                replace_block(l1, policy, freq)

            l1.append(block)

        freq[block] += 1

    total = len(sequence)

    l1_rate = l1_hits / total
    l2_rate = l2_hits / total
    overall_hit = (l1_hits + l2_hits) / total

    return l1_rate, l2_rate, overall_hit


# ---------------- Adaptive Cache ----------------

def adaptive_cache_from_workload(sequence, max_l1=64, max_l2=128):

    working_set = len(set(sequence))

    # better heuristic
    l1_size = int(working_set * 0.4)
    l2_size = int(working_set * 1.1)

    l1_size = max(2, min(l1_size, max_l1))
    l2_size = max(l1_size + 1, min(l2_size, max_l2))

    return l1_size, l2_size, working_set
