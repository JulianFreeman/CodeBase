from typing import overload
from os import PathLike


class Entry:
    title: str
    url: str

    def __init__(self, title: str, url: str): ...
    def to_dict(self) -> dict: ...
    def to_xml(self) -> str: ...


class Group:
    name: str
    entries: list[Entry]
    groups: list[Group]

    def __init__(self, name: str): ...

    @overload
    def add_entry(self, title: str, url: str) -> Entry: ...
    @overload
    def add_entry(self, entry: Entry) -> Entry: ...
    @overload
    def add_group(self, name: str) -> Group: ...
    @overload
    def add_group(self, group: Group) -> Group: ...
    def get_group(self, name: str) -> Group: ...
    def to_xml(self) -> str: ...
    def to_dict(self) -> dict: ...


def make_xml(group: Group, filepath: str | PathLike): ...

def is_google_drive_url(url: str) -> bool: ...

def bm2xml(browser: str, xml_filepath: str, google_only: bool): ...