# coding=utf-8
"""
Global  functions 
"""
from tkinter import filedialog


def browse_folder() -> str:
    """
    Open a directory browser and set the selected path to the given entry widget
    :return: The selected path
    """
    folder = filedialog.askdirectory()
    return folder


def make_modal(tk_root, tk_child):
    """
    Make a tk_child windows displayed as a modal window.
    :param tk_root: root tk windows
    :param tk_child: tk_child tk window
    :return:
    """
    tk_child.transient(tk_root)
    tk_child.grab_set()
    tk_child.focus_set()
    tk_child.wait_window()
