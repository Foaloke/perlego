from functools import reduce

from source.la.treebank.converter import is_pnoun, print_word
from utils.lambda_utils import lmap

PNOUN_CLUSTER_TYPE = "pnoun_cluster"


def is_dot(w):
    return w["form"] == "."


def are_adjacents(wA, wB):
    wA_start = wA["start_index"]
    wA_next = wA["end_index"]
    if wA["space"]:
        wA_next = wA_next + 1
    wB_start = wB["start_index"]
    wB_next = wB["end_index"]
    if wB["space"]:
        wB_next = wB_next + 1
    return wA_next == wB_start or wB_next == wA_start


def have_same_case(wA, wB):
    return wA["postag"] == wB["postag"]


def is_pnoun_word_or_dot(w):
    return is_pnoun(w["lemma"], w["form"], w["postag"]) or is_dot(w)


def cluster_dots_or_adjacent_and_in_same_case(acc, curr):
    for cluster in acc:
        for item_in_cluster in cluster:
            one_is_dot = is_dot(item_in_cluster) or is_dot(curr)
            same_postag = have_same_case(item_in_cluster, curr)
            adjacents = are_adjacents(item_in_cluster, curr)
            if (same_postag or one_is_dot) and adjacents:
                cluster.append(curr)
                return acc
    acc.append([curr])
    return acc


def trim_dots(cluster):
    index = 0
    while index < len(cluster) and is_dot(cluster[index]):
        index = index + 1
    start_index = index
    index = len(cluster) - 1
    while index > 0 and is_dot(cluster[index]):
        index = index - 1
    end_index = index + 1
    return cluster[start_index:end_index]


def not_empty(array):
    return len(array) > 0


def to_info(pnoun_cluster):
    pnoun_cluster.sort(key=lambda item: item["start_index"])
    return {
        "start_index": pnoun_cluster[0]["start_index"],
        "end_index": pnoun_cluster[len(pnoun_cluster) - 1]["end_index"],
        "type": PNOUN_CLUSTER_TYPE,
        "label": "".join(
            lmap(lambda i: print_word(i, as_lemma=True), pnoun_cluster)
        ).strip(),
    }


def cluster_pnouns(words):
    # Filter pnouns or dots only
    # (Dots may be part of an abbreviated name)
    pnouns_and_dot = filter(is_pnoun_word_or_dot, words)
    # Clustering adjacent pnouns with same latin case, or dots in between them
    pnouns_clusters_and_dots = reduce(
        cluster_dots_or_adjacent_and_in_same_case, pnouns_and_dot, []
    )
    # We clustered pnouns declined in the same latin case
    # so clusters can only accept dots if they are
    # in between non-dot tokens with the same latin case.
    # Any other dot can only be the result
    # of accidental clustering of dots without pnouns.
    pnouns_clusters_trimmed_dots = lmap(trim_dots, pnouns_clusters_and_dots)
    # If a cluster was made with accidentally clustered dots only,
    # trimming must have made it empty, so remove it
    pnouns_clusters = filter(not_empty, pnouns_clusters_trimmed_dots)
    return lmap(to_info, pnouns_clusters)
