import copy
from typing import Dict, List, Tuple

from src.kernfilebuilder import _get_duration_pitch_from_kern_note
from src.mode_formulas import PC_TO_NAMES
from src.util import DURATION_TO_KERN, KERN_TO_DURATION, _count_accidentals

CHORD_INTERVALS = {
    "major": [4, 3],  # Tonic, major 3rd, perfect 5th
    "minor": [3, 4],  # Tonic, minor 3rd, perfect 5th
}

CHORD_DISPLAY_NAMES = {
    "major": lambda x: x.upper(),
    "minor": lambda x: x.upper() + "m",
}


def harmony_list_prep():
    # Define basic text score
    out = ["**text"]
    # fill empty lines to match the melody header
    out.append("*")
    out.append("*")
    out.append("*")
    # Start first measure
    out.append("=1")
    return out


def make_chord_kern(chord: Dict, use_sharps: bool = True) -> str:
    # Get chord root name
    sharp_root, flat_root = PC_TO_NAMES[chord["root_pitch_class"]]
    root = sharp_root if use_sharps else flat_root
    # Identify chord nature
    intervals = chord["root_position_intervals"]
    nature = None
    for nat, intrv in CHORD_INTERVALS.items():
        if intervals == intrv:
            nature = nat
            break
    if nature is None:
        raise ValueError(f"Unknown chord nature with intervals {intervals}")
    # Prepare chord token
    token = CHORD_DISPLAY_NAMES[nature](root)
    return token


def _make_tied_notes(note_token: str, end_tie_duration: float) -> List[str]:
    duration, pitch = _get_duration_pitch_from_kern_note(note_token)
    total_duration = KERN_TO_DURATION[duration]
    # First part of the tied note
    start_tie_duration = total_duration - end_tie_duration
    start_tie = DURATION_TO_KERN[start_tie_duration] + pitch
    # Second part of the tied note
    end_tie = DURATION_TO_KERN[end_tie_duration] + pitch
    out = [f"[{start_tie}L", f"{end_tie}]J"]
    return out


def make_harmony_list(
    harmony_json: List[Dict],
    melody_tokens: List[str],
    keys: List[Tuple[int, str]],
) -> List[str]:
    out = []
    # Initialize key
    _, current_key = keys[0]
    sharps, flats = _count_accidentals(current_key)
    use_sharps = sharps >= flats
    # Initialize melody onset tracker
    melody_onset = 0
    # Prepare chord variables
    current_chord = harmony_json[0]
    print(current_chord)
    chord_onset = current_chord["onset"]
    next_chord_idx = 1
    chord_added = False
    # Strip melody headers
    melody_headers = []
    melody = copy.deepcopy(melody_tokens)
    while melody[0][0] in ["*", "!", "%", "="]:
        melody_headers.append(melody.pop(0))
    # Iterate over melody to count time elapsed
    i = 0
    while i < len(melody):
        note_token = melody[i]
        if note_token[0] == "=":
            # it's a bar token, copy it
            out.append(note_token)
            i += 1
            continue
        elif note_token[0] == "*":
            # can be a new meter or key token
            if note_token[1] == "k":
                current_key = note_token
                sharps, flats = _count_accidentals(current_key)
                use_sharps = sharps >= flats
            out.append("*")
            i += 1
            continue
        if melody_onset >= chord_onset:
            out.append(make_chord_kern(current_chord, use_sharps))
            if melody_onset > chord_onset:
                # To write the chord properly, we need to split the melody here
                split = i - 1
                melody_left = melody[:split]
                melody_right = melody[split + 1 :]
                split_token = melody[split]
                new_tokens = _make_tied_notes(
                    split_token, melody_onset - chord_onset
                )
                i += 1
                melody = melody_left + new_tokens + melody_right
                out.append(".")
            try:
                current_chord = harmony_json[next_chord_idx]
                next_chord_idx += 1
                chord_onset = current_chord["onset"]
            except IndexError:
                # we already used all chords
                pass
        else:
            out.append(".")
        duration, _ = _get_duration_pitch_from_kern_note(note_token)
        melody_onset += KERN_TO_DURATION[duration]
        i += 1
    return out, melody_headers + melody
