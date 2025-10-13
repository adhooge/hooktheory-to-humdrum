from typing import Dict

import src.kernfilebuilder as K
import src.util as U


def convert(json_data: Dict) -> str:
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
    melody += K.make_notes_from_melody(json_data["annotations"]["melody"])
    ## Convert list to str
    melody = "\n".join(melody)

    # Combine strings
    out = metadata + melody + "*-"
    return out
