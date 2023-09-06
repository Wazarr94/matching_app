from enum import Enum
from typing import Callable, Hashable, NamedTuple, Sequence

import polars as pl
import rapidfuzz.distance as rfd
import streamlit as st
from rapidfuzz import process
from stqdm import stqdm
from string_cleaning import clean_string


class DataMatch(NamedTuple):
    df: pl.DataFrame
    col: str
    col_id: str | None


DistanceScorer = Callable[[Sequence[Hashable], Sequence[Hashable]], float]


class DistanceMatching(Enum):
    DamerauLevenshtein = rfd.DamerauLevenshtein
    Hamming = rfd.Hamming
    Indel = rfd.Indel
    Jaro = rfd.Jaro
    JaroWinkler = rfd.JaroWinkler
    Levenshtein = rfd.Levenshtein
    OSA = rfd.OSA
    Prefix = rfd.Prefix
    Postfix = rfd.Postfix


def get_distance() -> DistanceScorer:
    col1, col2 = st.columns([5, 4])

    options_matching = [dm.name for dm in DistanceMatching]
    matching_fn = col1.selectbox(
        "Select the matching function", options_matching, index=4
    )
    assert matching_fn is not None

    options_dist = [
        "distance",
        "normalized_distance",
        "similarity",
        "normalized_similarity",
    ]
    distance_fn = col2.selectbox("Select the distance function", options_dist, index=2)
    assert distance_fn is not None

    return get_distance_return(distance_fn, matching_fn)


def get_distance_return(distance_fn: str, matching_fn: str) -> DistanceScorer:
    if distance_fn == "distance":
        return DistanceMatching[matching_fn].value.distance

    elif distance_fn == "normalized_distance":
        return DistanceMatching[matching_fn].value.normalized_distance

    elif distance_fn == "similarity":
        return DistanceMatching[matching_fn].value.similarity

    elif distance_fn == "normalized_similarity":
        return DistanceMatching[matching_fn].value.normalized_similarity

    else:
        raise ValueError("Distance function not given")


def match_df(
    info_match: DataMatch,
    info_known: DataMatch,
    distance_scorer: DistanceScorer,
    limit: int,
) -> pl.DataFrame:
    df_match, col_match, col_match_id = info_match
    df_known, col_known, col_known_id = info_known

    with st.spinner("Cleaning strings of match database"):
        col_match_join = [
            col_match_id,
            col_match,
            pl.col(col_match).apply(clean_string).alias(f"{col_match}_clean"),
        ]
        columns_join_match = [val for val in col_match_join if val is not None]
        names_match_join = df_match.select(columns_join_match).unique()

    names_match_input: list[str] = (
        names_match_join.select(pl.col(f"{col_match}_clean")).to_series().to_list()
    )

    with st.spinner("Cleaning strings of known database"):
        col_known_join = [
            col_known,
            col_known_id,
            pl.col(col_known).apply(clean_string).alias(f"{col_known}_clean"),
        ]
        columns_join_known = [val for val in col_known_join if val is not None]
        names_known_join = df_known.select(columns_join_known).unique()

    names_known_input: list[str] = (
        names_known_join.select(pl.col(f"{col_known}_clean")).to_series().to_list()
    )

    matches_dict = dict()

    with st.spinner("Matching"):
        for name_match in stqdm(names_match_input):
            matches_dict[name_match] = list(
                process.extract(
                    name_match,
                    names_known_input,
                    scorer=distance_scorer,
                    limit=limit,
                )
            )

    matches_keys = []
    matches_names = []
    matches_scores = []
    matches_rank = []
    for k, value in matches_dict.items():
        matches_keys.append(k)
        matches_names.append([v[0] for v in value])
        matches_scores.append([v[1] for v in value])
        matches_rank.append(list(range(1, limit + 1)))

    col_matches = columns_join_match + columns_join_known + ["score", "rank"]
    matches = (
        pl.DataFrame(
            {
                f"{col_match}_clean": matches_keys,
                f"{col_known}_clean": matches_names,
                "score": matches_scores,
                "rank": matches_rank,
            }
        )
        .explode(f"{col_known}_clean", "score", "rank")
        .join(names_match_join, on=f"{col_match}_clean")
        .join(names_known_join, on=f"{col_known}_clean")
        .select(col_matches)
        .drop([f"{col_match}_clean", f"{col_known}_clean"])
        .sort(by=[pl.col(col_match), "rank"])
    )
    return matches
