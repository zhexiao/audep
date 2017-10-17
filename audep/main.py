# -*- coding: utf-8 -*-
# !/usr/bin/python3
"""
自动化部署 入口文件
"""

import argparse
import configparser
from audep.deploy import Deploy
from audep.hdexceptions import ConfigError


class Arguments(object):
    """
    命令行参数
    """
    CONFIG_FILE = None

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='自动化部署')
        self.run()

    def run(self):
        # 配置参数
        self.parser.add_argument(
            '-c', '--config', help='配置文件路径'
        )
        args = self.parser.parse_args()

        # 验证文件
        self.CONFIG_FILE = args.config
        if not self.CONFIG_FILE:
            raise ConfigError('缺少配置文件')


class ConfigValidate(object):
    """
    验证配置文件
    """
    REQUIRED_PARAMS = {
        'server': ['host', 'user', 'passwd'],
        'network': ['gateway'],
        'mc_bigdata': [],
        'dependency': ['ovftool'],
        'vsphere': ['host', 'user', 'passwd', 'data-storage', 'data-center',
                    'cluster']
    }

    def __init__(self, config_file):
        self.config_file = config_file
        self.configure = configparser.ConfigParser()
        self.configure.read(config_file)

    def validate(self):
        """
        验证配置文件的参数
        :return:
        """
        for sc, params in self.REQUIRED_PARAMS.items():
            # 验证section
            if sc not in self.configure.sections():
                raise ConfigError('缺少配置模块：{0}'.format(sc))

            # 验证参数params
            for pm in params:
                if pm not in list(self.configure[sc]):
                    raise ConfigError('缺少配置变量：{0}下面需要{1}'.format(
                        sc, pm
                    ))

        return True

    def __getattr__(self, item):
        """
        简化数据的读取
        :param item:
        :return:
        """
        try:
            return self.configure[item]
        except ConfigError as e:
            return None


def run():
    # 生成参数
    ag = Arguments()

    # 验证配置文件
    cv = ConfigValidate(ag.CONFIG_FILE)
    if cv.validate():
        Deploy(config_obj=cv)
