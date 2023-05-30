# coding=utf-8
"""
Implementation for:
- PluginsBuildIdFixer: A window to update plugin files with the Custom Engine Build ID.
"""
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox as messagebox

from modules.ToolConfigClass import ToolConfig
from modules.functions import browse_folder
from modules.globals import default_engine_folder, config_folder, config_filename


class PluginsBuildIdFixer(tk.Toplevel):
    """
    A window to update plugin files with the Custom Engine Build ID.
    :param master: The parent window.
    :param display_callback: A callback function to display the result.
    """

    def __init__(self, master, display_callback=None):
        """
        Initialize the PluginsBuildIdFixer window with widgets.
        :param master: The parent window.
        """
        super().__init__(master)
        self.name = 'PluginsBuildIdFixer'
        self.description = 'Update plugin files with the Custom Engine Build ID. Read the Build ID for a given engine folder and update the plugin files in the given plugins folder.'
        self.width = 500
        self.height = 270
        self.config_file, self.config = self.init_config(self.name)
        self.build_id = ''
        self.result = ''
        self.display_callback = display_callback
        self.error_list = []
        self.title('Update Plugins')
        self.resizable(False, False)
        self.geometry(f'{self.width}x{self.height}')

        # Initialize StringVar variables for managing Entry widgets
        self.engine_folder_var = tk.StringVar()
        self.plugins_folder_var = tk.StringVar()
        self.plugins_folder_var.trace_add("write", lambda *args: self.config.set('plugins_folder', self.plugins_folder_var.get()))
        self.engine_folder_var.trace_add("write", lambda *args: self.config.set('engine_folder', self.engine_folder_var.get()))
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
            'engine_folder': default_engine_folder,  #
            'plugins_folder': os.path.join(default_engine_folder, 'Plugins/Marketplace'),  #
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
        frm_engine = tk.LabelFrame(self, text='Engine Binary Folder (source of the Build ID)')
        frm_plugins = tk.LabelFrame(self, text='Marketplace Plugins Folder (Build ID updates)')
        frm_button = tk.LabelFrame(self, text='Commands')

        lbl_description.pack(fill=tk.X, **pack_def_options)
        frm_engine.pack(fill=tk.X, **pack_def_options)
        frm_plugins.pack(fill=tk.X, **pack_def_options)
        frm_button.pack(fill=tk.X, **pack_def_options)

        # noinspection DuplicatedCode
        entry_engine_folder = ttk.Entry(frm_engine, textvariable=self.engine_folder_var)
        entry_engine_folder.pack(side=tk.LEFT, fill=tk.X, expand=True, **pack_def_options)
        btn_engine_folder = ttk.Button(frm_engine, text='Browse', command=self._browse_engine_folder)
        btn_engine_folder.pack(side=tk.LEFT, **pack_def_options)

        # noinspection DuplicatedCode
        entry_plugins_folder = ttk.Entry(frm_plugins, textvariable=self.plugins_folder_var)
        entry_plugins_folder.pack(side=tk.LEFT, fill=tk.X, expand=True, **pack_def_options)
        btn_plugins_folder = ttk.Button(frm_plugins, text='Browse', command=self._browse_plugins_folder)
        btn_plugins_folder.pack(side=tk.LEFT, **pack_def_options)

        btn_update = ttk.Button(frm_button, text='Update Plugin Files', command=self.fix_build_id)
        btn_update.pack(**pack_def_options)

        self._update_path_entries()

    def _update_path_entries(self):
        """
        Update the paths in the configuration file.
        :return:
        """
        self.engine_folder_var.set(self.config.get('engine_folder'))
        self.plugins_folder_var.set(self.config.get('plugins_folder'))

    def _browse_engine_folder(self):
        path = browse_folder()
        if os.path.isdir(path):
            self.config.set('engine_folder', path)
            self.engine_folder_var.set(path)

    def _browse_plugins_folder(self):
        path = browse_folder()
        if os.path.isdir(path):
            self.config.set('plugins_folder', path)
            self.plugins_folder_var.set(path)

    def _extract_build_id(self) -> str:
        """
        Extract Custom Engine Build ID from the paper2D plugin from the specified engine path.
        """
        paper_plugin_path = os.path.join(self.config.get('engine_folder'), 'Plugins', '2D', 'Paper2D', 'Binaries', 'Win64', 'UnrealEditor.modules')
        paper_plugin_path = os.path.abspath(paper_plugin_path)
        try:
            with open(paper_plugin_path, 'r') as file:
                data = json.load(file)
                build_id = data['BuildId']
            return build_id
        except FileNotFoundError:
            self.log(f'Could not find the the plugin we read build_id from ({paper_plugin_path}).\nThe engine path is probably wrong.')
            return ''

    def _replace_build_id(self, json_file: str) -> bool:
        """
        Replace the value of the 'BuildId' key in a JSON file.
        :param json_file: The path to the JSON file.
        :return: True if the file has been updated, False otherwise.
        """
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
            data['BuildId'] = self.build_id
            with open(json_file, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except FileNotFoundError:
            self.log(f'File not found: {json_file}')
        except json.decoder.JSONDecodeError:
            self.log(f'Invalid JSON file: {json_file}')
        return False

    def _find_plugins(self) -> list:
        """
        Recursively find all Unreal Engine plugins from a given directory.
        :return: A list of plugin paths.
        """
        folders_to_skip = ['Binaries', 'Build', 'DerivedDataCache', 'Intermediate', 'Saved', 'ThirdParty']
        plugin_files = []
        for root, dirs, files in os.walk(self.config.get('plugins_folder')):
            if any(folder in os.path.basename(root) for folder in folders_to_skip):
                continue  # Skip folders that are not plugins
            for file in files:
                if file.endswith('.uplugin'):
                    plugin_files.append(os.path.join(root, file))
                    continue
        return plugin_files

    def _fix_build_id_in_plugins(self) -> None:
        """
        Update all the plugin a plugins directory with a Custom Engine Build ID.
        """
        plugins = self._find_plugins()
        for plugin_file in plugins:
            if self._fix_build_id_in_plugin(plugin_file):
                self.result += f'Updated plugin files in {plugin_file}\n'
            else:
                self.result += f'Failed to update plugin files in {plugin_file}\n'

    def _fix_build_id_in_plugin(self, plugin_file: str) -> bool:
        """
        Update the .modules and .uplugin of a plugin files with a Custom Engine Build ID.
        :param plugin_file: The path to the plugin file.
        """
        # Update .uplugin file
        result = self._replace_build_id(plugin_file)
        # Update modules file
        plugin_path = os.path.dirname(plugin_file)
        modules_file_path = os.path.join(plugin_path, 'Binaries', 'Win64', 'UnrealEditor.modules')
        result = result and self._replace_build_id(modules_file_path)
        return result

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

    def fix_build_id(self) -> None:
        """
        Update plugin files in the specified engine_folder and plugins_folder.
        """
        if self.config.get('engine_folder') == '' or self.config.get('plugins_folder') == '':
            messagebox.showerror('Error', 'Engine Path or Plugins Directory not specified.')
            return
        build_id = self._extract_build_id()
        if build_id:
            self._fix_build_id_in_plugins()
            messagebox.showinfo('Command Result', 'Plugin files updated successfully.')
        else:
            messagebox.showerror('Error', 'Failed to extract Custom Engine Build ID from the specified file.')
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
