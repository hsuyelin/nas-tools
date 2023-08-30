# NAS媒体库管理工具

[![GitHub stars](https://img.shields.io/github/stars/hsuyelin/nas-tools?style=plastic)](https://github.com/hsuyelin/nas-tools/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/hsuyelin/nas-tools?style=plastic)](https://github.com/hsuyelin/nas-tools/network/members)
[![GitHub issues](https://img.shields.io/github/issues/hsuyelin/nas-tools?style=plastic)](https://github.com/hsuyelin/nas-tools/issues)
[![GitHub license](https://img.shields.io/github/license/hsuyelin/nas-tools?style=plastic)](https://github.com/hsuyelin/nas-tools/blob/master/LICENSE.md)
[![Docker pulls](https://img.shields.io/docker/pulls/hsuyelin/nas-tools?style=plastic)](https://hub.docker.com/r/hsuyelin/nas-tools)
[![Platform](https://img.shields.io/badge/platform-amd64/arm64-pink?style=plastic)](https://hub.docker.com/r/hsuyelin/nas-tools)

## 维护声明

1）本维护项目为[nas-tools](https://github.com/NAStool/nas-tools)维护项目非官方项目；  
2）本维护项目旨在帮助喜欢PT的小伙伴更加易用，本人未创建任何交流群或频道，任何自称是该项目维护者的人皆为假冒；  
3）本维护项目提交的修复和需求皆为开源，任何维护该项目的小伙伴皆可参考，但尽量注明出处；  
4）使用本维护项目请尽量保持低调，尽可能不在交流群或者频道传播，自己使用即可；  
5）欢迎任何形式的pr，请尽量将pr内容描述清楚；  

## 官方WiKi

https://wiki.nastool.org

## 开发路线及官方原版新增内容
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
