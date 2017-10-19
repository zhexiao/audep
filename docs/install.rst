开始使用
^^^^^^^^

安装
-----

Audep是基于Python3开发的，在安装之前，需要安装python3-pip。

.. code-block:: bash

   > sudo apt-get install python3 python3-pip
   > sudo pip3 install audep

使用
-----
.. code-block:: bash

   > audep -c data/demo.ini

demo.ini
---------
.. code-block:: bash

   [ftp]
   user=ftpuser
   passwd=ftppassword

   [server]
   host=192.168.33.39
   user=ubuntu
   passwd=18fc2f8e53c021a965cd9628

   [mc_server]
   host=192.168.71.180
   user=mcuser
   passwd=mcpasswd

   [vsphere]
   host=192.168.1.11
   user=administrator@vsphere.local
   passwd=vspherepasword
   data-storage=bigdata_datastore
   data-center=Datacenter
   cluster=cluster1

   [network]
   address_range=180 ~ 190
   address_exclude=180,181
   netmask=255.255.255.255
   gateway=192.168.1.1
   dns-nameservers=8.8.8.8

   [dependency]
   ovftool=ftp://122.122.122.122/super/VMware-ovftool-4.2.0.bundle

   [mc_bigdata]
   ;elasticsearch=ftp://122.122.122.122/super/bigdata/Elasticsearch.ovf, autoes7
   ;hdfs_1=ftp://122.122.122.122/super/bigdata/HDFS_1.ovf
   ;hdfs_2=ftp://122.122.122.122/super/bigdata/HDFS_2.ovf
   ;kafka=ftp://122.122.122.122/super/bigdata/Kafka.ovf,audepkafka2
   ;lrs=ftp://122.122.122.122/super/bigdata/LRS.ovf
   spark_master=ftp://122.122.122.122/super/bigdata/Spark_master.ovf,autospm
   spark_slave1=ftp://122.122.122.122/super/bigdata/Spark_slave1.ovf,autosps1