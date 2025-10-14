import copy
from typing import Dict, List, Tuple

from src.kernfilebuilder import _get_duration_pitch_from_kern_note
from src.mode_formulas import PC_TO_NAMES
from src.util import DURATION_TO_KERN, KERN_TO_DURATION, _count_accidentals

CHORD_INTERVALS = {
    "major": [4, 3],  # Tonic, major 3rd, perfect 5th
    "minor": [3, 4],  # Tonic, minor 3rd, perfect 5th
    "diminished": [3, 3],  # Tonic, minor 3rd, diminished 5th
    "sus4": [5, 2],  # Tonic, p4th, p5th
    "add9": [4, 3, 7],  # Tonic, M3rd, p5th, M9th
    "madd9": [3, 4, 7],  # Tonic, m3rd, p5th, M9th
    "7sus4": [5, 2, 3],  # Tonic, p4th, p5th, minor 7th
    "seventh": [4, 3, 3],  # Tonic, major 3rd, P5th, minor 7th
    "minseventh": [3, 4, 3],  # Tonic, minor 3rd, P5th, minor 7th
    "majseventh": [4, 3, 4],  # Tonic, major 3rd, P5th, major 7th
}

CHORD_DISPLAY_NAMES = {
    "major": lambda x: x.upper(),
    "minor": lambda x: x.upper() + "m",
    "diminished": lambda x: x.upper() + "dim",
    "sus4": lambda x: x.upper() + "sus4",
    "add9": lambda x: x.upper() + "add9",
    "madd9": lambda x: x.upper() + "madd9",
    "7sus4": lambda x: x.upper() + "7sus4",
    "seventh": lambda x: x.upper() + "7",
    "minseventh": lambda x: x.upper() + "min7",
    "majseventh": lambda x: x.upper() + "maj7",
}


def _invert_chord(
    chord: Dict, token: str, inversion: int, use_sharps: bool = True
) -> str:
    """_invert_chord.
    Define common possible inversions, that affect the displayed name of the chord 

    Args:
        chord (Dict): chord json representation from hooktheory
        token (str): token representing the chord as text, to use in 
        inversion (int): inversion number
        use_sharps (bool): flag to use note names with sharps rather than flats

    Returns:
        str: token representing the inverted chord
    """
    out = token
    match inversion:
        case 1:
            # Get pitch class of third to add correct bass note
            root = chord["root_pitch_class"]
            third = (root + chord["root_position_intervals"][0]) % 12
            sharp_3, flat_3 = PC_TO_NAMES[third]
            bass = sharp_3 if use_sharps else flat_3
            out += f"/{bass}"
        case 2:
            # Get pitch class of fifth to add correct bass note
            root = chord["root_pitch_class"]
            fifth = (
                root
                + chord["root_position_intervals"][0]
                + chord["root_position_intervals"][1]
            ) % 12
            sharp_5, flat_5 = PC_TO_NAMES[fifth]
            bass = sharp_5 if use_sharps else flat_5
            out += f"/{bass}"
        case 3:
            # Get pitch class of seventh to add correct bass note
            root = chord["root_pitch_class"]
            seventh = (
                root
                + chord["root_position_intervals"][0]
                + chord["root_position_intervals"][1]
                + chord["root_position_intervals"][2]
            ) % 12
            sharp_7, flat_7 = PC_TO_NAMES[seventh]
            bass = sharp_7 if use_sharps else flat_7
            out += f"/{bass}"
        case _:
            raise ValueError(
                f"Currently unsupported inversion {inversion} for chord {chord}"
            )
    return out


def harmony_list_prep():
    """harmony_list_prep.
    Create headers for **kern notation of chords
    """
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
    """make_chord_kern.
    Create text token to represent a chord in **kern
    
    Args:
        chord (Dict): chord json representation from hooktheory
        use_sharps (bool): flag to favour enharmonic notes with sharps

    Returns:
        str: chord token
    """
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
    ## Make flat lowercase if there was any
    if len(root) > 1 and root[-1] == "b":
        assert token[1] == "B"
        token = token[0] + "b" + token[2:]
    # Deal with inversion
    inversion = chord["inversion"]
    if inversion != 0:
        token = _invert_chord(chord, token, inversion, use_sharps)
    return token


def _make_tied_notes(note_token: str, end_tie_duration: float) -> List[str]:
    """_make_tied_notes.
    Split an existing note token in kern representation between two tied-notes

    Args:
        note_token (str): note_token to split
        end_tie_duration (float): duration (in quarter notes) of the second tied note

    Returns:
        List[str]: tied notes tokens
    """
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
    ) -> Tuple[List[str], List[str]]:
    """make_harmony_list.
    Iterate over the json harmonic content to generate the kern notation for the chords.

    Args:
        harmony_json (List[Dict]): list of dict objects representing the chords, from hooktheory's json.
        melody_tokens (List[str]): list of str objects corresponding to the **kern notation of the melody.
        keys (List[Tuple[int, str]]): List of (onset, key_token) pairs in case the key changes during the song. 

    Returns:
        Tuple[List[str], List[str]]: 1st list is the **kern notation for the chords, 2nd list for the melody because it can be modified by this function
    """
    out = []
    # Initialize key
    _, current_key = keys[0]
    sharps, flats = _count_accidentals(current_key)
    use_sharps = sharps >= flats
    # Initialize melody onset tracker
    melody_onset = 0
    # Prepare chord variables
    current_chord = harmony_json[0]
    chord_onset = current_chord["onset"]
    next_chord_idx = 1
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
        entered_while = False
        # Write chord token if the onset is reached
        while chord_onset is not None and melody_onset >= chord_onset:
            entered_while = True
            out.append(make_chord_kern(current_chord, use_sharps))
            split_notes = False
            if melody_onset > chord_onset:
                split_notes = True
                # To write the chord properly, we need to split the melody here
                split = i - 1
                split_token = melody[split]
                if split_token[0] == "=":
                    # splitting right on a bar line, go back one token
                    split = i - 2
                    split_token = melody[split]
                    # we also need to invert the last two tokens in out
                    out.insert(-1, out.pop())
                melody_left = melody[:split]
                melody_right = melody[split + 1 :]
                new_tokens = _make_tied_notes(
                    split_token, melody_onset - chord_onset
                )
                i += 1
                melody = melody_left + new_tokens + melody_right
            try:
                current_chord = harmony_json[next_chord_idx]
                next_chord_idx += 1
                chord_onset = current_chord["onset"]
            except IndexError:
                # we already used all chords
                chord_onset = None
            if split_notes:
                if (chord_onset is not None and chord_onset > melody_onset) or (
                    chord_onset is None and len(out) < len(melody)
                ):
                    out.append(".")
        if not entered_while:
            out.append(".")
        duration, _ = _get_duration_pitch_from_kern_note(note_token)
        melody_onset += KERN_TO_DURATION[duration]
        i += 1
    return out, melody_headers + melody
