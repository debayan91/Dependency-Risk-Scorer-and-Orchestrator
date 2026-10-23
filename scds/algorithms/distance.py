"""
Deterministic string distance algorithms: Levenshtein distance & Jaro-Winkler similarity.
Implemented natively with zero external dependencies.
"""

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes the Levenshtein distance between two strings.
    Represents the minimum number of single-character edits (insertions, deletions, substitutions).
    """
    s1, s2 = s1.lower(), s2.lower()
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    # Use two rows instead of full matrix for O(min(m, n)) memory efficiency
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1] + [0] * len(s2)
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (0 if c1 == c2 else 1)
            current_row[j + 1] = min(insertions, deletions, substitutions)
        previous_row = current_row

    return previous_row[len(s2)]


def jaro_similarity(s1: str, s2: str) -> float:
    """
    Computes the Jaro similarity between two strings (0.0 to 1.0).
    """
    s1, s2 = s1.lower(), s2.lower()
    len1, len2 = len(s1), len(s2)

    if len1 == 0 and len2 == 0:
        return 1.0
    if len1 == 0 or len2 == 0:
        return 0.0
    if s1 == s2:
        return 1.0

    # Max distance window for matching characters
    match_distance = max(len1, len2) // 2 - 1
    if match_distance < 0:
        match_distance = 0

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

    if matches == 0:
        return 0.0

    # Count transpositions
    transpositions = 0
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    transpositions //= 2
    return (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0


def jaro_winkler_similarity(s1: str, s2: str, prefix_weight: float = 0.1, max_prefix_len: int = 4) -> float:
    """
    Computes the Jaro-Winkler similarity (0.0 to 1.0).
    Adds a prefix bonus to Jaro similarity for matching leading characters.
    """
    s1, s2 = s1.lower(), s2.lower()
    j_sim = jaro_similarity(s1, s2)
    if j_sim < 0.7:
        return j_sim

    # Common prefix length up to max_prefix_len (standard is 4)
    prefix_len = 0
    max_len = min(len(s1), len(s2), max_prefix_len)
    for i in range(max_len):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break

    return j_sim + (prefix_len * prefix_weight * (1.0 - j_sim))
