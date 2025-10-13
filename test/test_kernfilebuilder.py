from src.kernfilebuilder import _note_char_from_octave


def test_note_char_from_octave():
    assert _note_char_from_octave("C", "", 0) == "c"
    assert _note_char_from_octave("C", "b", 0) == "c-"
    assert _note_char_from_octave("C", "#", 0) == "c#"
    assert _note_char_from_octave("C", "", 1) == "cc"
    assert _note_char_from_octave("C", "#", 2) == "ccc#"
    assert _note_char_from_octave("C", "b", 3) == "cccc-"
    assert _note_char_from_octave("C", "", -1) == "C"
    assert _note_char_from_octave("C", "#", -2) == "CC#"
    assert _note_char_from_octave("C", "b", -3) == "CCC-"
