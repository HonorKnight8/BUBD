# import time
# import sys
import os

# 用于读取脚本执行参数
import argparse

# 加载 循环单元 基类
import CycleUnit

# import asyncio

# TOML 解析：Python 3.11+ 内置 tomllib，用于读取配置文件
try:
    import tomllib
    # print(tomllib)
except Exception:
    print("tomllib module not found. run 'pip install tomllib' to install it.")
    exit()

# # 键盘监听，快捷键支持（未使用）
# try:
#     import keyboard
#     # print(keyboard)
# except Exception:
#     keyboard = None
#     print("keyboard module not found. some features may be disabled.")
#     exit()

# ↑↑↑↑↑ 加载部份完成 ↑↑↑↑↑

# 读取脚本执行参数
parser = argparse.ArgumentParser(
    description=(
        "BUBD: Bell Up, Bell Down. 铃起铃落。 \n"
        "——Work and Breaks. Find your rhythm between focus and rest. \n"
        "——工作与小憩，找到你专注与休息的节奏。 \n"
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument(
    '--type', 
    '--starttype', 
    dest='CycleUnit-Type', 
    type=str, 
    help='以这个循环类型开始：work, rest, break, 默认 work')
parser.add_argument(
    '--work', 
    '--workminutes', 
    dest='work', 
    type=int, 
    help='工作时长（分钟），默认 50')
parser.add_argument(
    '--rest', 
    '--restminutes', 
    dest='rest', 
    type=int, 
    help='休息时长（分钟），默认 10')
parser.add_argument(
    '--cycles', 
    dest='cycles', 
    type=int, 
    help='循环次数（0 表示无限循环）')
args = parser.parse_args()
# print(args)

# 读取配置文件
def load_config(path='config.toml'):
    if not os.path.exists(path):
        print("config.toml not found.")
        return {}
    # print(tomllib)
    if tomllib is None:
        print("tomllib module not found. run 'pip install tomllib' to install it.")
        return {}
    # print(tomllib)
    try:
        with open(path, 'rb') as f:
            return tomllib.load(f)
    except Exception:
        print("Failed to load config.toml.")
        return {}

cfg = load_config('config.toml')
# print(cfg)
# exit()

# 从配置文件和命令行参数中选择最终参数的函数
# 参数优先级：命令行 > 配置文件 > 默认值
def choose_param(cmd_value, cfg, key, default):
    if cmd_value is not None:
        return cmd_value
    if cfg and key in cfg:
        try:
            return int(cfg[key])
        except Exception:
            return default
    return default

cfg['work_minutes'] = choose_param(args.work, cfg, 'work_minutes', 50)
cfg['rest_minutes'] = choose_param(args.rest, cfg, 'rest_minutes', 10)
cfg['cycles'] = choose_param(args.cycles, cfg, 'cycles', 0)

# 释放内存
del args

# print(cfg)
# exit()

# ↑↑↑↑↑ 参数部份完成 ↑↑↑↑↑

def main():
    # 从配置中读取铃声设置（命令行优先，没有时从配置文件中读取）
    work_bell = None
    rest_bell = None
    work_bell_volume = 75
    rest_bell_volume = 75
    bell_duration = 3
    if cfg:
        # 支持多个命名约定
        work_bell = cfg.get('work_bell')
        rest_bell = cfg.get('rest_bell')
        work_bell_volume = float(cfg.get('work_bell_volume'))
        rest_bell_volume = float(cfg.get('rest_bell_volume'))
        bell_duration = min(600,max(1, int(cfg.get('bell_duration'))))

    cycle_count = 1

    print("================================")
    if cfg.get('cycles') == 0:
        print("  番茄工作计时器 (无限循环)    ")
    else:
        print(f"  番茄工作计时器 (共{cfg.get('cycles')}个循环)    ")
    print("================================")
    # print(f"工作时间: {work_minutes} 分钟")
    # print(f"休息时间: {rest_minutes} 分钟")
    print("按 Ctrl+C 停止\n")

    try:
        while True:
            if cfg.get('cycles') > 0 and cycle_count > cfg.get('cycles')*2:
                print("================================")
                print("所有循环已完成！")
                print("================================")
                break

            if cfg.get('starttype', 'work') == 'work':
                work_block = CycleUnit.WorkBlock(cfg)
                assert work_block.duration == cfg['work_minutes'] * 60
                # asyncio.run(work_block.run())
                work_block.run()
                cfg['starttype'] = 'rest'
            else:
                rest_block = CycleUnit.RestBlock(cfg)
                assert rest_block.duration == cfg['rest_minutes'] * 60
                # asyncio.run(rest_block.run())
                rest_block.run()
                cfg['starttype'] = 'work'

            cycle_count += 1
            print()
            # work_block = CycleUnit.WorkBlock(cfg)
            # asyncio.run(work_block.run())
            
    except KeyboardInterrupt:
        print('\n已手动停止。')


if __name__ == '__main__':
    main()
