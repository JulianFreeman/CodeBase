# coding: utf8
from clihelper import CliHelper


def open_file():
    print("File Opened")


def new_folder(name):
    print(f"Folder [{name}] created")


c = CliHelper()
c.config(right_padding=20)
n = c.add_option(title="New")
c.add_option(title="Open File", func=open_file)
c.add_option(title="Save")
c.add_exit_option()

c.add_return_option(n)
c.add_option(n, "New File")
c.add_option(n, "New Folder", new_folder, ("Temp",))
c.add_exit_option(n)

c.start_loop()
