# code: utf8
from html import escape
from scan_bookmarks import scan_bookmarks


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


def bm2xml(browser, xml_filepath):
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

    make_xml(root, xml_filepath)