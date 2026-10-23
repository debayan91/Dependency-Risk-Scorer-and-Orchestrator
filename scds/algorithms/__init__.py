"""
String distance algorithms for typosquatting and confusion attack detection.
"""
from scds.algorithms.distance import levenshtein_distance, jaro_similarity, jaro_winkler_similarity

__all__ = ["levenshtein_distance", "jaro_similarity", "jaro_winkler_similarity"]
