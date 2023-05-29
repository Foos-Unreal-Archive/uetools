# coding=utf-8
"""
Implementation for:
- PluginsTool: A window to update plugin files with the Custom Engine Build ID.
"""
import configparser
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox as messagebox
from modules.functions import browse_folder, log


class PluginsTool(tk.Toplevel):
    """
    A window to update plugin files with the Custom Engine Build ID.
    :param master: The parent window.
    :param display_callback: A callback function to display the result.
    """

    def __init__(self, master, display_callback=None):
        """
        Initialize the PluginsTool window with widgets.
        :param master: The parent window.
        """
        super().__init__(master)
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
        self.conf = {'engine_folder': '', 'plugins_folder': ''}
        self.build_id = ''
        self.result = ''
        self.display_callback = display_callback
        self.entry_engine_folder = None
        self.entry_plugins_folder = None
        self.title('Update Plugins')
        self.resizable(False, False)
        self.geometry('500x220')
        self.create_widgets()
        self.bind('<Key>', self.on_key)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()  # Captures keyboard events in the Toplevel window

    def create_widgets(self):
        """
        Create the widgets for the window.
        """
        pack_def_options = {'ipadx': 5, 'ipady': 5, 'padx': 3, 'pady': 3}

        frm_engine = tk.LabelFrame(self, text='Engine Path')
        frm_plugins = tk.LabelFrame(self, text='Marketplace Plugins Folder')
        frm_button = tk.LabelFrame(self, text='Commands')

        frm_engine.pack(fill=tk.X, **pack_def_options)
        frm_plugins.pack(fill=tk.X, **pack_def_options)
        frm_button.pack(fill=tk.X, **pack_def_options)

        self.entry_engine_folder = ttk.Entry(frm_engine)
        self.entry_engine_folder.pack(side=tk.LEFT, fill=tk.X, expand=True, **pack_def_options)
        btn_engine_folder = ttk.Button(frm_engine, text='Browse', command=self._browse_engine_folder)
        btn_engine_folder.pack(side=tk.LEFT, **pack_def_options)

        self.entry_plugins_folder = ttk.Entry(frm_plugins)
        self.entry_plugins_folder.pack(side=tk.LEFT, fill=tk.X, expand=True, **pack_def_options)
        btn_plugins_folder = ttk.Button(frm_plugins, text='Browse', command=self._browse_plugins_folder)
        btn_plugins_folder.pack(side=tk.LEFT, **pack_def_options)

        btn_update = ttk.Button(frm_button, text='Update Plugin Files', command=self.fix_build_id)
        btn_update.pack(**pack_def_options)

        self.load_configuration()
        self._update_paths()

    def _update_paths(self):
        """
        Update the paths in the configuration file.
        :return:
        """
        self.entry_engine_folder.delete(0, tk.END)
        self.entry_engine_folder.insert(0, self.conf['engine_folder'])
        self.entry_plugins_folder.delete(0, tk.END)
        self.entry_plugins_folder.insert(0, self.conf['plugins_folder'])

    def _browse_engine_folder(self):
        path = browse_folder()
        if os.path.isdir(path):
            self.conf['engine_folder'] = path
            self._update_paths()

    def _browse_plugins_folder(self):
        path = browse_folder()
        if os.path.isdir(path):
            self.conf['plugins_folder'] = path
            self._update_paths()

    def _extract_build_id(self) -> str:
        """
        Extract Custom Engine Build ID from the paper2D plugin from the specified engine path.
        """
        paper_plugin_path = os.path.join(self.conf['engine_folder'], 'Plugins', '2D', 'Paper2D', 'Binaries', 'Win64', 'UnrealEditor.modules')
        paper_plugin_path = os.path.abspath(paper_plugin_path)
        try:
            with open(paper_plugin_path, 'r') as file:
                data = json.load(file)
                build_id = data['BuildId']
            return build_id
        except FileNotFoundError:
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
            log(f'File not found: {json_file}')
        except json.decoder.JSONDecodeError:
            log(f'Invalid JSON file: {json_file}')
        return False

    def _find_plugins(self) -> list:
        """
        Recursively find all Unreal Engine plugins from a given directory.
        :return: A list of plugin paths.
        """
        folders_to_skip = ['Binaries', 'Build', 'DerivedDataCache', 'Intermediate', 'Saved', 'ThirdParty']
        plugin_files = []
        for root, dirs, files in os.walk(self.conf['plugins_folder']):
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
        self.destroy()

    def save_configuration(self):
        """
        Save the configuration values to a configuration file.
        """
        config = configparser.ConfigParser()
        config['Paths'] = self.conf

        with open(self.config_file, 'w') as file:
            config.write(file)

    def load_configuration(self):
        """
        Load the configuration values from a configuration file.
        """
        config = configparser.ConfigParser()
        config.read(self.config_file)

        if 'Paths' in config:
            self.conf = dict(config['Paths'])

    def fix_build_id(self) -> None:
        """
        Update plugin files in the specified engine_folder and plugins_folder.
        """
        if self.conf['engine_folder'] == '' or self.conf['plugins_folder'] == '':
            messagebox.showerror('Error', 'Engine Path or Plugins Directory not specified.')
            return
        build_id = self._extract_build_id()
        if build_id:
            self._fix_build_id_in_plugins()
            messagebox.showinfo('Command Result', 'Plugin files updated successfully.')
        else:
            messagebox.showerror('Error', 'Failed to extract Custom Engine Build ID from the specified file.')
        self.save_configuration()
        try:
            self.display_callback(self.result)
        except AttributeError:
            log('No display callback specified.')
        self.close_window()
