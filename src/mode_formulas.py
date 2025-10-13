from typing import List

MODES_INTERVALS = {
    "ionian": [2, 2, 1, 2, 2, 2],
    "dorian": [2, 1, 2, 2, 2, 1],
    "phrygian": [1, 2, 2, 2, 1, 2],
    "lydian": [2, 2, 2, 1, 2, 2],
    "mixolydian": [2, 2, 1, 2, 2, 1],
    "aeolian": [2, 1, 2, 2, 1, 2],
    "locrian": [1, 2, 2, 1, 2, 2],
}

# Ignoring Double-flats or double sharps for now
PC_TO_NAMES = {
    0: ("C", "C"),
    1: ("C#", "Db"),
    2: ("D", "D"),
    3: ("D#", "Eb"),
    4: ("E", "E"),
    5: ("F", "F"),
    6: ("F#", "Gb"),
    7: ("G", "G"),
    8: ("G#", "Ab"),
    9: ("A", "A"),
    10: ("A#", "Bb"),
    11: ("B", "B"),
}


# Relative major offset (in semitones below modal tonic)
MODE_TO_MAJOR_OFFSET = {
    "ionian": 0,
    "dorian": -2,
    "phrygian": -4,
    "lydian": -5,
    "mixolydian": -7,
    "aeolian": -9,
    "locrian": -11,
}

SHARPS = ["f#", "c#", "g#", "d#", "a#", "e#", "b#"]
FLATS = ["b-", "e-", "a-", "d-", "g-", "c-", "f-"]

# Number of sharps (positive) or flats (negative) for each key
KEY_SIGNATURES = {
    "C": 0,
    "G": 1,
    "D": 2,
    "A": 3,
    "E": 4,
    "B": 5,
    "F#": 6,
    "C#": 7,
    "F": -1,
    "Bb": -2,
    "Eb": -3,
    "Ab": -4,
    "Db": -5,
    "Gb": -6,
    "Cb": -7,
}


def identify_mode(intervals: List[int]) -> str:
    for mode, sdi in MODES_INTERVALS.items():
        if intervals == sdi:
            return mode
    raise ValueError(
        f"Unknown mode with scale degree intervals {scale_degree_intervals}"
    )


def get_num_accidentals(modal_tonic: int, intervals: List[int]) -> int:
    mode = identify_mode(intervals)

    # Find parent major pitch class
    parent_major_pc = (modal_tonic + MODE_TO_MAJOR_OFFSET[mode]) % 12

    sharp_name, flat_name = PC_TO_NAMES[parent_major_pc]
    # assume that correct key is the one that minimises number of accidentals
    acc1 = KEY_SIGNATURES.get(sharp_name, 999)
    acc2 = KEY_SIGNATURES.get(flat_name, 999)
    acc = acc1 if acc1 < abs(acc2) else acc2
    return acc


def get_accidentals_names(num_accidentals: int) -> List[str]:
    if num_accidentals >= 0:
        return SHARPS[:num_accidentals]
    else:
        return FLATS[:-num_accidentals]
