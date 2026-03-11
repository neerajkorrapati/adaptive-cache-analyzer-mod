from collections import OrderedDict


def simulate_cache(sequence, cache_size):

    cache = OrderedDict()
    hits = 0
    misses = 0

    for block in sequence:

        if block in cache:

            hits += 1
            cache.move_to_end(block)

        else:

            misses += 1

            if len(cache) >= cache_size:
                cache.popitem(last=False)

            cache[block] = True

    total = hits + misses

    if total == 0:
        return 0

    return hits / total


def analyze_cache_sizes(sequence, max_cache_size):

    results = {}

    for size in range(1, max_cache_size + 1):

        hit_rate = simulate_cache(sequence, size)

        results[size] = hit_rate

    return results


def adaptive_cache(sequence, max_cache_size):

    best_size = 1
    best_hit = 0

    history = []

    for size in range(1, max_cache_size + 1):

        hit_rate = simulate_cache(sequence, size)

        history.append((size, hit_rate))

        if hit_rate > best_hit:
            best_hit = hit_rate
            best_size = size

    return best_size, best_hit, history
