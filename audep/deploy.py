"""
部署
"""
from abc import ABCMeta
from fabric.api import run, env, prompt, cd, sudo
from fabric.contrib.files import exists
from fabric.colors import red, green
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

        self.check_ovftool()
        self.install()

    @staticmethod
    def load_machine(host, user, passwd):
        """
        加载主机
        :param host:
        :param user:
        :param passwd:
        :return:
        """
        env.host_string = host
        env.user = user
        env.password = passwd

    def install(self):
        """
        安装
        :return:
        """
        if prompt('安装大数据系统?', default='n').startswith('y'):
            self.MC_BIGDATA_LISTS = list(self.conf.mc_bigdata)

        if self.MC_BIGDATA_LISTS:
            for name in self.MC_BIGDATA_LISTS:
                if prompt('安装{0}?'.format(name), default='n').startswith('y'):
                    self.download_mc(name)

    def download_mc(self, name):
        """
        下载服务器
        :param name:
        :return:
        """
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
            use_ftp = True
        else:
            use_ftp = False

        # 检查文件保存目录是否存在
        if not exists(self.DOWNLOAD_FOLDER):
            run('mkdir {0}'.format(self.DOWNLOAD_FOLDER))

        # 开始下载
        if use_ftp:
            self.ftp_download(mf_file)
            self.ftp_download(ovf_file)
            self.ftp_download(disk_file)

    def check_ovftool(self):
        """
        检查ovftool是否存在
        :return:
        """
        try:
            run('ovftool -v')
        except:
            print(red('ovftool不存在，开始安装ovftool：'))
            file = self.conf.dependency.get('ovftool')
            self.ftp_download(file)

            with cd(self.DOWNLOAD_FOLDER):
                filename = file.split('/')[-1]
                sudo('/bin/sh {0}'.format(filename))

    def ftp_download(self, file):
        """
        使用FTP下载数据
        :return:
        """
        try:
            ftp = self.conf.ftp
            ftpuser = ftp['user']
            ftppass = ftp['passwd']
        except:
            raise ConfigError('缺少FTP配置模块')

        dd_cmd = 'wget --ftp-user="{0}" --ftp-password="{1}" -c {2}'
        cmd_str = dd_cmd.format(ftpuser, ftppass, file)

        with cd(self.DOWNLOAD_FOLDER):
            run(cmd_str)
