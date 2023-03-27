# coding: utf8
from __future__ import annotations
from typing import Callable, Optional


class CliHelper(object):

    class _OptionNode(object):
        def __init__(self,
                     title: str = "Untitled Option",
                     func: Callable = None,  # cannot have return value
                     args: tuple = None,
                     kwargs: dict = None):
            self.title = title
            self.func = func if func is not None else self._default_func
            self.args = args if args is not None else ()
            self.kwargs = kwargs if kwargs is not None else {}
            self.children = []  # type: list[CliHelper._OptionNode]

        @staticmethod
        def _default_func():
            print("No function")

    def __init__(self):
        self._root = self._OptionNode("Main Menu")
        self._config = {
            "left_padding": 2,
            "right_padding": 10,
            "top_padding": 1,
            "bottom_padding": 1,
            "border_char": "#",
            "serial_marker": ". ",
        }

    def _draw_menu(self, p_option: _OptionNode):
        left = self._config["left_padding"]
        right = self._config["right_padding"]
        top = self._config["top_padding"]
        bottom = self._config["bottom_padding"]
        bc = self._config["border_char"]
        sm = self._config["serial_marker"]

        max_len_opt = self._get_max_length_of_options(p_option)
        max_len_serial = len(str(len(p_option.children)))
        opt_width = max_len_opt + max_len_serial + len(sm)
        menu_width = opt_width + left + right  # no border

        top_bottom_wall = f"{bc}{' ' * menu_width}{bc}"
        top_bottom_border = bc * (menu_width + len(bc) * 2)
        left_wall = f"{bc}{' ' * left}"
        right_wall = f"{' ' * right}{bc}"

        print("\n".join([top_bottom_border] + [top_bottom_wall] * top))
        i = 1
        for opt in p_option.children:
            print(f"{left_wall}{i:0{max_len_serial}}{sm}{opt.title:<{max_len_opt}}{right_wall}")
            i += 1
        print("\n".join([top_bottom_wall] * bottom + [top_bottom_border]))

    def add_option(self,
                   parent: _OptionNode = None,
                   title: str = "Untitled Option",
                   func: Callable = None,
                   args: tuple = None,
                   kwargs: dict = None) -> _OptionNode:
        if parent is None:
            parent = self._root
        option = self._OptionNode(title, func, args, kwargs)
        parent.children.append(option)

        parent.func = self._enter_level
        parent.args = (parent, )

        return option

    @staticmethod
    def _get_max_length_of_options(p_option: _OptionNode):
        return max([len(c.title) for c in p_option.children])

    def config(self, **kwargs):
        for k in kwargs:
            if k in self._config:
                self._config[k] = kwargs[k]

    @staticmethod
    def _request_input(p_option: _OptionNode) -> Optional[_OptionNode]:
        choice = input("\nYour option: ")
        if not choice.isdigit():
            print("No such option, please enter again")
            return None

        c = int(choice)
        if c < 1 or c > len(p_option.children):
            print("No such option, please enter again")
            return None

        return p_option.children[c - 1]

    def _enter_level(self, p_option: _OptionNode):
        stop = 0
        while not stop:
            if stop == 0:
                self._draw_menu(p_option)
            stop = None

            opt = self._request_input(p_option)
            if opt is None:
                continue

            stop = opt.func(*opt.args, **opt.kwargs)

        return 0

    @staticmethod
    def _return_previous_level() -> bool:
        return True

    def start_loop(self):
        self._enter_level(self._root)

    def add_return_option(self, p_option: _OptionNode = None):
        if p_option is None:
            p_option = self._root
        self.add_option(p_option, title="[Back]", func=self._return_previous_level)

    def add_exit_option(self, p_option: _OptionNode = None):
        if p_option is None:
            p_option = self._root
        self.add_option(p_option, title="[Exit]", func=exit, args=(0, ))
