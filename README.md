# BUBD

Bell Up, Bell Down.  
铃起铃落。

——Work and Breaks. Find your rhythm between focus and break.  
——工作与小憩，找到你专注与休息的节奏。

## 依赖

python, pygame, colorama, keyboard

## 安装

1、安装 Python  
3.11+，3.11以上原生支持解析toml配置文件，减少第三方依赖  

2、安装 pygame, colorama, keyboard  
`pip install pygame`  
*建议安装，如果不安装本依赖，则不支持自定义铃声，以蜂鸣声 “哔哔~” 代替*  
`pip install colorama`  
*非必须，只是界面好看一点；不装就是无色的界面*  
`pip install keyboard`  
*快捷键需要*  

3、下载/拷贝本项目至本地  

## 使用

在本目录中执行：  
  `python bubd.py`  
  ——以缺省参数循环执行  
  或 `python bubd.py --work 50 --breath 10 --cycles 4`  
  ——工作时间：50分钟；小憩时间：10分钟；循环4次。  

## 配置文件

- 配置文件为：config.toml
- 除了上述三个运行参数，还可以自定义铃声：
  - 铃声文件放置于 sounds 子目录中
  - 支持设置铃声音量、播放时长，详见配置文件注释
- 参数优先级：
  - 运行参数第一，配置文件第二，最后是程序中的默认值  

## 快捷键说明

| 快捷键 | 助记 | 说明 |
| :---- | :----: | :---- |
| Ctrl + 数字 | | |
| &nbsp;&nbsp;&nbsp;&nbsp;**Ctrl+1** | | 延长 1 分钟 |
| &nbsp;&nbsp;&nbsp;&nbsp;**Ctrl+2..9** | | 依此类推 |
| &nbsp;&nbsp;&nbsp;&nbsp;**Ctrl+0** | | 延长 10 分钟 |
| **Ctrl+N** | Next | 提前结束当前循环单元，进入下一个循环单元 |
| **Ctrl+W** | Work | 切换到“工作”循环单元 |
| **Ctrl+B** | Break | 切换到“小憩”循环单元 |
| **Ctrl+R** | Rest | 切换到“休息/待机”循环单元 |
| **Ctrl+Q** | Quit | 退出程序 |
| **Ctrl+C** | | 退出程序（通用，强制结束） |

## 其他

sounds目录中现有的两个mp3铃声文件来源于：pixabay.com，里面的授权文件也保留了。  
用户可以按自己的喜好更换铃声文件。支持 mp3、wav、ogg  

## 后续开发打算

- 记录功能
  - 结束时列出各个“循环单元/时间块”的类型、启动结束时间、提前结束/延长操作
