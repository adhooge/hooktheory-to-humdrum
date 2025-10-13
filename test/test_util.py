import json

import pytest

from src.util import _make_kern_key, get_artist, get_hooktheoryid, get_title


# Load the JSON file once for all tests
@pytest.fixture
def json_data():
    with open("data/fileExample.json", "r") as f:
        j = json.load(f)
    return list(j.values())[0]


def test_get_artist(json_data):
    result = get_artist(json_data)
    assert result == "adam-lambert"


def test_get_title(json_data):
    result = get_title(json_data)
    assert result == "whataya-want-from-me"


def test_get_hooktheoryid(json_data):
    result = get_hooktheoryid(json_data)
    assert result == "qveoYyGGodn"


def test_make_kern_key(json_data):
    tonic = json_data["annotations"]["keys"][0]["tonic_pitch_class"]
    sdi = json_data["annotations"]["keys"][0]["scale_degree_intervals"]
    result = _make_kern_key(tonic, sdi)
    assert result == "*k[f#c#]"
