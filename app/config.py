import os
from configparser import ConfigParser

PATH = "./config.ini"


class cfg(object):
    def __init__(self, path) -> None:
        super().__init__()
        self.config = ConfigParser()
        self.path = path
        self.__setup()

    def __setup(self) -> None:
        if os.path.isfile(self.path):
            self.config.read(self.path)
        # section1 network
        self.__set_network_config()
        # section2 path
        self.__set_path_config()
        # section3 ui
        self.__set_ui_config()
        self.__save()

    def __save(self) -> None:
        with open(self.path, 'w') as cfgfile:
            self.config.write(cfgfile)

    def __set_network_config(self) -> None:
        # section1 network
        if not self.config.has_section('network'):
            self.config['network'] = {}
            self.config['network']['ip'] = input("IP:")
            self.config['network']['port'] = input("Port:")

    def __set_path_config(self) -> None:
        # section2 path
        if not self.config.has_section('path'):
            self.config['path'] = {}
            self.config['path']['image'] = './app/img/'
            self.config['path']['template'] = './app/template/'

    def __set_ui_config(self) -> None:
        # section2 path
        if not self.config.has_section('ui'):
            self.config['ui'] = {}
            self.config['ui']['window_size'] = input("window_size(1920x1080):")

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

