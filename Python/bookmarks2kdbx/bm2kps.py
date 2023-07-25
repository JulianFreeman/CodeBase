# code: utf8

# Change Log:
#
# v0.1 粗糙的命令行英文版本，能用
#

import os
import sys
from html import escape
from pathlib import Path

from scan_bookmarks import scan_bookmarks
from clihelper import CliHelper, request_input


def args_match(args: tuple, count: int, a_types: tuple) -> bool:
    if len(args) != count:
        return False

    for ori, exp in zip(args, a_types):
        if not isinstance(ori, exp):
            return False

    return True


class Entry(object):
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def to_dict(self):
        return {
            "Title": self.title,
            "URL": self.url
        }

    def to_xml(self):
        return f"""<Entry>
            <String>
                <Key>Title</Key>
                <Value>{self.title}</Value>
            </String>
            <String>
                <Key>URL</Key>
                <Value>{self.url}</Value>
            </String>
        </Entry>"""


class Group(object):
    def __init__(self, name):
        self.name = name
        self.entries = []
        self.groups = []

    def add_entry(self, *args):
        if args_match(args, 1, (Entry, )):
            e = args[0]
            self.entries.append(e)
        elif args_match(args, 2, (str, str)):
            title, url = args
            e = Entry(title, url)
            self.entries.append(e)
        else:
            raise TypeError
        return e

    def add_group(self, *args):
        if args_match(args, 1, (Group, )):
            g = args[0]
            self.groups.append(g)
        elif args_match(args, 1, (str, )):
            name = args[0]
            g = Group(name)
            self.groups.append(g)
        else:
            raise TypeError
        return g

    def get_group(self, name):
        for g in self.groups:
            if g.name == name:
                return g
        else:
            g = self.add_group(name)
            return g

    def to_xml(self):
        head = f"""<Group>
            <Name>{self.name}</Name>
            {{entries}}
            {{groups}}
        </Group>"""
        entries = "\n".join([e.to_xml() for e in self.entries])
        groups = "\n".join([g.to_xml() for g in self.groups])
        return head.format(entries=entries, groups=groups)

    def to_dict(self):
        return {
            "Name": self.name,
            "Entry": [
                e.to_dict() for e in self.entries
            ],
            "Group": [
                g.to_dict() for g in self.groups
            ]
        }


def make_xml(group, filepath):
    with open(filepath, "w", encoding="utf8") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<KeePassFile>
    <Root>
        {group.to_xml()}
    </Root>
</KeePassFile>""")


def add_browser_prefix(browser, filepath):
    filepath_p = Path(filepath)
    filepath_pp = filepath_p.parent
    filename = filepath_p.name
    new_filepath = str(Path(filepath_pp, f"{browser}_{filename}"))

    return new_filepath


def xml2kps(kps_cli_path, xml_filepath, filepath):
    cmd = f""""{kps_cli_path}" import {xml_filepath} {filepath}"""
    os.system(cmd)
    os.remove(xml_filepath)


def bm2xml(browser, kps_cli_path, xml_filepath, filepath):
    new_xml_filepath = add_browser_prefix(browser, xml_filepath)
    new_filepath = add_browser_prefix(browser, filepath)

    bm_db, _ = scan_bookmarks(browser)
    root = Group("Bookmarks")
    for url in bm_db:
        info = bm_db[url]
        name = info["name"]
        prof, addr = info["profiles_pos"][0]  # type: str, str

        sub_g = root.get_group(prof)
        d_addr = addr.split("/")
        ln_d_addr = len(d_addr)

        i = 1
        ss_g = sub_g
        while i < ln_d_addr:
            ss_g = ss_g.get_group(d_addr[i])
            i += 1
        ss_g.add_entry(escape(name), escape(url))

    make_xml(root, new_xml_filepath)
    print("Generating the .kdbx file...")
    xml2kps(kps_cli_path, new_xml_filepath, new_filepath)
    print(f"\nSuccessfully export the bookmarks of [{browser}] to [{new_filepath}].")

    return CliHelper._RETURN_CODE


def check_filepath(filepath):
    p = Path(filepath)
    pp = p.parent
    return pp.is_dir() and not p.exists()


def main():
    filepath, b = request_input(
        "Enter the file path to save the .kdbx",
        "The path is invalid or already exists.",
        check_func=check_filepath, ask_again=True,
    )
    if b is False:
        print("Quit.")
        sys.exit(0)

    if not filepath.endswith(".kdbx"):
        filepath += ".kdbx"
    xml_filepath = filepath + ".xml"

    plat = sys.platform
    default_kps_cli_path = {
        "win32": r"C:\Program Files\KeePassXC\keepassxc-cli.exe",
        "darwin": r"/Applications/KeePassXC.app/Contents/MacOS/keepassxc-cli"
    }

    kps_cli_path, b = request_input(
        "Enter the path of keepassxc_cli",
        "keepassxc_cli file does not detected.",
        has_default_val=True,
        default_val=default_kps_cli_path[plat],
        check_func=lambda x: Path(x).exists(), ask_again=True,
    )
    if b is False:
        print("Quit.")
        sys.exit(0)

    clihelper = CliHelper(show_version=False)
    clihelper.add_option(title="Chrome", exec_func=bm2xml, args=("Chrome", kps_cli_path, xml_filepath, filepath))
    clihelper.add_option(title="Edge", exec_func=bm2xml, args=("Edge", kps_cli_path, xml_filepath, filepath))
    clihelper.add_option(title="Brave", exec_func=bm2xml, args=("Brave", kps_cli_path, xml_filepath, filepath))
    clihelper.start_loop()


if __name__ == '__main__':
    main()
