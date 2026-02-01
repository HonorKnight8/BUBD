import argparse
# 用于读取脚本执行参数

import os
import time
import sys

import threading
# 用于多线程播放铃声

# TOML 解析：Python 3.11+ 内置 tomllib，用于读取配置文件
try:
    import tomllib
    # print(tomllib)
except Exception:
    print("tomllib module not found. run 'pip install tomllib' to install it.")
    exit()

# 颜色支持
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
    HAS_COLOR = True
except Exception:
    HAS_COLOR = False
    class Fore:
        GREEN = ''
        YELLOW = ''
        CYAN = ''
        MAGENTA = ''
    class Style:
        RESET_ALL = ''

# 播放铃声功能
from paly_sound import play_alert

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

work_minutes = choose_param(args.work, cfg, 'work_minutes', 50)
rest_minutes = choose_param(args.rest, cfg, 'rest_minutes', 10)
cycles = choose_param(args.cycles, cfg, 'cycles', 0)
print(f"{work_minutes} ， {rest_minutes} ， {cycles}")

# ↑↑↑↑↑ 参数部份完成 ↑↑↑↑↑

# 倒计时显示函数
def show_countdown(title: str, minutes: int, color: str = None):
    total_seconds = int(minutes * 60)
    start_time = time.time()
    try:
        while True:
            elapsed = int(time.time() - start_time)
            remaining = total_seconds - elapsed
            if remaining <= 0:
                break
            m = remaining // 60
            s = remaining % 60
            text = f"[{title}] 剩余时间: {m:02d}:{s:02d}"
            if HAS_COLOR and color:
                col = getattr(Fore, color.upper(), '')
                sys.stdout.write('\r' + col + text + Style.RESET_ALL)
            else:
                sys.stdout.write('\r' + text)
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        raise
    print()


def main():
    # parser = argparse.ArgumentParser(description='番茄工作计时器（50 分钟工作，10 分钟休息）')
    # # 不在解析阶段设置默认值，以便优先使用命令行，其次是配置文件，最后是内置默认
    # parser.add_argument('--work', '--workminutes', dest='work', type=int, default=None, help='工作时长（分钟），默认 50')
    # parser.add_argument('--rest', '--restminutes', dest='rest', type=int, default=None, help='休息时长（分钟），默认 10')
    # parser.add_argument('--cycles', dest='cycles', type=int, default=None, help='循环次数（0 表示无限循环）')
    # args = parser.parse_args()

    # cfg = load_config('config.toml')

    # work_minutes = choose_param(args.work, cfg, 'work', 50)
    # rest_minutes = choose_param(args.rest, cfg, 'rest', 10)
    # cycles = choose_param(args.cycles, cfg, 'cycles', 0)

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
    if cycles == 0:
        print("  番茄工作计时器 (无限循环)    ")
    else:
        print(f"  番茄工作计时器 (共{cycles}个循环)    ")
    print("================================")
    print(f"工作时间: {work_minutes} 分钟")
    print(f"休息时间: {rest_minutes} 分钟")
    print("按 Ctrl+C 停止\n")

    try:
        while True:
            if cycles > 0 and cycle_count > cycles:
                print("================================")
                print("所有循环已完成！")
                print("================================")
                break


            work_bell_thread = threading.Thread(target=play_alert, args=(work_bell, work_bell_volume, bell_duration))
            work_bell_thread.start()

            print(f"第 {cycle_count} 轮")
            print(Fore.GREEN + "🔴 工作开始！" + Style.RESET_ALL if HAS_COLOR else "🔴 工作开始！")
            show_countdown("工作中", work_minutes, 'GREEN')
            print(Fore.CYAN + "🔔 工作时间结束！" + Style.RESET_ALL if HAS_COLOR else "🔔 工作时间结束！")
            rest_bell_thread = threading.Thread(target=play_alert, args=(rest_bell, rest_bell_volume, bell_duration))
            rest_bell_thread.start()
            # time.sleep(2)

            print(Fore.YELLOW + "🟢 休息时间！" + Style.RESET_ALL if HAS_COLOR else "🟢 休息时间！")
            show_countdown("休息中", rest_minutes, 'YELLOW')
            print(Fore.CYAN + "🔔 休息时间结束！" + Style.RESET_ALL if HAS_COLOR else "🔔 休息时间结束！")
            work_bell_thread = threading.Thread(target=play_alert, args=(work_bell, work_bell_volume, bell_duration))
            work_bell_thread.start()

            cycle_count += 1
            print()

    except KeyboardInterrupt:
        print('\n已手动停止。')


if __name__ == '__main__':
    main()




