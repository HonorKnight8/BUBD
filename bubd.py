# import time
# import sys
# import os

# print(sys.stdout.encoding)
# print(sys.stderr.encoding)
# sys.stdout.reconfigure(encoding='utf-8')
# sys.stderr.reconfigure(encoding='utf-8')
# print(sys.stdout.encoding)
# print(sys.stderr.encoding)
# exit()

# 用于读取脚本执行参数
import argparse

# 加载 配置管理类
import config

# 加载 热键管理类
from HotKeys import Hotkeys

# 加载 循环单元 基类
import CycleUnit

# ↑↑↑↑↑ 加载部份完成 ↑↑↑↑↑

# 读取脚本执行参数
parser = argparse.ArgumentParser(
    description=(
        "BUBD: Bell Up, Bell Down. 铃起铃落。 \n"
        "——Work and Breaks. Find your rhythm between focus and break. \n"
        "——工作与小憩，找到你专注与休息的节奏。 \n"
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument(
    '--type', 
    '--starttype', 
    dest='type', 
    type=str, 
    help='以这个循环类型开始：work, breath, rest, 默认 work')
parser.add_argument(
    '--work', 
    '--workminutes', 
    dest='work', 
    type=int, 
    help='工作时长（分钟），默认 50')
parser.add_argument(
    '--breath', 
    '--breathminutes', 
    dest='breath', 
    type=int, 
    help='休息时长（分钟），默认 10')
parser.add_argument(
    '--cycles', 
    dest='cycles', 
    type=int, 
    help='循环次数（0 表示无限循环）')
args = parser.parse_args()
# print(args)

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

# print(config.getall())

config.set('work_minutes', choose_param(args.work, config.getall(), 'work_minutes', 50))
config.set('breath_minutes', choose_param(args.breath, config.getall(), 'breath_minutes', 10))
config.set('cycles', choose_param(args.cycles, config.getall(), 'cycles', 0))  

# # 调试用：缩短时间
# config.set('work_minutes', config.get('work_minutes')/10)
# config.set('breath_minutes', config.get('breath_minutes')/5)
# config.set('bell_duration', config.get('bell_duration')/5)

# print(config.get('cycle_unit_type'))
config.set('cycle_unit_type', args.type if args.type else config.get('cycle_unit_type', 'work'))
# print(config.get('cycle_unit_type'))

# print(config.getall())
# exit()

# 释放内存
del args

# ↑↑↑↑↑ 完成读取参数和配置 ↑↑↑↑↑

def main():
    # 从配置中读取铃声设置（命令行优先，没有时从配置文件中读取）
    # work_bell = None
    # breath_bell = None
    # work_bell_volume = 75
    # breath_bell_volume = 75
    # bell_duration = 3
    # if config.getall():
    #     # 支持多个命名约定
    #     work_bell = config.get('work_bell')
    #     breath_bell = config.get('breath_bell')
    #     work_bell_volume = float(config.get('work_bell_volume'))
    #     breath_bell_volume = float(config.get('breath_bell_volume'))
    #     bell_duration = min(600,max(1, int(config.get('bell_duration'))))

    cycle_count = 1

    print("================================")
    if config.get('cycles') == 0:
        print("  铃起铃落 - 作息计时 (无限循环)    ")
    else:
        print(f"  铃起铃落 - 作息计时 (共{config.get('cycles')}个循环)    ")
    print("================================")
    # print(f"工作时间: {work_minutes} 分钟")
    # print(f"休息时间: {breath_minutes} 分钟")
    # print("按 Ctrl+C 停止\n")

    # 尝试导入 Hotkeys 管理类（容错加载）
    # try:
    #     from hotkeys import Hotkeys
    # except Exception:
    #     import importlib.util
    #     spec = importlib.util.spec_from_file_location('hotkeys', os.path.join(os.path.dirname(__file__), 'hotkeys.py'))
    #     hot_mod = importlib.util.module_from_spec(spec)
    #     spec.loader.exec_module(hot_mod)
    #     Hotkeys = hot_mod.Hotkeys

    # 运行状态与当前正在运行的循环单元引用
    run_state = {
        'running': True,            # while循环标志
        'current': None,            # 当前活动的循环单元的引用
        'dont_change_type': False   # 跳过修改类型的步骤
        }
    
    # 回调函数：由 Hotkeys 调用
    # 延长当前循环单元时间
    def cb_extend(minutes):
        current_running_CycleUnit = run_state.get('current')
        # print(run_state)
        if current_running_CycleUnit is not None:
            print(f"快捷键：延长 {minutes} 分钟")
            current_running_CycleUnit.extend(int(minutes * 60))
        else:
            print('没有活动的循环单元可延长')

    # 提前结束当前循环单元，进入下一个
    def cb_next():
        current_running_CycleUnit = run_state.get('current')
        # print(run_state)
        if current_running_CycleUnit is not None:
            print('\n快捷键Ctrl+N：提前结束当前循环，进入下一循环单元')
            next_unit=current_running_CycleUnit.next()
            # current_running_CycleUnit._stopped = True
            run_state['running'] = True
            run_state['current'] = next_unit
            current_running_CycleUnit.end()
            # next_unit.run() # 由主循环从 run_state 中调用运行，不需要在次运行
            del current_running_CycleUnit
            # run_state['running'] = True
        else:
            print('没有活动的循环单元可跳过')

    # 结束当前循环单元，进入指定循环单元类型
    def cb_set_mode(mode):
        # mode: 'work', 'short_breath', 'rest' -> map 到 cfg.cycle_unit_type
        # HotKeys 可能传入 'work', 'breath', 'rest'
        
        current_running_CycleUnit = run_state.get('current')
        # print(f"cb_set_mode called with mode={mode}, current config={config.get('cycle_unit_type')}, current_running={bool(current_running_CycleUnit)}, dont_change_type={run_state.get('dont_change_type')}")
        # 规范化传入的 mode，确保与主循环使用的类型一致
        mode_map = {
            'short_breath': 'breath',
            'breath': 'breath',
            'work': 'work',
            'rest': 'rest'
        }
        normalized = mode_map.get(mode, mode)
        config.set('cycle_unit_type', normalized)
        # 告知 CycleUnit 在倒计时结束时不要覆盖我们刚设置的类型
        config.set('skip_cycle_unit_auto_switch', True)

        # print("\n" + config.get('cycle_unit_type'))
        print(f'\n切换到\"{config.get("cycle_unit_type")}\"循环单元')

        # 不再修改全局的 cycles 值（会导致循环计数和顺序异常）

        # 结束倒计时，重新开始倒计时
        if current_running_CycleUnit is not None:
            try:
                current_running_CycleUnit.end()
            except Exception:
                pass
            del current_running_CycleUnit
            # run_state['current'] = None
        
        run_state['dont_change_type'] = True
        run_state['running'] = True

    # 退出程序
    def cb_quit():
        print('快捷键：退出程序')
        run_state['running'] = False
        current_running_CycleUnit = run_state.get('current')
        # print(run_state)
        if current_running_CycleUnit is not None:
            try:
                current_running_CycleUnit.end()
            except Exception:
                pass
        try:
            hk.stop()
        except Exception:
            pass

    # 注册快捷键（Hotkeys 会在创建时绑定）
    hk = Hotkeys(on_extend=cb_extend, on_next=cb_next, on_set_mode=cb_set_mode, on_quit=cb_quit)
    # print(f"--- 模式 #{hk} ---")

    try:
        # config['cycle_unit_type'] = 'work'
        while run_state.get('running', True):
            if config.get('cycles') > 0 and cycle_count > config.get('cycles')*2:
                print("================================")
                print("所有循环已完成！")
                print("================================")
                break

            if config.get('cycle_unit_type') == 'work':
                current_unit = CycleUnit.WorkBlock()
                run_state['current'] = current_unit
                current_unit.run()
                # print(config.get('cycle_unit_type')+"1"+str(run_state.get('dont_change_type')))
                run_state['current'] = None
                if not run_state.get('dont_change_type'):
                    config.set('cycle_unit_type', 'breath')
                else:
                    run_state['dont_change_type'] = False
            elif config.get('cycle_unit_type') == 'breath':
                current_unit = CycleUnit.BreathBlock()
                run_state['current'] = current_unit
                current_unit.run()
                # print(config.get('cycle_unit_type')+"1"+str(run_state.get('dont_change_type')))
                run_state['current'] = None
                if not run_state.get('dont_change_type'):
                    config.set('cycle_unit_type', 'work')
                else:
                    run_state['dont_change_type'] = False
            elif config.get('cycle_unit_type') == 'rest':
                current_unit = CycleUnit.RestBlock()
                run_state['current'] = current_unit
                current_unit.run()
                run_state['current'] = None
                if not run_state.get('dont_change_type'):
                    config.set('cycle_unit_type', 'work')
                else:
                    run_state['dont_change_type'] = False

            # print(current_unit)
            # current_unit = current_unit.next()
            # print(current_unit)
            # run_state['current'] = current_unit
            # current_unit.run()
            
            cycle_count += 1
            print() #换行分隔循环单元

            if not run_state.get('running'):
                break
        run_state['current'] = None

    except KeyboardInterrupt:
        print('\n已手动停止。')
    finally:
        try:
            hk.stop()
        except Exception:
            pass


if __name__ == '__main__':
    main()
