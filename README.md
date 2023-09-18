# NAS媒体库管理工具

[![GitHub stars](https://img.shields.io/github/stars/hsuyelin/nas-tools?style=plastic)](https://github.com/hsuyelin/nas-tools/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/hsuyelin/nas-tools?style=plastic)](https://github.com/hsuyelin/nas-tools/network/members)
[![GitHub issues](https://img.shields.io/github/issues/hsuyelin/nas-tools?style=plastic)](https://github.com/hsuyelin/nas-tools/issues)
[![GitHub license](https://img.shields.io/github/license/hsuyelin/nas-tools?style=plastic)](https://github.com/hsuyelin/nas-tools/blob/master/LICENSE.md)
[![Docker pulls](https://img.shields.io/docker/pulls/hsuyelin/nas-tools?style=plastic)](https://hub.docker.com/r/hsuyelin/nas-tools)
[![Platform](https://img.shields.io/badge/platform-amd64/arm64-pink?style=plastic)](https://hub.docker.com/r/hsuyelin/nas-tools)

## 维护声明

1）本维护项目为[nas-tools](https://github.com/NAStool/nas-tools)维护项目非官方项目；  
2）本维护项目旨在帮助喜欢PT的小伙伴更加易用，本人未创建任何交流群或频道；  
3）本维护项目提交的修复和需求皆为开源，任何维护该项目的小伙伴皆可参考，但尽量注明出处；  
4）使用本维护项目请尽量保持低调，尽可能不在交流群或者频道传播，自己使用即可；  
5）欢迎任何形式的pr，请尽量将pr内容描述清楚；  

## 开发路线及官方原版新增内容

基于官方 3.2.3 版本

[开发路线](https://github.com/hsuyelin/nas-tools/discussions/91)

- [x] 支持Aria2/115/PikPak下载器
- [x] 支持chromedriver114版本以上的谷歌浏览器
- [x] 支持识别历史记录一键清理
- [x] 支持通过插件安装Jackett和Prowlarr扩展内置索引
- [x] 支持TMDB搜索18+内容
- [x] 支持通过开关控制刮削时是否刮削视频实际媒体信息
- [x] 支持管理我的媒体库显示模块
- [x] 修复官方版豆瓣图片无法显示
- [x] 修复官方原版豆瓣同步方式近期动态与全量同步失效
- [x] 修复官方原版高清空间签到cookies错误
- [x] 持续更新索引站点
- [x] 更多功能请查阅 [版本发布](https://github.com/hsuyelin/nas-tools/releases)  更新日志 

## 安装
### 1、Docker
```
docker pull hsuyelin/nas-tools:latest
```
教程见 [这里](https://raw.githubusercontent.com/hsuyelin/nas-tools/master/docker/readme.md) 。

如无法连接Github，注意不要开启自动更新开关(NASTOOL_AUTO_UPDATE=false)，将NASTOOL_CN_UPDATE设置为true可使用国内源加速安装依赖。

### 2、本地运行
仅支持python3.10版本，需要预安装cython（python3 -m pip install Cython），如发现缺少依赖包需额外安装：
```
git clone -b master https://github.com/hsuyelin/nas-tools --recurse-submodule 
python3 -m pip install --force-reinstall -r requirements.txt
export NASTOOL_CONFIG="/xxx/config/config.yaml"
nohup python3 run.py & 
```

### 3、可执行文件运行
仅支持python3.10版本，先从tag下载对应的可执行文件，打开终端，例如下载的是macos版本，文件名为：nastool_macos_v3.2.2：
```bash
mv nastool_macos_v3.2.2 nastools
chmod +x nastools
// macos 12以上需要去隐私-安全性，允许任意开发者
./nastools（如果需要不在终端输出执行：./nastool &> /dev/null）
```

## 官方免责

1）本软件仅供学习交流使用，对用户的行为及内容毫不知情，使用本软件产生的任何责任需由使用者本人承担。  
2）本软件代码开源，基于开源代码进行修改，人为去除相关限制导致软件被分发、传播并造成责任事件的，需由代码修改发布者承担全部责任，不建议对用户认证机制进行规避或修改并公开发布。  
3）本项目没有在任何地方发布捐赠信息页面，也不会接受捐赠或收费，请仔细辨别避免误导。


## 常见问题

### 1. 启动inotify报错/无法自动目录同步

> 问题描述
> 无法启动，日志报inotify instance limit reached、inotify watch limit reached等与inotify相关错误
> 目录同步无法自动同步或只有部份目录正常，但在服务中手动启动可以正常同步

解决办法：
* 宿主机上（不是docker容器里），执行以下命令：
 ```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
echo fs.inotify.max_user_instances=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```
* 插件-定时目录同步

### 2. 启动报错数据库no such column
> 问题描述
> 启动报错数据库no such column

解决办法：
* [Sqlite浏览器](https://github.com/sqlitebrowser/sqlitebrowser)打开config文件夹下user.db
* 删除alembic_version表后重启

### 3. Nginx-Proxy-Manager无法申请/更新Let's Encrypt证书
> 问题描述
> Nginx-Proxy-Manager无法申请/更新Let's Encrypt证书

解决办法：
* 无法通过DNSpod申请, 进入容器，执行命令
```bash
pip install certbot-dns-dnspod
```

* 无法更新/自动更新
```bash
进入容器，执行命令 pip install zope
```

* pip使用代理
```
pip install xxx --proxy=http://ip:port
```

### 4. 消息通知内容无法跳转
> 问题描述
> 消息通知内容无法跳转

解决办法：
* 设置-基础设置-系统-外网访问地址

### 5. 电影/电视剧订阅一直队列中
> 问题描述
> 电影/电视剧订阅添加后，一直在队列中
> 需手动刷新订阅开始搜索或订阅

解决办法：
* 订阅如启用有订阅站点, 请在设置-基础设置-服务-订阅RSS周期设置启用
* 订阅如启用有搜索站点, 请在设置-基础设置-服务-订阅搜索周期设置启用
* 添加后点击订阅，选择刷新

### 6. 目录同步文件重复转移
> 问题描述
> 设置-基础设置-媒体-重命名格式中包含{releaseGroup}
> 文件转移方式为目录同步
> 转移后，出现重复的转移文件（制作组等后缀不同）

解决办法：
* 目录同步设置时，目的目录不要在源目录下

### 7. 识别转移错误码-1
> 问题描述
> 识别转移错误码-1

解决办法：
* 硬链接跨盘，转移前后目录根目录需相同
* 群晖中，不同的共享文件夹会被系统认为是跨盘

### 8. 电视剧订阅在完结前自动删除
> 问题描述
> 电视剧订阅在完结前自动删除

解决办法：
*  TMDB词条未更新集数/下载资源无法识别集数
*  订阅中设置总集数

更多功能使用请查看 [nas-tools wiki](https://t.me/NAStool_wiki)
