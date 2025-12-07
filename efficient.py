import sys
import time
import psutil
import basic

# -----------------------------
# Cost parameters
# -----------------------------
delta = 30
alpha = {
    'A': {'A': 0, 'C': 110, 'G': 48, 'T': 94},
    'C': {'A': 110, 'C': 0, 'G': 118, 'T': 48},
    'G': {'A': 48, 'C': 118, 'G': 0, 'T': 110},
    'T': {'A': 94, 'C': 48, 'G': 110, 'T': 0}
}

# -----------------------------
# Read + Generate strings, same as basic.py
# -----------------------------
def read(path):
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip() != '']
    if not lines:
        return "", ""

    idx = 0

    # First base string
    X_base = lines[idx]
    idx += 1
    X_indices = []
    while idx < len(lines) and lines[idx].isdigit():
        X_indices.append(int(lines[idx]))
        idx += 1
    # Second base string
    Y_base = lines[idx]
    idx += 1
    Y_indices = []
    while idx < len(lines):
        Y_indices.append(int(lines[idx]))
        idx += 1
    return X_base, X_indices, Y_base, Y_indices

def generate(base, indices):
    s = base
    for i in indices:
        if i < 0 or i > len(s) - 1:
            raise ValueError("Invalid insertion index")
        else:
            pos = i + 1
            s = s[:pos] + s + s[pos:]
    return s

# -----------------------------
# Hirschberg helpers
# -----------------------------
def dp_bottom_row(S, T):
    """
    Compute the last row of the DP table for sequences S and T.
    Uses only O(len(T)) space.
    """
    m = len(S)
    n = len(T)

    prev = [j * delta for j in range(n + 1)]

    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        curr[0] = i * delta

        for j in range(1, n + 1):
            cost_sub = prev[j - 1] + alpha[S[i - 1]][T[j - 1]]
            cost_del = prev[j] + delta
            cost_ins = curr[j - 1] + delta

            curr[j] = min(cost_sub, cost_del, cost_ins)

        prev = curr

    return prev

def dp_last_row_reverse(S, T):
    # reverse S & T
    S_rev = S[::-1]
    T_rev = T[::-1]

    row_rev = dp_bottom_row(S_rev, T_rev)

    row = row_rev[::-1]
    return row

def hirschberg(S, T):
    m = len(S)
    n = len(T)

    if m == 0:
        return "_" * n, T
    if n == 0:
        return S, "_" * m
    if m == 1 or n == 1:
        _, ax, ay = basic.basic_dp(S, T)
        return ax, ay

    mid = m // 2

    # forward DP for left
    scoreL = dp_bottom_row(S[:mid], T)

    # backward DP for right
    scoreR = dp_last_row_reverse(S[mid:], T)

    split = 0
    best = scoreL[0] + scoreR[0]
    for j in range(1, len(scoreL)):
        if scoreL[j] + scoreR[j] < best:
            best = scoreL[j] + scoreR[j]
            split = j

    # recursive part
    leftX, leftY = hirschberg(S[:mid], T[:split])
    rightX, rightY = hirschberg(S[mid:], T[split:])

    return leftX + rightX, leftY + rightY

# -----------------------------
# Compute cost
# -----------------------------
def compute_cost(A, B):
    total = 0
    for p, q in zip(A, B):
        if p == "_" or q == "_":
            total += delta
        else:
            total += alpha[p][q]
    return total

# -----------------------------
# Memory and Time Measurement
# -----------------------------
def process_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss / 1024)
    return memory_consumed


def time_wrapper(algo):
    start_time = time.time()
    result = algo()
    end_time = time.time()
    time_taken = (end_time - start_time) * 1000
    return time_taken, result


# -----------------------------
# MAIN
# -----------------------------
def main():
    if len(sys.argv) != 3:
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    X_base, X_indices, Y_base, Y_indices = read(input_file)
    X = generate(X_base, X_indices)
    Y = generate(Y_base, Y_indices)

    mem_before = process_memory()
    time_taken, (ax, ay) = time_wrapper(lambda: hirschberg(X, Y))
    mem_after = process_memory()
    mem_used = max(0, mem_after - mem_before)

    cost = compute_cost(ax, ay)

    with open(output_file, "w") as f:
        f.write(str(cost) + "\n")
        f.write(ax + "\n")
        f.write(ay + "\n")
        f.write(str(time_taken) + "\n")
        f.write(str(mem_used) + "\n")


if __name__ == "__main__":
    main()
