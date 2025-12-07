import sys
import time
import psutil


# ---------------------------------------------------------------------------
# Input String Generator
# ---------------------------------------------------------------------------
# The input contains:
#   1. A base string X_base
#   2. j integers (insertion indices) used to repeatedly expand X_base
#   3. A base string Y_base
#   4. k integers (insertion indices) used to expand Y_base
#
# This function reads the file and separates these four components exactly
# according to the project specification.
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# String Generation
# ---------------------------------------------------------------------------
# Using the provided base string and a list of insertion indices:
# For each index i, insert the entire current string immediately
# AFTER position i (0-indexed). Each step doubles the string length.
# ---------------------------------------------------------------------------
def generate(base, indices):
    s = base
    for i in indices:
        if i < 0 or i > len(s) - 1:
            raise ValueError("Invalid insertion index")
        else:
            pos = i + 1
            s = s[:pos] + s + s[pos:]
    return s

# ---------------------------------------------------------------------------
# Cost Parameters (Provided in Assignment)
# ---------------------------------------------------------------------------
delta = 30 # Gap penalty

# Mismatch/Match cost table α(p,q)
alpha = {
    'A': {'A': 0, 'C': 110, 'G': 48, 'T': 94},
    'C': {'A': 110, 'C': 0, 'G': 118, 'T': 48},
    'G': {'A': 48, 'C': 118, 'G': 0, 'T': 110},
    'T': {'A': 94, 'C': 48, 'G': 110, 'T': 0}
}

# ---------------------------------------------------------------------------
# Basic Dynamic Programming (Bottom-Up)
# ---------------------------------------------------------------------------
# Builds the full (m+1) × (n+1) DP table for classical sequence alignment.
# dp[i][j] = minimum cost of aligning X[:i] with Y[:j]
# ---------------------------------------------------------------------------
def bottom_up(X, Y):
    # Initialize DP table
    m = len(X)
    n = len(Y)
    dp = []
    for i in range(m + 1):
        dp.append([0] * (n + 1))

    # Base cases: aligning with empty string
    for i in range(1, m + 1):
        dp[i][0] = i * delta
    for j in range(1, n + 1):
        dp[0][j] = j * delta

    # Fill DP table using recurrence
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # recurrence formula
            dp[i][j] = min(
                dp[i - 1][j - 1] + alpha[X[i - 1]][Y[j - 1]],  # match/ mismatch between X and Y
                dp[i - 1][j] + delta,  # gap in Y
                dp[i][j - 1] + delta  # gap in X
            )

    return dp

# ---------------------------------------------------------------------------
# Backtracking (Top-Down)
# ---------------------------------------------------------------------------
# Reconstructs one optimal alignment by following the DP table backwards.
# Produces:
#   alignment_x: aligned version of X (with '_')
#   alignment_y: aligned version of Y (with '_')
# ---------------------------------------------------------------------------
def top_down(X, Y, dp):
    alignment_x = []
    alignment_y = []
    i = len(X)
    j = len(Y)

    while i > 0 and j > 0:
        if dp[i][j] == dp[i - 1][j - 1] + alpha[X[i - 1]][Y[j - 1]]:
            alignment_x.append(X[i - 1])
            alignment_y.append(Y[j - 1])
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + delta:
            alignment_x.append(X[i - 1])
            alignment_y.append("_")
            i -= 1
        else:
            alignment_x.append("_")
            alignment_y.append(Y[j - 1])
            j -= 1

    while i > 0:
        alignment_x.append(X[i - 1])
        alignment_y.append("_")
        i -= 1

    while j > 0:
        alignment_x.append("_")
        alignment_y.append(Y[j - 1])
        j -= 1

    return "".join(alignment_x[::-1]), "".join(alignment_y[::-1])

# ---------------------------------------------------------------------------
# Basic DP Wrapper
# Runs bottom-up DP, retrieves cost, and reconstructs alignment.
# ---------------------------------------------------------------------------
def basic_dp(X, Y):
    dp_table = bottom_up(X, Y)
    process = psutil.Process()

    current_mem = process.memory_info().rss / 1024

    cost = dp_table[len(X)][len(Y)]
    alignment_x, alignment_y = top_down(X, Y, dp_table)

    return cost, alignment_x, alignment_y, current_mem

# ---------------------------------------------------------------------------
# Memory and Time Measurement
# ---------------------------------------------------------------------------
def process_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss / 1024)
    return memory_consumed


def time_wrapper(algo):
    start_time = time.perf_counter()
    result = algo()
    end_time = time.perf_counter()
    time_taken = (end_time - start_time) * 1000
    return time_taken, result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) != 3:
        return
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read and generate full strings
    X_base, X_indices, Y_base, Y_indices = read(input_file)
    X = generate(X_base, X_indices)
    Y = generate(Y_base, Y_indices)

    # Measure memory + time around alignment
    mem_before = process_memory()
    time_taken, (cost, alignment_x, alignment_y, memory_used) = time_wrapper(lambda: basic_dp(X, Y))
    # mem_after = process_memory()
    # memory_used = max(0, mem_after - mem_before)

    # Write results to output file (required format)
    with open(output_file, "w") as f:
        f.write(str(cost) + "\n")
        f.write(alignment_x + "\n")
        f.write(alignment_y + "\n")
        f.write(str(time_taken) + "\n")
        f.write(str(memory_used) + "\n")


if __name__ == "__main__":
    main()
