"""
部署
"""
from abc import ABCMeta
import re
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
    USE_FTP = True

    def __init__(self, config_obj):
        self.conf = config_obj

        self.load_machine(
            config_obj.server.get('host'),
            config_obj.server.get('user'),
            config_obj.server.get('passwd')
        )

        self.check_prerequisite()
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
                    self.process_mc(name)

    def process_mc(self, name):
        """
        处理虚拟机
        :param name:
        :return:
        """
        ovf_file, mc_name, filename = self.format_name(name)

        # 获得disk和mf文件
        tmp_ftp_url = ovf_file.split('.ovf')[0]
        disk_file = '{0}-disk1.vmdk'.format(tmp_ftp_url)
        mf_file = '{0}.mf'.format(tmp_ftp_url)

        # 开始下载
        if self.USE_FTP:
            self.ftp_download(mf_file)
            self.ftp_download(ovf_file)
            self.ftp_download(disk_file)

        # 导入虚拟机
        self.import_mc(filename, mc_name)

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

    def check_prerequisite(self):
        """
        检查一些先决必须条件
        :return:
        """
        # 检查文件保存目录是否存在
        if not exists(self.DOWNLOAD_FOLDER):
            run('mkdir {0}'.format(self.DOWNLOAD_FOLDER))

        # 检查是否已经安装了ovftool
        self.check_ovftool()

    def format_name(self, name):
        """
        格式化名字，获取虚拟机的名字和url
        :param name:
        :return:
        """
        data_info = self.conf.mc_bigdata.get(name).split(',')
        # 如果提供了名字
        if len(data_info) == 2:
            ovf_file, mc_name = data_info
        # 如果没有提供名字，则默认读取文件的名字
        else:
            ovf_file = data_info[0]
            mc_name = re.sub(r'\.ovf', '', ovf_file.split('/')[-1])

        # 去掉空白
        ovf_file, mc_name = ovf_file.strip(), mc_name.strip()
        filename = ovf_file.split('/')[-1]

        # 检查是否是ftp下载
        if ovf_file.startswith('ftp'):
            self.USE_FTP = True
        else:
            self.USE_FTP = False

        return ovf_file, mc_name, filename

    def import_mc(self, filename, mc_name):
        """
        将虚拟机导入到vsphere中
        :param filename:
        :param mc_name:
        :return:
        """
        try:
            vsphere = self.conf.vsphere
            host = vsphere['host']
            user = vsphere['user']
            passwd = vsphere['passwd']
            data_storage = vsphere['data-storage']
            data_center = vsphere['data-center']
            cluster = vsphere['cluster']
        except:
            raise ConfigError('缺少必要的Vsphere配置模块')

        cmd_str = ('ovftool -ds={data_storage} -n={mc_name} {filename} '
                   'vi://{user}:{passwd}@{host}/{data_center}/host/{cluster}')
        cmd = cmd_str.format(data_storage=data_storage, mc_name=mc_name,
                             filename=filename, user=user, passwd=passwd,
                             host=host,
                             data_center=data_center, cluster=cluster)

        with cd(self.DOWNLOAD_FOLDER):
            run(cmd)
