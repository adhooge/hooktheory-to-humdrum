import copy
from typing import Dict, List

from src.mode_formulas import get_accidentals_names, get_num_accidentals


def _make_kern_key(
    tonic_pitch_class: int, scale_degree_intervals: List[int]
) -> str:
    accidentals = get_accidentals_names(
        get_num_accidentals(tonic_pitch_class, scale_degree_intervals)
    )
    out = "*k["
    for acc in accidentals:
        out += acc
    out += "]"
    return out


def get_artist(json_dict: Dict) -> str:
    return json_dict["hooktheory"]["artist"]


def get_title(json_dict: Dict) -> str:
    return json_dict["hooktheory"]["song"]


def get_hooktheoryid(json_dict: Dict) -> str:
    return json_dict["hooktheory"]["id"]
