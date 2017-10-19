"""
部署
"""
from abc import ABCMeta
import re
import json
import os
import time
from fabric.api import run, env, prompt, cd, sudo
from fabric.contrib.files import exists, sed
from fabric.colors import red, green
from audep.hdexceptions import ConfigError


class BaseAbstract(metaclass=ABCMeta):
    def __init__(self):
        pass

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


class Deploy(BaseAbstract):
    MC_BIGDATA_LISTS = []
    DOWNLOAD_FOLDER = '~/download'
    USE_FTP = True

    def __init__(self, config_obj):
        self.conf = config_obj

        self.switch_ovftool_server()

        self.check_prerequisite()
        self.install()

    def install(self):
        """
        安装
        :return:
        """
        if prompt('安装大数据系统?', default='n').startswith('y'):
            self.MC_BIGDATA_LISTS = list(self.conf.mc_bigdata)

        if self.MC_BIGDATA_LISTS:
            for name in self.MC_BIGDATA_LISTS:
                message = green('安装{0}?'.format(name))
                if prompt(message, default='n').startswith('y'):
                    # 切换到ovftool服务器
                    self.switch_ovftool_server()
                    # 下载安装虚拟机
                    self.process_mc(name)
                    time.sleep(3)

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
            self.install_ovftool()

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

        cmd_str = ('ovftool -ds={data_storage} -n={mc_name} --powerOn '
                   '--X:injectOvfEnv --acceptAllEulas --X:logFile=ovftool.log '
                   '--X:logLevel=trivia --diskMode=thin '
                   '--X:enableHiddenProperties --allowExtraConfig '
                   '--noSSLVerify --X:waitForIp '
                   '{filename} '
                   'vi://{user}:{passwd}@{host}/{data_center}/host/{cluster}')
        cmd = cmd_str.format(data_storage=data_storage, mc_name=mc_name,
                             filename=filename, user=user, passwd=passwd,
                             host=host,
                             data_center=data_center, cluster=cluster)

        with cd(self.DOWNLOAD_FOLDER):
            run(cmd)

        # 配置机器
        ConfigureMachine(config_obj=self.conf, mc_name=mc_name)

    def install_ovftool(self):
        """
        安装ovftool
        :return:
        """
        file = self.conf.dependency.get('ovftool')
        self.ftp_download(file)

        with cd(self.DOWNLOAD_FOLDER):
            filename = file.split('/')[-1]
            sudo('/bin/sh {0}'.format(filename))

    def switch_ovftool_server(self):
        """
        切换到ovftool服务器
        :return:
        """
        self.load_machine(
            self.conf.server.get('host'),
            self.conf.server.get('user'),
            self.conf.server.get('passwd')
        )


class ConfigureMachine(BaseAbstract):
    INTERFACE_FILE = '/etc/network/interfaces'
    INSTALL_INFO = 'audep_install.json'
    USED_IP = []

    def __init__(self, config_obj, mc_name=None):
        self.conf = config_obj
        self.mc_name = mc_name

        self.load_machine(
            config_obj.mc_server.get('host'),
            config_obj.mc_server.get('user'),
            config_obj.mc_server.get('passwd')
        )

        self.check_prerequisite()
        self.configure()

    def check_prerequisite(self):
        """
        检查前置条件是否满足
        :return:
        """
        # 不存在文件，则创建文件
        if not os.path.exists(self.INSTALL_INFO):
            with open(self.INSTALL_INFO, 'w'):
                pass
        # 读取文件，获得已经使用了的IP地址
        else:
            with open(self.INSTALL_INFO, 'r') as fh:
                data = fh.read()

            if data:
                json_data = json.loads(data)
                for dt in json_data:
                    self.USED_IP.append(dt['ip_address'])

    def configure(self):
        """
        配置
        :return:
        """
        self.setup_network()

    def setup_network(self):
        """
        设置网络
        :return:
        """
        ip_range_str = self.conf.network.get('address_range')
        ip_exclude_str = self.conf.network.get('address_exclude')
        netmask = self.conf.network.get('netmask')
        gateway = self.conf.network.get('gateway')
        dns_nameservers = self.conf.network.get('dns-nameservers')

        # 格式化ip range
        try:
            ip_range = ip_range_str.split('~')
            ip_start = int(ip_range[0])
            ip_end = int(ip_range[1])
        except:
            raise ConfigError('address_range格式不正确')

        # 格式化ip exclude
        if ip_exclude_str:
            try:
                ip_exclude_list = [int(i) for i in ip_exclude_str.split(',')]
                self.USED_IP.extend(ip_exclude_list)
            except:
                raise ConfigError('address_exclude格式不正确')

        # 得到允许使用的IP
        allowed_ip = None
        for ip in range(ip_start, ip_end + 1):
            if ip in self.USED_IP:
                continue

            allowed_ip = ip
            break

        # 计算得到真实IP地址
        gateway_arr = gateway.split('.')
        gateway_arr[3] = str(allowed_ip)
        real_ip = '.'.join(gateway_arr)

        # 修改网络配置文件
        sed(self.INTERFACE_FILE, 'address .*', 'address {0}'.format(
            real_ip
        ), use_sudo=True)
        sed(self.INTERFACE_FILE, 'netmask .*', 'netmask {0}'.format(
            netmask
        ), use_sudo=True)
        sed(self.INTERFACE_FILE, 'gateway .*', 'gateway {0}'.format(
            gateway
        ), use_sudo=True)
        sed(self.INTERFACE_FILE, 'dns-nameservers .*',
            'dns-nameservers {0}'.format(dns_nameservers), use_sudo=True)

        # 记录安装历史
        self.record_history(allowed_ip)

        # 重启服务器
        try:
            sudo('reboot -h now')
        except:
            print(red('重启服务器。'))

    def record_history(self, ip):
        """
        记录安装历史
        :return:
        """
        json_data = []
        with open(self.INSTALL_INFO, 'r') as fh:
            data = fh.read()
            if data != '':
                json_data = json.loads(data)

        with open(self.INSTALL_INFO, 'w') as fh:
            json_data.append({
                'ip_address': ip,
                'machine_name': self.mc_name
            })
            fh.write(json.dumps(json_data))
