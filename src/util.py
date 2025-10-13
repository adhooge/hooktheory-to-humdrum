import copy
from typing import Dict, List

from src.mode_formulas import get_accidentals_names, get_num_accidentals

DURATION_TO_KERN = {
    4: "1",  # whole note
    2: "2",  # half note
    1.5: "4.",  # dotted quarter note
    1: "4",  # quarter note
    0.75: "8.",  # dotted 8th note
    0.5: "8",  # 8th
    0.25: "16",  # 16th
}

KERN_TO_DURATION = {v: k for k, v in DURATION_TO_KERN.items()}


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


def get_key_signatures(json_dict: Dict) -> List:
    out = []
    keys = json_dict["annotations"]["keys"]
    for key in keys:
        beat = key["beat"]
        tpc = key["tonic_pitch_class"]
        sdi = key["scale_degree_intervals"]
        kern_key = _make_kern_key(tpc, sdi)
        out.append((beat, kern_key))
    return out


def get_meters(json_dict: Dict) -> List:
    out = []
    meters = json_dict["annotations"]["meters"]
    for meter in meters:
        beat = meter["beat"]
        num_beats = meter["beats_per_bar"]
        subdivision = meter["beat_unit"]
        kern_meter = f"*M{num_beats}/{subdivision}"
        out.append((beat, kern_meter))
    return out
