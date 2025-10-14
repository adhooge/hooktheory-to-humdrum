from typing import Dict, List, Tuple

from src.mode_formulas import PC_TO_NAMES
from src.util import DURATION_TO_KERN, KERN_TO_DURATION, _count_accidentals


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


def _get_duration_pitch_from_kern_note(note: str) -> Tuple[str, str]:
    duration = ""
    for i, char in enumerate(note):
        if not char.isalpha():
            duration += char
        else:
            break
    duration = duration.lstrip("[")
    pitch = note[i:]
    pitch = pitch.rstrip("]")
    return duration, pitch


def _get_bar_duration(kern_meter: str) -> float:
    """
    Get the duration of a bar given kern meter notation e.g. '*M4/4'
    """
    num_beats = int(kern_meter[2])
    subdivision = int(kern_meter[-1])
    bar_duration = 4 * (num_beats / subdivision)
    return bar_duration


def _split_tied_notes(
    kern_melody: List[str], end_tie_duration: float, bar_number: int
) -> List[str]:
    last_note = kern_melody.pop()
    duration, pitch = _get_duration_pitch_from_kern_note(last_note)
    total_duration = KERN_TO_DURATION[duration]
    # First part of the tied note
    start_tie_duration = total_duration - end_tie_duration
    start_tie = DURATION_TO_KERN[start_tie_duration] + pitch
    # Second part of the tied note
    end_tie = DURATION_TO_KERN[end_tie_duration] + pitch
    # Add everything to original melody
    kern_melody += [f"[{start_tie}", f"={bar_number}", f"{end_tie}]"]
    return kern_melody


def make_notes_from_melody(
    melody: List[Dict[str, int]],
    meters: List[Tuple[int, str]],
    keys: List[Tuple[int, str]],
) -> List[str]:
    out = []
    # Initialize meter
    current_meter_idx = 0
    _, current_meter = meters[current_meter_idx]
    bar_duration = _get_bar_duration(current_meter)
    current_bar_duration = 0
    bar_counter = 1  # first bar is always prepared
    if len(meters) > 1:
        next_meter_onset = meters[current_meter_idx + 1][0]
    else:
        next_meter_onset = None
    # Initialize key
    current_key_idx = 0
    _, current_key = keys[current_key_idx]
    sharps, flats = _count_accidentals(current_key)
    use_sharps = sharps > flats
    if len(keys) > 1:
        next_key_onset = keys[current_key_idx + 1][0]
    else:
        next_key_onset = None
    # Initialize previous offset tracker
    current_onset = None
    previous_offset = 0
    for note in melody:
        current_onset = note["onset"]
        # Update meter if necessary
        if next_meter_onset is not None and current_onset >= next_meter_onset:
            current_meter_idx += 1
            _, current_meter = meters[current_meter_idx]
            if out[-1][0] != "=":
                # last melody token is not a bar but probably a tied note, we need to insert the new meter before that token.
                out.insert(-1, current_meter)
            else:
                out.append(current_meter)
            bar_duration = _get_bar_duration(current_meter)
            try:
                next_meter_onset = meters[current_meter_idx + 1][0]
            except IndexError:
                # last meter reached
                next_meter_onset = None
        # Update key if necessary
        if next_key_onset is not None and current_onset >= next_key_onset:
            current_key_idx += 1
            _, current_key = keys[current_key_idx]
            sharps, flats = _count_accidentals(current_key)
            use_sharps = sharps > flats
            if out[-1][0] != "=":
                # last melody token is not a bar but probably a tied note, we need to insert the new key before that token.
                out.insert(-1, current_key)
            else:
                out.append(current_key)
            try:
                next_key_onset = keys[current_key_idx + 1][0]
            except IndexError:
                # last key reached
                next_key_onset = None
        if current_onset > previous_offset:
            # need to add a rest
            out.append(_make_rest(current_onset - previous_offset))
            current_bar_duration += current_onset - previous_offset
        out.append(_kern_note(note, use_sharps))
        previous_offset = note["offset"]
        current_bar_duration += note["offset"] - note["onset"]
        if current_bar_duration >= bar_duration:
            bar_counter += 1
            current_bar_duration -= bar_duration
            if current_bar_duration > 0:
                # previous note should be tied between two bars
                out = _split_tied_notes(out, current_bar_duration, bar_counter)
            else:
                # just add the bar line
                out.append(f"={bar_counter}")
    # Add final rest if necessary
    if current_bar_duration < bar_duration:
        out.append(_make_rest(bar_duration - current_bar_duration))
    return out
