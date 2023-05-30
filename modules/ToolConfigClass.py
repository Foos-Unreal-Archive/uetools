# coding=utf-8
"""
Implementation for:
- ToolConfig: A class to manage configuration values.
"""
import configparser
import os

from modules.globals import config_folder, config_filename


class ToolConfig:
    """
    A class to manage configuration values for a specific tool.
    Note: A tool is a window in the application. Each tool has its own section in the configuration file.
    """

    def __init__(self, init_values: dict, section: str, config_file: str = None):
        """
        Initialize the Config object.
        :param init_values: Initialisation values for the options in the section.
        :param section: Section to set
        :param config_file: Configuration file to use. If None, the default configuration file is used (see globals.py)
        """
        if os.path.isdir(config_folder) is False:
            os.makedirs(config_folder)

        self.section = section
        if config_file is None:
            self.config_file = os.path.join(os.path.join(config_folder, config_filename))
        else:
            self.config_file = config_file

        self.config = configparser.ConfigParser()
        if not self.config.has_section(section):
            self.config.add_section(section)

        # set initial values, will be overwritten when loading the config file
        for key, value in init_values.items():
            self.set(key, value)

    def get(self, option: str, default=None):
        """
        Get a configuration value.
        :param option: Option to get
        :param default: Default value if the key is not found
        :return: The value of the key or the default value
        """
        return self.config.get(self.section, option, fallback=default)

    def set(self, option: str, value) -> None:
        """
        Set a configuration value.
        :param option: Option to set
        :param value: Value to set
        """
        self.config.set(self.section, option, value)

    def save(self):
        """
        Save the configuration values to a configuration file.
        """
        with open(self.config_file, 'w') as file:
            self.config.write(file)

    def load(self):
        """
        Load the configuration values from a configuration file.
        """
        if os.path.isfile(self.config_file):
            self.config.read(self.config_file)
