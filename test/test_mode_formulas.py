import json

import pytest

from src.mode_formulas import (
    get_accidentals_names,
    get_num_accidentals,
    identify_mode,
)


# Load the JSON file once for all tests
@pytest.fixture
def json_data():
    with open("data/fileExample.json", "r") as f:
        j = json.load(f)
    return list(j.values())[0]


def test_identify_mode(json_data):
    assert identify_mode([2, 2, 1, 2, 2, 2]) == "ionian"
    assert (
        identify_mode(
            json_data["annotations"]["keys"][0]["scale_degree_intervals"]
        )
        == "ionian"
    )


def test_get_num_accidentals(json_data):
    # simple C major
    assert get_num_accidentals(0, [2, 2, 1, 2, 2, 2]) == 0
    # simple D major
    modal_tonic = json_data["annotations"]["keys"][0]["tonic_pitch_class"]
    sdi = json_data["annotations"]["keys"][0]["scale_degree_intervals"]
    assert get_num_accidentals(modal_tonic, sdi) == 2
    # G dorian
    assert get_num_accidentals(7, [2, 1, 2, 2, 2, 1]) == -1
    # Bb minor
    assert get_num_accidentals(10, [2, 1, 2, 2, 1, 2]) == -5


def test_get_accidentals_names():
    # C major
    assert get_accidentals_names(0) == []
    # D major
    assert get_accidentals_names(2) == ["f#", "c#"]
    # G dorian
    assert get_accidentals_names(-1) == ["b-"]
    # Bb minor
    assert get_accidentals_names(-5) == ["b-", "e-", "a-", "d-", "g-"]
