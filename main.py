# coding=utf-8
"""
The main UETools window.
"""
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo

from modules.FolderCleanerClass import FolderCleaner
from modules.functions import make_modal
from modules.PluginVersionFixerClass import PluginsBuildIdFixer


class UETools(tk.Tk):
    """
    The main UETools window.
    """

    def __init__(self):
        super().__init__()
        self.text_content = None
        self.keep_existing = False
        self.width = 500
        self.height = 500
        self.file_types = (('csv file', '*.csv'), ('tcsv file', '*.tcsv'), ('json file', '*.json'), ('text file', '*.txt'))

        self.title('UE Tools')
        self.resizable(False, False)
        self.geometry(f'{self.width}x{self.height}')

        self.create_widgets()
        self.bind('<Key>', self.on_key)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """
        Create the widgets for the UETools window.
        """
        pack_def_options = {'ipadx': 5, 'ipady': 5, 'padx': 3, 'pady': 3}
        lblf_top = tk.LabelFrame(self, text='Run Commands')
        lblf_content = tk.LabelFrame(self, text='Results')
        lblf_bottom = tk.LabelFrame(self)

        lblf_top.pack(side=tk.TOP, fill=tk.X, **pack_def_options)
        lblf_content.pack(fill=tk.X, **pack_def_options)
        lblf_bottom.pack(side=tk.BOTTOM, fill=tk.X, **pack_def_options)

        btn_plugins_fix_build_id = ttk.Button(lblf_top, text='Fix BuildId in Plugins', command=self.run_plugins_fix_build_id)
        btn_plugins_fix_build_id.pack(side=tk.LEFT, **pack_def_options)
        btn_folder_cleaner = ttk.Button(lblf_top, text='Clean projects folder', command=self.run_folder_cleaner)
        btn_folder_cleaner.pack(side=tk.LEFT, **pack_def_options)

        pack_def_options = {'ipadx': 3, 'ipady': 3}
        text_content = tk.Text(lblf_content, font=('Verdana', 8))
        scrollbar_y = ttk.Scrollbar(lblf_content)
        scrollbar_y.config(command=text_content.yview)
        text_content.config(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, **pack_def_options)
        text_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, **pack_def_options)

        pack_def_options = {'ipadx': 5, 'ipady': 5, 'padx': 3, 'pady': 3}
        ttk.Button(lblf_bottom, text='Clean content', command=self.clean).pack(**pack_def_options, side=tk.LEFT)
        ttk.Button(lblf_bottom, text='Save To File', command=self.save_to_file).pack(**pack_def_options, side=tk.LEFT)
        ttk.Button(lblf_bottom, text='Close', command=self.close_app).pack(**pack_def_options, side=tk.RIGHT)

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

    def clean(self) -> None:
        """
        Clean the content of the window
        """
        self.text_content.delete('1.0', tk.END)

    def save_to_file(self) -> str:
        """
        Save the content displayed to a file
        """
        filename = asksaveasfilename(title='Choose a file to save text to', filetypes=self.file_types, initialfile='results.txt')
        if filename:
            with open(filename, 'w') as f:
                f.write(self.text_content.get('1.0', tk.END))
            showinfo(self.wm_title(), f'Content Saved to {filename}')
        return filename

    def run_plugins_fix_build_id(self) -> None:
        """
        Open the Update Plugin Files window.
        """
        toplevel = PluginsBuildIdFixer(self, display_callback=self.display)
        make_modal(tk_root=self, tk_child=toplevel)

    def run_folder_cleaner(self) -> None:
        """
        Open the Folder Cleaner window.
        """
        toplevel = FolderCleaner(self, display_callback=self.display)
        make_modal(tk_root=self, tk_child=toplevel)

    def close_app(self) -> None:
        """
        Close the application.
        """
        self.destroy()


if __name__ == "__main__":
    app = UETools()
    app.mainloop()
