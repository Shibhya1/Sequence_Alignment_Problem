delta = 30  # Gap cost

alpha = { # Substitution cost matrix
    'A': {'A': 0,   'C': 110, 'G': 48,  'T': 94},
    'C': {'A': 110, 'C': 0,   'G': 118, 'T': 48},
    'G': {'A': 48,  'C': 118, 'G': 0,   'T': 110},
    'T': {'A': 94,  'C': 48,  'G': 110, 'T': 0}
}

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

def generate_strings(filename):
    """
    Read the inputs from a file with the following format:
    Line 1: Base string S
    Line 2: Integer j (number of positions for S)
    Line 3--N: j integers (positions for S)
    Line N+1: Base string T
    Next Line: Integer k (number of positions for T)
    Next Line--End: k integers (positions for T)
    """
    with open(filename, "r") as f:

        lines = [line.strip() for line in f if line.strip()]

    # Build S
    s_base = lines[0]
    j = int(lines[1])
    s_positions = [int(x) for x in lines[2 : 2 + j]]

    # Generate S
    S = s_base
    for pos in s_positions:
        left = S[:pos + 1]
        right = S[pos + 1:]
        S = left + S + right


    # Build T
    t_start = 2 + j
    t_base = lines[t_start]
    k = int(lines[t_start + 1])
    t_positions = [int(x) for x in lines[t_start + 2 : t_start + 2 + k]]

    # Generate T
    T = t_base
    for pos in t_positions:
        left = T[:pos + 1]
        right = T[pos + 1:]
        T = left + T + right

    return S, T


if __name__ == "__main__":
    S, T = generate_strings("input.txt")

    print("\nS:", S)
    print("Size:", len(S))

    print("\nT:", T)
    print("Size:", len(T))

    last_row = dp_bottom_row(S, T)
    print("Last row DP:", last_row)
