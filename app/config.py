import os
from configparser import ConfigParser


class cfg(object):
    def __init__(self, path) -> None:
        super().__init__()
        self.config = ConfigParser()
        self.path = path
        self.__setup()

    def __setup(self) -> None:
        if os.path.isfile(self.path):
            self.config.read(self.path)
        # section path
        self.__set_path_config()
        # section ui
        self.__set_ui_config()
        self.__save()

    def __save(self) -> None:
        with open(self.path, 'w') as cfgfile:
            self.config.write(cfgfile)

    def __set_path_config(self) -> None:
        # section path
        if not self.config.has_section('path'):
            self.config['path'] = {}
            self.config['path']['image'] = ''
            self.config['path']['template'] = ''

    def __set_ui_config(self) -> None:
        # section ui
        if not self.config.has_section('ui'):
            self.config['ui'] = {}
            self.config['ui']['window_size'] = ''

    def write(self, section, keyword, value) -> None:
        if not self.config.has_section(section):
            self.config[section] = {}
        self.config[section][keyword] = value
        self.__save()

    def read(self, section, keyword) -> str:
        self.config.read(self.path)
        value = self.config.get(section, keyword)
        return value

    def delete(self, section, keyword) -> None:
        self.config.remove_option(section, keyword)
        self.__save()
