from typing import Dict, List

from src.mode_formulas import PC_TO_NAMES
from src.util import DURATION_TO_KERN


def _make_rest(duration: float) -> str:
    kern_duration = DURATION_TO_KERN[duration]
    return kern_duration + "r"


def _note_char_from_octave(pitch: str, accidental: str, octave: int) -> str:
    if accidental == "b":
        # flat in kern is '-'
        accidental = "-"
    if octave == 0:
        return pitch.lower() + accidental
    elif octave > 0:
        # higher octaves require to repeat lowercase letter
        return (pitch.lower() * (octave + 1)) + accidental
    else:
        # lower octaves require to repeat highcase letter
        return (pitch * abs(octave)) + accidental


def _kern_note(note: Dict[str, int], use_sharps: bool = True) -> str:
    """
    Inputs:
    - note (Dict[str, int]), as taken from hooktheory representation. Should have 4 keys: onset, offset, octave, and pitch_class.
    Output:
    - Corresponding kern notation
    """
    out = ""
    onset, offset, octave, pc = (
        note["onset"],
        note["offset"],
        note["octave"],
        note["pitch_class"],
    )
    # Start with duration number
    duration = offset - onset
    out += DURATION_TO_KERN[duration]
    # Now determine pitch class name and use octave info
    pcsharp, pcflat = PC_TO_NAMES[pc]
    pc_char = pcsharp if use_sharps else pcflat
    pitch = pc_char[0]
    accidental = pc_char[1] if len(pc_char) > 1 else ""
    note_char = _note_char_from_octave(pitch, accidental, octave)
    out += note_char
    return out


def make_reference_records(artist: str, title: str, htid: str) -> str:
    COM = f"!!!COM: {artist}\n"
    OTL = f"!!!OTL: {title}\n"
    RNB = f"!!!RNB: hooktheoryid: {htid}\n"
    return COM + OTL + RNB


def melody_list_prep(key: str, meter: str):
    # Define basic kern score
    out = ["**kern"]
    # Melodies are written in Treble clef by default
    out.append("*clefG2")
    # Add Key signature and meter
    out.append(key)
    out.append(meter)
    # Start first measure
    out.append("=1")
    return out


def make_notes_from_melody(melody: List[Dict[str, int]]) -> List[str]:
    out = []
    current_onset = None
    previous_offset = 0
    for note in melody:
        current_onset = note["onset"]
        if current_onset > previous_offset:
            # need to add a rest
            out.append(_make_rest(current_onset - previous_offset))
        out.append(_kern_note(note))
        previous_offset = note["offset"]
        # TODO: controler la duree de facon cumulative pour ajouter des silences quand c'est necessaire
    return out
