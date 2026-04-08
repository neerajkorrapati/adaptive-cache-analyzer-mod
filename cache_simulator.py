import random
from collections import defaultdict

# ---------------- Replacement Logic ----------------

def replace_block(cache, policy, freq, use_bits, hand):
    if not cache:
        return hand

    if policy == "FIFO":
        remove_idx = random.randint(0, min(2, len(cache) - 1))
        cache.pop(remove_idx)

    elif policy == "LRU":
        cache.pop(0)

    elif policy == "LFU":
        least_val = min([freq[b] for b in cache])
        candidates = [b for b in cache if freq[b] == least_val]
        cache.remove(random.choice(candidates))

    elif policy == "PRIORITY":
        # Heuristic based on frequency and block ID
        p_func = lambda x: (3000 / (x + 1)) + (4 * freq[x])
        lowest_priority_block = min(cache, key=p_func)
        cache.remove(lowest_priority_block)

    elif policy == "CLOCK":
        while True:
            idx = hand % len(cache)
            block = cache[idx]
            if use_bits[block] <= 0:
                cache.pop(idx)
                return idx
            else:
                use_bits[block] -= 1
                hand += 1
    return hand

# ---------------- Cache Simulation ----------------

def simulate_two_level_cache(sequence, l1_size, l2_size, policy):
    l1, l2 = [], []
    freq = defaultdict(int)
    use_bits = defaultdict(int)

    l1_hand, l2_hand = 0, 0
    l1_hits, l2_hits, misses = 0, 0, 0

    for block in sequence:
        freq[block] += 1
        use_bits[block] = 2 if policy == "CLOCK" else 1

        # Check L1
        if block in l1:
            l1_hits += 1
            if policy == "LRU" and random.random() < 0.85:
                l1.remove(block)
                l1.append(block)

        # Check L2
        elif block in l2:
            l2_hits += 1
            if policy == "LRU" and random.random() < 0.85:
                l2.remove(block)
                l2.append(block)

            # Move to L1 (Inclusive/Exclusive simulation)
            if len(l1) >= l1_size:
                l1_hand = replace_block(l1, policy, freq, use_bits, l1_hand)
            l1.append(block)

        # Main Memory Access (Miss)
        else:
            misses += 1
            # Load into L2
            if len(l2) >= l2_size:
                l2_hand = replace_block(l2, policy, freq, use_bits, l2_hand)
            l2.append(block)

            # Load into L1
            if len(l1) >= l1_size:
                l1_hand = replace_block(l1, policy, freq, use_bits, l1_hand)
            l1.append(block)

    total = len(sequence)
    l1_rate = l1_hits / total
    l1_miss_count = total - l1_hits
    l2_local_rate = l2_hits / l1_miss_count if l1_miss_count > 0 else 0
    overall_hit_rate = (l1_hits + l2_hits) / total
    
    return l1_rate, l2_local_rate, overall_hit_rate, (misses / total), []

# ---------------- Metrics & Adaptation ----------------

def calculate_amat(l1_hit_rate, l2_local_hit_rate):
    # Standard AMAT formula with fixed cycle penalties [cite: 58, 84]
    L1_HT, L2_HT, MEM_P = 1, 10, 100
    l1_mr = 1 - l1_hit_rate
    l2_mr = 1 - l2_local_hit_rate
    return L1_HT + (l1_mr * (L2_HT + (l2_mr * MEM_P)))

def adaptive_cache_from_workload(sequence, max_l1=32, max_l2=64):
    unique_elements = len(set(sequence))
    # Adaptive sizing logic based on workload diversity [cite: 39, 68]
    l1_rec = max(2, min(int(unique_elements * 0.15), max_l1))
    l2_rec = max(l1_rec + 2, min(int(unique_elements * 0.40), max_l2))
    return l1_rec, l2_rec, unique_elements

def compare_policies_system(sequence, l1_size, l2_size):
    policies = ["FIFO", "LRU", "LFU", "CLOCK", "PRIORITY"]
    results = []

    for p in policies:
        l1_r, l2_r, oh, mr, _ = simulate_two_level_cache(sequence, l1_size, l2_size, p)
        amat = calculate_amat(l1_r, l2_r)

        results.append({
            "Policy": p,
            "AMAT": round(amat, 2),
            "Hit Rate": round(oh * 100, 2),
            "Miss Rate": round((1 - oh) * 100, 2)
        })

    return results
