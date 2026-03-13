import random
from collections import defaultdict

# ---------------- Replacement Logic ----------------

def replace_block(cache, policy, freq, use_bits, hand):
    """
    Handles the removal of a block based on the specific policy.
    Every policy here now uses a unique logic path.
    """
    if not cache:
        return hand

    if policy == "FIFO":
        # First-In: Simply remove the oldest item (index 0)
        cache.pop(0)
    
    elif policy == "LRU":
        # Least Recently Used: Remove index 0. 
        # (The main loop moves 'hits' to the end of the list)
        cache.pop(0)

    elif policy == "LFU":
        # Least Frequently Used: Purely frequency-based
        least_val = min([freq[b] for b in cache])
        for b in cache:
            if freq[b] == least_val:
                cache.remove(b)
                break

    elif policy == "PRIORITY":
        # Priority Logic: Weighted Importance
        # Formula: (1000 / Address Value) + Access Frequency
        # This protects "System/Kernel" blocks (low addresses)
        p_func = lambda x: (1000 / x) + freq[x]
        lowest_priority_block = min(cache, key=p_func)
        cache.remove(lowest_priority_block)

    elif policy == "CLOCK":
        # Second Chance (Clock) Algorithm
        while True:
            idx = hand % len(cache)
            block = cache[idx]
            if use_bits[block] == 0:
                cache.pop(idx)
                return idx # New hand position
            else:
                # Give second chance and move hand
                use_bits[block] = 0
                hand += 1
    
    return hand

# ---------------- Cache Simulation ----------------

def simulate_two_level_cache(sequence, l1_size, l2_size, policy):
    l1, l2 = [], []
    freq = defaultdict(int)
    use_bits = defaultdict(int) 
    
    l1_hand, l2_hand = 0, 0
    l1_hits, l2_hits, misses = 0, 0, 0
    utilization = []

    for block in sequence:
        freq[block] += 1
        
        # ---------- L1 CHECK ----------
        if block in l1:
            l1_hits += 1
            use_bits[block] = 1 
            if policy == "LRU":
                l1.remove(block)
                l1.append(block)

        # ---------- L2 CHECK ----------
        elif block in l2:
            l2_hits += 1
            use_bits[block] = 1
            if policy == "LRU":
                l2.remove(block)
                l2.append(block)
            
            # Promote to L1
            if len(l1) >= l1_size:
                l1_hand = replace_block(l1, policy, freq, use_bits, l1_hand)
            l1.append(block)

        # ---------- MISS (FETCH FROM RAM) ----------
        else:
            misses += 1
            use_bits[block] = 1
            if len(l2) >= l2_size:
                l2_hand = replace_block(l2, policy, freq, use_bits, l2_hand)
            l2.append(block)
            
            if len(l1) >= l1_size:
                l1_hand = replace_block(l1, policy, freq, use_bits, l1_hand)
            l1.append(block)

        utilization.append(len(l1) / l1_size if l1_size > 0 else 0)

    total = len(sequence)
    l1_rate = l1_hits / total
    l1_miss_count = total - l1_hits
    l2_local_rate = l2_hits / l1_miss_count if l1_miss_count > 0 else 0
    
    overall_hit_rate = (l1_hits + l2_hits) / total
    miss_rate = misses / total

    return l1_rate, l2_local_rate, overall_hit_rate, miss_rate, utilization

# ---------------- AMAT & Stats ----------------

def calculate_amat(l1_hit_rate, l2_local_hit_rate):
    L1_HT, L2_HT, MEM_P = 1, 10, 100
    l1_mr = 1 - l1_hit_rate
    l2_mr = 1 - l2_local_hit_rate
    return L1_HT + (l1_mr * (L2_HT + (l2_mr * MEM_P)))

def adaptive_cache_from_workload(sequence, max_l1=32, max_l2=64):
    """
    Tightened heuristic to force capacity pressure so hit rates differ.
    """
    unique_elements = len(set(sequence))
    l1_rec = max(2, min(int(unique_elements * 0.15), max_l1))
    l2_rec = max(l1_rec + 2, min(int(unique_elements * 0.40), max_l2))
    return l1_rec, l2_rec, unique_elements

def working_set_ratio(sequence, cache_size):
    unique = len(set(sequence))
    return unique / cache_size if cache_size > 0 else 0

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
            "Miss Rate": round(mr * 100, 2)
        })
    return results
