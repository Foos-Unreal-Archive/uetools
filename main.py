# coding=utf-8
"""
The main UETools window.
"""
import tkinter as tk
from tkinter import ttk

from modules.functions import make_modal
from modules.PluginVersionFixerClass import PluginsBuildIdFixer


class UETools(tk.Tk):
    """
    The main UETools window.
    """

    def __init__(self):
        super().__init__()
        self.text_content = None
        self.title('UE Tools')
        self.geometry('500x500')
        self.resizable(False, False)
        self.create_widgets()
        self.keep_existing = False
        self.bind('<Key>', self.on_key)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """
        Create the widgets for the UETools window.
        """
        pack_def_options = {'ipadx': 5, 'ipady': 5, 'padx': 3, 'pady': 3}
        frm_top = tk.LabelFrame(self, text='Run Commands')
        frm_center = tk.LabelFrame(self, text='Results')
        frm_bottom = tk.LabelFrame(self)

        frm_top.pack(side=tk.TOP, fill=tk.X, **pack_def_options)
        frm_center.pack(fill=tk.X, **pack_def_options)
        frm_bottom.pack(side=tk.BOTTOM, fill=tk.X, **pack_def_options)

        btn_update = ttk.Button(frm_top, text='Fix BuildId in Plugins', command=self.run_plugins_fix_build_id)
        btn_update.pack(side=tk.LEFT, **pack_def_options)

        pack_def_options = {'ipadx': 3, 'ipady': 3}
        text_content = tk.Text(frm_center, font=('Verdana', 8))
        scrollbar_y = ttk.Scrollbar(frm_center)
        scrollbar_y.config(command=text_content.yview)
        text_content.config(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, **pack_def_options)
        text_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, **pack_def_options)

        pack_def_options = {'ipadx': 5, 'ipady': 5, 'padx': 3, 'pady': 3}
        btn_close = ttk.Button(frm_bottom, text='Close', command=self.close_app)
        btn_close.pack(side=tk.RIGHT, **pack_def_options)

        self.text_content = text_content

    def on_close(self, _event=None) -> None:
        """
        Event when the window is closing
        :param _event: the event that triggered the call of this function
        """
        self.close_window()

    def on_key(self, event) -> None:
        """
        Event when a key is pressed
        :param event: the event that triggered the call of this function
        """
        if event.keysym == 'Escape':
            self.on_close()

    def close_window(self) -> None:
        """
        Close the window
        """
        self.quit()

    def display(self, content='', keep_mode=True) -> None:
        """
        Display the content in the window. By default, ie. keep_mode==True, each new call adds the content to the existing content with a new line.
        :param content: the text to print
        :param keep_mode: whether to keep the existing content when a new one is added
        """

        if self.keep_existing:
            content += '\n'
            self.text_content.insert(tk.END, content)
        else:
            self.text_content.delete('1.0', tk.END)
            self.text_content.insert(tk.END, content)
        # set the mode at the end to allow using display() to be used to change the mode for the next call
        self.keep_existing = keep_mode

    def run_plugins_fix_build_id(self) -> None:
        """
        Open the Update Plugin Files window.
        """
        toplevel = PluginsBuildIdFixer(self, display_callback=self.display)
        make_modal(tk_root=self, tk_child=toplevel)

    def close_app(self) -> None:
        """
        Close the application.
        """
        self.destroy()


if __name__ == "__main__":
    app = UETools()
    app.mainloop()
