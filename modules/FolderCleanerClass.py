# coding=utf-8
"""
Implementation for:
- FolderCleaner: A window to clean UE projects from build and intermediate folders.
"""
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox as messagebox
# https://ttkwidgets.readthedocs.io/en/sphinx_doc/ttkwidgets
import ttkwidgets as ttkw

# next import adds a hook to allow the -tooltips options to be added to tk widgets.
# it's not correctly detected by pycharm, but it works.
# noinspection PyUnresolvedReferences
from ttkwidgets import tooltips

from modules.ToolConfigClass import ToolConfig
from modules.functions import browse_folder
from modules.globals import config_folder, config_filename


class FolderCleaner(tk.Toplevel):
    """
    A window to clean UE projects from build and intermediate folders.
    :param master: The parent window.
    :param display_callback: A callback function to display the result.
    """

    def __init__(self, master, display_callback=None):
        super().__init__(master)
        self.name = 'FolderCleaner'
        self.description = 'Clean UE projects from build and intermediate folders.'
        self.width = 500
        self.height = 600
        self.config_file, self.config = self.init_config(self.name)
        self.build_id = ''
        self.result = f'\n###########\nRUNNING {self.name}\n###########\n'
        self.display_callback = display_callback
        self.error_list = []
        self.folder_list = []  # List of ALL the folders that have been found

        self.title('Projects Cleaner')
        self.resizable(False, False)
        self.geometry(f'{self.width}x{self.height}')

        self.btn_execute = None
        self.content_tree = None  # The treeview widget, with the list of SELECTED folders
        self.projects_folder_var = tk.StringVar()
        self.projects_folder_var.trace_add("write", lambda *args: self.config.set('projects_folder', self.projects_folder_var.get()))
        self.create_widgets()
        self.bind('<Key>', self.on_key)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()  # Captures keyboard events in the Toplevel window

    @staticmethod
    def init_config(section: str) -> tuple[str, ToolConfig]:
        """
        Initialize the config file and default value for this window.
        :return: The config file name and config object.
        """
        defaults = {
            'projects_folder': '',  #
        }
        config_file = os.path.join(os.path.join(config_folder, config_filename))
        config = ToolConfig(init_values=defaults, section=section)
        config.load()
        return config_file, config

    def create_widgets(self):
        """
        Create the widgets for the window.
        """
        pack_def_options = {'ipadx': 5, 'ipady': 5, 'padx': 3, 'pady': 3}
        lbl_description = ttk.Label(self, text=self.description, wraplength=int(self.width * .9), font='TkDefaultFont 9 bold')
        lbl_description.pack(fill=tk.X, **pack_def_options)

        lblf_top = tk.LabelFrame(self, text='Folder that contains projects to clean')
        lblf_top.pack(fill=tk.X, **pack_def_options)

        # Folder list frame
        lblf_content = ttk.LabelFrame(self, text='List of folders to clean')
        lblf_content.pack(fill=tk.X, **pack_def_options)
        content_tree = ttkw.CheckboxTreeview(lblf_content, selectmode='extended', columns='Folder')
        content_tree.column('#0', width=30, stretch=tk.NO)
        content_tree.heading('#0', text='Ck', anchor=tk.W)
        content_tree.heading('Folder', text='Subfolder', anchor=tk.CENTER)
        scrollbar = ttkw.AutoHideScrollbar(lblf_content, command=content_tree.yview)
        content_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.content_tree = content_tree
        lblf_bottom = tk.LabelFrame(self, text='Commands')
        lblf_bottom.pack(fill=tk.X, **pack_def_options)

        # noinspection DuplicatedCode
        entry_projects = ttk.Entry(lblf_top, textvariable=self.projects_folder_var)
        entry_projects.pack(side=tk.LEFT, fill=tk.X, expand=True, **pack_def_options)
        btn_projects = ttk.Button(lblf_top, text='Browse', command=self._browse_projects)
        btn_projects.pack(side=tk.LEFT, **pack_def_options)

        # noinspection DuplicatedCode
        ttk.Button(lblf_bottom, text='Close', command=self.close_window).pack(**pack_def_options, side=tk.RIGHT)
        ttk.Button(lblf_bottom, text='Find folders', command=self.find, state=tk.NORMAL).pack(side=tk.LEFT, **pack_def_options)
        self.btn_execute = ttk.Button(lblf_bottom, text='Clean projects', command=self.execute, state=tk.DISABLED)
        self.btn_execute.pack(side=tk.LEFT, **pack_def_options)

        self._update_widgets_from_config()

    def _update_widgets_from_config(self):
        """
        Update the widgets with the configuration file values.
        """
        self.projects_folder_var.set(self.config.get('projects_folder'))

    def _browse_projects(self):
        path = browse_folder()
        if os.path.isdir(path):
            self.config.set('projects_folder', path)
            self.projects_folder_var.set(path)

    def _find_folders(self) -> list:
        """
        Recursively find all the folder to clean from a given directory.
        :return: A list of folder paths.
        """
        names_to_clean = ['Binaries', 'Build', 'DerivedDataCache', 'Intermediate']
        folder_list = []
        self.content_tree.delete(*self.content_tree.get_children())
        for root, dirs, files in os.walk(self.config.get('projects_folder')):
            for to_clean in names_to_clean:
                for dir_name in dirs:
                    if to_clean == dir_name:
                        path = os.path.join(root, dir_name)
                        path = os.path.normpath(path)
                        text = path.replace('\\', '/').replace(
                            " ", "\\ "
                        )  # escape spaces and backslashes bnecause they can't be displayed in the treeview
                        folder_list.append(path)
                        # values field will be displayed in the treeview
                        # text field are used to retrieve the path when the folder is selected
                        self.content_tree.insert('', 'end', text=path, values=text, tags='checked')
        return folder_list

    def _clean_folders(self) -> None:
        """
        Clean all the folders in the list.
        """

        # get selected folders
        selected_indexes = self.content_tree.get_checked()
        if len(selected_indexes) == 0:
            self.result += 'No folder to clean has been selected.'
            return
        folder_list = []
        for index in selected_indexes:
            # path = self.content_tree.item(index)['values'][0]
            path = self.content_tree.item(index)['text']
            folder_list.append(path)

        for folder in folder_list:
            try:
                # check if the folder is still there, it could have been deleted when its parent was deleted
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
                    self.result += f'Cleaned {folder}\n'
            except Exception as error:
                self.result += f'Failed to clean {folder}: error {error!r}\n'

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
        self.config.save()
        self.destroy()

    def log(self, message: str) -> None:
        """
        Log a message to the console.
        :param message: The message to log.
        """
        print(f'[{self.__class__.__name__}] {message}')
        self.error_list.append(message)

    def find(self) -> None:
        """
        Find the projects to clean.
        """
        if not self.config.get('projects_folder'):
            messagebox.showerror('Error', 'Projects Directory not specified.')
            return

        self.folder_list = self._find_folders()
        count = len(self.folder_list)
        if count > 0:
            self.btn_execute.config(state=tk.NORMAL)
        else:
            messagebox.showinfo('Command Result', f'No folder to clean has been found.')
            self.btn_execute.config(state=tk.DISABLED)

    def execute(self) -> None:
        """
        Execute the main command for that window.
        """
        if len(self.folder_list) < 1:
            messagebox.showerror('Error', 'The list of project to clean is empty.')
            return

        self._clean_folders()
        messagebox.showinfo('Command Result', 'Folder cleaned successfully.')

        self.config.save()
        if len(self.error_list) > 0:
            self.result += '\n###########\nErrors\n###########\n'
            self.result += '\n'.join(self.error_list)
        else:
            self.result += '\n###########\nNo Errors\n###########\n'
        try:
            self.display_callback(self.result)
        except AttributeError:
            self.log('No display callback specified.')
        self.close_window()
