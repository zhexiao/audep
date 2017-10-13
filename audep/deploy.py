"""
部署
"""
from abc import ABCMeta
from fabric.api import run, env, prompt, cd
from fabric.contrib.files import exists

from audep.hdexceptions import ConfigError


class DeployAbstract(metaclass=ABCMeta):
    def __init__(self):
        pass


class Deploy(DeployAbstract):
    MC_BIGDATA_LISTS = []
    DOWNLOAD_FOLDER = '~/download'

    def __init__(self, config_obj):
        self.conf = config_obj

        self.load_machine(
            config_obj.server.get('host'),
            config_obj.server.get('user'),
            config_obj.server.get('passwd')
        )

        self.install()

    @staticmethod
    def load_machine(host, user, passwd):
        env.host_string = host
        env.user = user
        env.password = passwd

    def install(self):
        if prompt('安装大数据系统?', default='n').startswith('y'):
            self.MC_BIGDATA_LISTS = list(self.conf.mc_bigdata)

        if self.MC_BIGDATA_LISTS:
            for name in self.MC_BIGDATA_LISTS:
                if prompt('安装{0}?'.format(name), default='n').startswith('y'):
                    self.download_mc(name)

    def download_mc(self, name):
        data_info = self.conf.mc_bigdata.get(name).split(',')
        # 如果提供了名字
        if len(data_info) == 2:
            ovf_file, mc_name = data_info
        else:
            ovf_file = data_info[0]
            mc_name = name

        # 去掉空白
        ovf_file, mc_name = ovf_file.strip(), mc_name.strip()
        disk_file = '{0}-disk1.vmdk'.format(ovf_file.split('.ovf')[0])
        mf_file = '{0}.mf'.format(ovf_file.split('.ovf')[0])

        # 检查是否是ftp下载
        if ovf_file.startswith('ftp'):
            ftp_download = True
        else:
            ftp_download = False

        if not exists(self.DOWNLOAD_FOLDER):
            run('mkdir {0}'.format(self.DOWNLOAD_FOLDER))

        with cd(self.DOWNLOAD_FOLDER):
            if ftp_download:
                try:
                    ftp = self.conf.ftp
                    ftpuser = ftp['user']
                    ftppass = ftp['passwd']

                except:
                    raise ConfigError('缺少FTP配置模块')

                command = 'wget --ftp-user="{0}" --ftp-password="{1}" -c {2}'
                str = command.format(ftpuser, ftppass, mf_file)
                print(str)


