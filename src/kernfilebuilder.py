from typing import Dict, List, Tuple

from src.mode_formulas import PC_TO_NAMES
from src.util import (
    DURATION_TO_KERN,
    KERN_TO_DURATION,
    _count_accidentals,
    find_best_durations_combination,
    find_best_note_combination,
)


def _make_rest(duration: float) -> List[str]:
    """_make_rest.
    make krn token(s) for representing a rest

    Args:
        duration (float): duration of the rest in quarter notes

    Returns:
        List[str]: the text tokens representing the rest note. There can be several tied tokens if the duration calls for it.
    """
    out = []
    try:
        durations = [DURATION_TO_KERN[duration]]
    except KeyError:
        # weird duration should be represented with tied notes
        print(f"Couldn't find duration {duration} in known durations")
        durations = find_best_durations_combination(duration)
    for i, dur in enumerate(durations):
        token = ""
        if len(durations) == 1:
            token += dur
            token += "r"
            out.append(token)
        else:
            if i == 0:
                token = f"{dur}r"
            elif i == len(durations) - 1:
                token = f"{dur}r"
            else:
                token = f"{dur}r"
            out.append(token)
    return out


def _note_char_from_octave(pitch: str, accidental: str, octave: int) -> str:
    """_note_char_from_octave.
    Apply the rules of **kern formatting to indicate note octaves. 
    We assume that octave=0 in hooktheory is the octave of C4

    Args:
        pitch (str): pitch class char representation
        accidental (str): accidental char (b or #)
        octave (int): octave numbers from hooktheory

    Returns:
        str: kern representation of the note in the correct octave
    """
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


def _kern_note(
    pitch_class: int,
    octave: int,
    duration: float,
    use_sharps: bool = True,
    no_tie_constraints: bool = False,
    open_tie: bool = False,
    close_tie: bool = False,
) -> List[str]:
    """_kern_note.
    Generate token(s) in kern notation representing a musical note.

    Args:
        pitch_class (int): pitch_class of the note as a number between 0 and 11
        octave (int): octave as a positive or negative integer
        duration (float): duration in quarter-lengths
        use_sharps (bool): flag to favour enharmonic names with sharps
        no_tie_constraints (bool): flag to ignore open_tie and close_tie arguments
        open_tie (bool): flag to enforce the first output token to open a tie
        close_tie (bool): flag to enforce the last output token to close a tie

    Returns:
        List[str]: the text tokens representing the musical note. There can be several tied tokens if the duration calls for it.
    """
    out = []
    try:
        durations = [DURATION_TO_KERN[duration]]
    except KeyError:
        # weird duration should be represented with tied notes
        print(f"Couldn't find duration {duration} in known durations")
        durations = find_best_durations_combination(duration)
    # Now determine pitch class name and use octave info
    pcsharp, pcflat = PC_TO_NAMES[pitch_class]
    pc_char = pcsharp if use_sharps else pcflat
    pitch = pc_char[0]
    accidental = pc_char[1] if len(pc_char) > 1 else ""
    note_char = _note_char_from_octave(pitch, accidental, octave)
    for i, dur in enumerate(durations):
        token = ""
        token += dur
        token += note_char
        out.append(token)
    if len(out) > 1 and no_tie_constraints:
        open_tie, close_tie = True, True
    if open_tie:
        out[0] = "[" + out[0]
    if close_tie:
        out[-1] = out[-1] + "]"
    return out


def make_reference_records(artist: str, title: str, htid: str) -> str:
    """make_reference_records.
    Prepare the **kern "reference records" of the file
    The hooktheoryid is added as a general comment

    Args:
        artist (str): artist name
        title (str): title of the song
        htid (str): hooktheoryid

    Returns:
        str: string header to use as is in the final .krn file
    """
    COM = f"!!!COM: {artist}\n"
    OTL = f"!!!OTL: {title}\n"
    RNB = f"!!!RNB: hooktheoryid: {htid}\n"
    return COM + OTL + RNB


def melody_list_prep(key: str, meter: str):
    """melody_list_prep.
    Create headers for **kern notation of the melody 

    Args:
        key (str): krn token representing the key signature at the beginning of the melody
        meter (str): krn token representing the meter at the beginning of the melody
    """
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
    """_get_duration_pitch_from_kern_note.
    Extract the duration and the pitch of a note based on its kern token

    Args:
        note (str): krn token representing the note

    Returns:
        Tuple[str, str]: (duration, pitch)
    """
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




def make_notes_from_melody(
    melody: List[Dict[str, int]],
    meters: List[Tuple[int, str]],
    keys: List[Tuple[int, str]],
) -> List[str]:
    """make_notes_from_melody.
    Generate the list of krn tokens representing a melody from hooktheory

    Args:
        melody (List[Dict[str, int]]): Dictionary representing the melody of a song as taken from hooktheory's json
        meters (List[Tuple[int, str]]): list of (onset, meter_token) for this song
        keys (List[Tuple[int, str]]): list of (onset, key_token) for this song

    Returns:
        List[str]: list of krn tokens representing the melody
    """
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
        pitch_class = note["pitch_class"]
        octave = note["octave"]
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
        # Add a Rest if there's a jump in onsets
        if current_onset > previous_offset:
            rest_duration = current_onset - previous_offset
            if current_bar_duration + rest_duration >= bar_duration:
                first_rest_duration = bar_duration - current_bar_duration
                remaining_rest_duration = rest_duration - first_rest_duration
                out.extend(_make_rest(first_rest_duration))
                bar_counter += 1
                out.append(f"={bar_counter}")
                while remaining_rest_duration >= bar_duration:
                    out.extend(_make_rest(bar_duration))
                    remaining_rest_duration -= bar_duration
                    bar_counter += 1
                    out.append(f"={bar_counter}")
                if remaining_rest_duration > 0:
                    out.extend(_make_rest(remaining_rest_duration))
                    current_bar_duration = remaining_rest_duration
                else:
                    current_bar_duration = 0
            else:
                out.extend(_make_rest(rest_duration))
                current_bar_duration += rest_duration
        # Add the note, possible as a set of tied notes if it goes over a barline
        note_duration = note["offset"] - note["onset"]
        previous_offset = note["offset"]
        if current_bar_duration + note_duration >= bar_duration:
            ## The note overlaps two measures
            first_note_duration = bar_duration - current_bar_duration
            remaining_note_duration = note_duration - first_note_duration
            out.extend(
                _kern_note(
                    pitch_class,
                    octave,
                    first_note_duration,
                    use_sharps,
                    open_tie=remaining_note_duration > 0,
                )
            )
            bar_counter += 1
            out.append(f"={bar_counter}")
            while remaining_note_duration >= bar_duration:
                out.extend(
                    _kern_note(pitch_class, octave, bar_duration, use_sharps)
                )
                remaining_note_duration -= bar_duration
                bar_counter += 1
                out.append(f"={bar_counter}")
            if remaining_note_duration > 0:
                out.extend(
                    _kern_note(
                        pitch_class,
                        octave,
                        remaining_note_duration,
                        use_sharps,
                        close_tie=True,
                    )
                )
                current_bar_duration = remaining_note_duration
            else:
                current_bar_duration = 0
        else:
            ## The note can be added directly in one measure
            out.extend(
                _kern_note(
                    pitch_class,
                    octave,
                    note_duration,
                    use_sharps,
                    no_tie_constraints=True,
                )
            )
            current_bar_duration += note_duration
    # Add final rest if necessary
    if current_bar_duration < bar_duration:
        out.extend(_make_rest(bar_duration - current_bar_duration))
    return out
