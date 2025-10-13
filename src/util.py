from typing import Dict


def get_artist(json_dict: Dict) -> str:
    return json_dict["hooktheory"]["artist"]


def get_title(json_dict: Dict) -> str:
    return json_dict["hooktheory"]["song"]


def get_hooktheoryid(json_dict: Dict) -> str:
    return json_dict["hooktheory"]["id"]
