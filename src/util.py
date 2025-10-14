import copy
from itertools import product
from typing import Dict, List, Tuple

from src.mode_formulas import get_accidentals_names, get_num_accidentals


def _count_accidentals(key_token: str) -> Tuple[int, int]:
    sharps = key_token.count("#")
    flats = key_token.count("-")
    return sharps, flats


DURATION_TO_KERN = {
    4: "1",  # whole note
    3: "2.",  # dotted half note
    2: "2",  # half note
    1.75: "4..",  # double dotted quarter note
    1.5: "4.",  # dotted quarter note
    1: "4",  # quarter note
    0.75: "8.",  # dotted 8th note
    0.5: "8",  # 8th
    0.25: "16",  # 16th
}

KERN_TO_DURATION = {v: k for k, v in DURATION_TO_KERN.items()}


def find_best_note_combination(
    duration, last_note_duration=None, tolerance=1e-6
):
    """
    Find an efficient representation (fewest notes) of a total duration
    using standard note values and dotted versions, with an optional constraint
    that the final tied note must have a given duration.

    Parameters:
        duration: float (1 = whole note)
        last_note_duration: optional float (if set, final note duration is fixed)
        tolerance: float for rounding tolerance
    """
    usable_durations = list(DURATION_TO_KERN.keys())

    sorted_dur = sorted(usable_durations, reverse=True)

    result = []
    last_note = None
    remaining = duration

    if last_note_duration is not None:
        # Check if last note exists in our known durations
        matching_notes = [
            dur
            for dur in sorted_dur
            if abs(dur - last_note_duration) < tolerance
        ]
        if not matching_notes:
            last_note = find_best_note_combination(last_note_duration)
            last_note = [KERN_TO_DURATION[r] for r in last_note]
        else:
            last_note = [matching_notes[0]]  # we'll add it at the end
        remaining -= last_note_duration

    for val in sorted_dur:
        count = int(remaining // val)
        if count > 0:
            result.extend([val] * count)
            remaining -= count * val
        if remaining < 0:
            raise ValueError
        if remaining < tolerance:
            break

    if remaining > tolerance:
        print(
            f"⚠️ Warning: Could not perfectly represent duration {duration}, remainder={remaining}"
        )

    if last_note is not None:
        result.extend(last_note)

    return [DURATION_TO_KERN[r] for r in result]


def find_best_durations_combination(duration, tolerance=1e-6):
    """
    Find the most efficient representation (fewest notes) of a total duration
    using standard note values and dotted versions.

    duration: float (1 = whole note)
    """
    usable_durations = list(DURATION_TO_KERN.keys())

    # Sort descending by value (greedy-friendly)
    sorted_dur = sorted(usable_durations, reverse=True)

    result = []
    remaining = duration

    for val in sorted_dur:
        count = int(remaining // val)
        if count > 0:
            result.extend([val] * count)
            remaining -= count * val
        if remaining < 0:
            raise ValueError
        if remaining < tolerance:
            break

    if remaining > tolerance:
        print(
            f"⚠️ Warning: Could not perfectly represent duration {duration}, remainder={remaining}"
        )
    return [DURATION_TO_KERN[r] for r in result]


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
