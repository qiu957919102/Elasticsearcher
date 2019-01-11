<style>
.important {
    color: red;
    font-weight: 900;
}
</style>

# 集群配置
## 1. 机器配置
### 主机硬件
<img src="images/机器配置-System.png" style="zoom:40%">
<img src="images/机器配置-Display.png" style="zoom:40%">

### 软件
- VMware-workstation-full-12.1.1-3770994.exe
- XShell5
- <div class='important'>jdk1.8.0_191</div>
- elasticsearch-5.6.13.tar.gz
- kibana-5.6.13-linux-x86_64.tar.gz
- elasticsearch-analysis-ik-5.6.13.zip

<div class='important'>ES版本最后确定使用5.x.x 因为6版本在与数据库同步时有问题</div>

### 分布式
3台虚拟机
系统镜像: CentOS-7.3-x86_64-DVD-1611.iso
<div class='important'>还是用些强悍的机器做8...</div>

## 2. 基本安装
1. 安装jdk
```shell
配置环境变量
vi /etc/profile.d/java.sh

JAVA_HOME=/usr/local/java/jdk1.8.1_191
CLASSPATH=$JAVA_HOME/lib/:$CLASSPATH
PATH=$JAVA_HOME/bin/:$PATH
export JAVA_HOME CLASSPATH PATH
```
2. 关闭防火墙
```
systemctl stop firewalld.service
systemctl disable firewalld.service
```
3. 配置Elasticsearch
   
由于Elasticsearch的主节点是通过集群"选举"出来的，所以每个节点均有可能为主节点
```
vim elasticsearch.yml

# 集群名
cluster.name: gdy-elasticsearcher
# 节点名
node.name: es-node-1
# 是否为主节点
node.master: true
# 是否为数据节点
node.data: true
# 数据和日志路径
path.data: /data/elasticsearch/data
path.logs: /data/elasticsearch/logs
# 集群地址设置
discovery.zen.ping.unicast.hosts: ["192.168.137.10", "192.168.137.11", "192.168.137.12"]
# 节点数目配置# 防止集群发生“脑裂”，即一个集群分裂成多个，配置集群最少主节点数目 (可成为主节点的主机数目 / 2) + 1
discovery.zen.minimum_master_nodes: 2
# 当最少几个节点回复之后，集群就正常工作
gateway.recover_after_nodes: 2
# 开启内存交换，提高ES性能
bootstrap.memory_lock: true
```
当然这里不要忘记了创建好/data目录，并配置好权限
```
mkdir -p /data/elasticsearch/data
mkdir -p /data/elasticsearch/logs
chown -R elastic:elastic /data
```

启动Elasticsearch
```
./bin/elasticsearch -d
-d 可以后台启动

然后通过访问`http://192.168.137.10:9200/_cluster/state`查看集群信息
```

2. 安装Kibana
   
**这里建议给需要安装Kibana的虚拟机分配多点内存**

安装步骤类似Elasticsearch, 启动Kibana后打开网址

`http://192.168.137.10:5601` 点击 `Monitoring`查看集群信息

3. 安装插件
   
3.1 ik中文分词
```
1. 下载安装包
https://github.com/medcl/elasticsearch-analysis-ik
解压到elasticsearch的plugins/ik目录下

2. bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v5.6.13/elasticsearch-analysis-ik-5.6.13.zip
``` 

## 3. 添加节点
1. 克隆虚拟机(完全克隆)
- <div class='important'>更改新虚拟机的MAC地址</div>
- <div class='important'>更改新虚拟机的IP地址</div>

2. 将虚拟机的IP地址改为静态IP
```shell
vim /etc/sysconfig/network-scripts/ifcfg-ens33

# 参照下面内容进行修改
TYPE="Ethernet"
BOOTPROTO="static"
IPADDR=192.168.137.11
NETMASK=255.255.255.0
GATEWAY=192.168.137.1
DNS1=192.168.137.1
DEFROUTE="yes"
PEERDNS="yes"
PEERROUTES="yes"
NAME="ens33"
UUID="59c7d520-8a21-4c3d-a89f-7415c2feac41"
DEVICE="ens33"
ONBOOT="yes"

# 修改完成后重启network服务
service network restart
```

# 常见问题及解决方案
## SSH登陆缓慢
```
ssh的服务端在连接时会自动检测dns环境是否一致导致的，修改为不检测即可，操作如下：

修改文件：/etc/ssh/sshd_config

UseDNS yes  --->默认为注释行

UseDNS no  --->把注释打开，改为no

然后重启ssh服务即可
service sshd restart
```

## memory locking requested for elasticsearch process but memory is not locked

```
vim /etc/security/limits.conf

添加如下内容
* soft nofile 65536
* hard nofile 65536
* soft nproc 32000
* hard nproc 32000
* hard memlock unlimited
* soft memlock unlimited

vim /etc/systemd/system.conf

添加如下内容
DefaultLimitNOFILE=65536
DefaultLimitNPROC=32000
DefaultLimitMEMLOCK=infinity
```

## Java.lang.UnsupportedOperationException: seccomp unavailable: requires kernel 3.5+ ...

```
Linux版本过低
1、重新安装新版本的Linux系统
2、警告不影响使用，可以忽略
```

## max file descriptors [4096] for elasticsearch process likely too low, increase to at least [65536]

```
vim /etc/security/limits.conf

* soft nofile 65536
* hard nofile 65536
* soft nproc 32000
* hard nproc 32000
```
这个建议跟上面的**memory locking requested for elasticsearch process but memory is not locked**一样修改

## max number of threads [1024] for user [es] likely too low, increase to at least [2048]

```
vim /etc/security/limits.d/90-nproc.conf

* soft nproc 1024 修改为 * soft nproc 2048
```

## max virtual memory areas vm.max_map_count [65530] likely too low, increase to at least [262144]

```
添加如下内容
vm.max_map_count=655360

执行命令
sysctl -p
```

## org.elasticsearch.transport.RemoteTransportException: Failed to deserialize exception response from stream

```
ES节点之间的JDK版本不一致
```

## ElasticSearch启动找不到主机或路由
```
检查Elasticsearch.yml中的
discovery.zen.ping.unicast.hosts
```

## 启动ES直接返回Killed
```
虚拟机内存不足
ES(6.5.4)这个版本占用的内存大概在1.2-1.5G左右, 因为后面改成了5.6.13版本，未测试，暂时不修改
每台机器配置2G内存其实是足够的，还是建议配高点
如果2G不运行其他进程，出现这个问题，重启试试
```

## Kibana server is not ready yet
```
说了没准备好，等会就好啦:)
```
