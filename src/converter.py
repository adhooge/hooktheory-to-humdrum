from typing import Dict

import src.chords as C
import src.kernfilebuilder as K
import src.util as U


def convert(json_data: Dict) -> str:
    # check data validity before processing
    if (
        json_data["annotations"]["melody"] is None
        or json_data["annotations"]["harmony"] is None
        or len(json_data["annotations"]["melody"]) == 0
        or len(json_data["annotations"]["harmony"]) == 0
    ):
        return ""
    # Prepare metadata
    title = U.get_title(json_data)
    artist = U.get_artist(json_data)
    id = U.get_hooktheoryid(json_data)
    metadata = K.make_reference_records(artist, title, id)
    # Prepare melody
    keys = U.get_key_signatures(json_data)
    meters = U.get_meters(json_data)
    ## Initialize melody with first key and first meter
    melody = K.melody_list_prep(keys[0][1], meters[0][1])
    ## add actual notes
    melody += K.make_notes_from_melody(
        json_data["annotations"]["melody"], meters, keys
    )
    # Prepare chords
    harmony = C.harmony_list_prep()
    harmony_tokens, melody = C.make_harmony_list(
        json_data["annotations"]["harmony"], melody, keys
    )
    harmony += harmony_tokens
    # Final string preparation
    melody.append("*-")
    harmony.append("*-")

    assert len(melody) == len(harmony)
    ## Merge Melody and harmony
    out_list = [melody[i] + "\t" + harmony[i] for i in range(len(melody))]
    ## Convert list to str
    out_str = "\n".join(out_list)

    # Combine strings
    out = metadata + out_str
    return out
