配置文件
^^^^^^^^

配置文件中模块的详细解释和使用用途。

ftp
----
ftp模块用来指定FTP服务器，我们把需要安装的虚拟机都挂载在FTP上，所以audep可以通过ftp
服务把虚拟机下载下来。

.. code-block:: bash

    [ftp]
    user=ftpuser
    passwd=ftppassword

.. note::

    - ``user``：FTP用户名
    - ``passwd``：FTP密码


server
-------
server模块指代一个服务器，这个服务器有如下作用：

1. 从FTP服务器下载虚拟机
2. 执行ovftool命令，与超融合集群服务器相互通信，安装虚拟机

.. code-block:: bash

    [server]
    host=192.168.33.39
    user=ubuntu
    passwd=18fc2f8e53c021a965cd9628

.. note::

    - ``host``：服务器主机地址
    - ``user``：服务器登录用户名
    - ``passwd``：服务器登录密码

mc_server
----------
mc_server(machine server)模块是默认从FTP下载下来的虚拟机的主机地址，用户名与密码。我们
定义这个模块是为了方便通过ssh进入到该虚拟机中自动化修改配置。

.. code-block:: bash

    [mc_server]
    host=192.168.71.180
    user=hdgs
    passwd=hdgs2017

.. note::

    - ``host``：服务器主机地址
    - ``user``：服务器登录用户名
    - ``passwd``：服务器登录密码

vsphere
--------
vsphere模块是超融合服务器安装完成后的一些认证信息和存储信息。我们的虚拟机都会通过ovftool
命令自动部署到vsphere中。

.. code-block:: bash

    [vsphere]
    host=192.168.1.11
    user=administrator@vsphere.local
    passwd=vspherepasword
    data-storage=bigdata_datastore
    data-center=Datacenter
    cluster=cluster1

.. note::

    - ``host``：vsphere主机地址
    - ``user``：vsphere登录用户名
    - ``passwd``：vsphere登录密码
    - ``data-storage``：虚拟机存储的地方
    - ``data-center``：vsphere数据中心，一般都是Datacenter
    - ``cluster``：虚拟机所在的集群名称

network
--------
网络模块代表分配给这个超融合集群里面服务器的IP地址段。

.. code-block:: bash

    [network]
    address_range=180 ~ 190
    address_exclude=180,181
    netmask=255.255.255.255
    gateway=192.168.1.1
    dns-nameservers=8.8.8.8

.. note::

    - ``address_range``：IP地址段区间，使用 "~" 符号代表区间
    - ``address_exclude``：去掉IP地址段区间中某些已经被使用过的地址，使用 "," 符号分隔
    - ``netmask``：网络的子网掩码
    - ``gateway``：网络的网关
    - ``dns-nameservers``：网络的DNS服务器

dependency
-----------
这个模块代表audep命令完成超融合集群安装所需要的一些依赖。

.. code-block:: bash

    [dependency]
    ovftool=ftp://122.204.161.220/super/VMware-ovftool-4.2.0.bundle

.. note::

    - ``ovftool``：需要检查是否已经安装了ovftool

mc_bigdata
-----------
mc_bigdata模块代表超融合集群中所有的与大数据相关虚拟机信息。

.. code-block:: bash

    [mc_bigdata]
    elasticsearch=ftp://122.204.161.220/super/bigdata/Elasticsearch.ovf, autoes7
    hdfs_1=ftp://122.204.161.220/super/bigdata/HDFS_1.ovf
    hdfs_2=ftp://122.204.161.220/super/bigdata/HDFS_2.ovf
    kafka=ftp://122.204.161.220/super/bigdata/Kafka.ovf,audepkafka2
    lrs=ftp://122.204.161.220/super/bigdata/LRS.ovf
    spark_master=ftp://122.204.161.220/super/bigdata/Spark_master.ovf
    spark_slave=ftp://122.204.161.220/super/bigdata/Spark_slave.ovf

.. note::

    下面我们以"kafka=ftp://122.204.161.220/super/bigdata/Kafka.ovf,audepkafka2"来解释：

    - ``kafka``：名称
    - ``ftp://122.204.161.220/super/bigdata/Kafka.ovf``：虚拟机下载地址
    - ``audepkafka2``：虚拟机名称（使用","）与下载地址分隔。如果没有提供则默认使用文件名作为虚拟机名称
