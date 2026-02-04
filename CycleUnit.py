import sys
import time

# 用于多线程播放铃声，及监听输入
import threading

# 加载 配置管理类
import config

# 导入播放铃声的函数
from paly_sound import play_alert

# 颜色支持
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
    HAS_COLOR = True
except Exception:
    HAS_COLOR = False
    class Fore:
        BLUE = ''
        YELLOW = ''
        GREEN = ''
        LIGHTMAGENTA_EX = ''
    class Style:
        RESET_ALL = ''

# 循环单元基类
class CycleUnit:
    def __init__(self,  label, color):
        # self.cfg = cfg
        self.label = label
        self.color = color
        self._stopped = False
        # self.duration = config.get('default_duration', 60)  # 默认持续时间，单位秒
        if label == "work":
            self.duration = config.get('work_minutes', 25) * 60
        elif label == "breath":
            self.duration = config.get('breath_minutes', 5) * 60
        elif label == "rest":
            self.duration = 0

    # 倒计时显示方法
    def show_countdown(self, title: str, minutes: int, color: str = None):
        start_time = time.time()
        try:
            while True:
                if getattr(self, '_stopped', False):
                    print()
                    break
                elapsed = int(time.time() - start_time)
                # remaining uses self.duration so that extend() updates are effective
                remaining = int(self.duration) - elapsed
                if remaining < 0:
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

        # 调试：输出结束时的上下文
        # print(f"show_countdown end: self.label={self.label}, stopped={getattr(self,'_stopped',False)}, current config before set={config.get('cycle_unit_type')}")

        # 如果上层通过快捷键请求了模式切换，跳过自动覆盖（由 cb_set_mode 设置）
        if config.get('skip_cycle_unit_auto_switch'):
            # print('show_countdown: skipping auto switch due to skip_cycle_unit_auto_switch flag')
            try:
                config.set('skip_cycle_unit_auto_switch', False)
            except Exception:
                pass
            return

        # 倒计时完成后，按当前单元类型设置下一个循环单元，
        # 不应依据 config 中的值（可能已被外部快捷键修改），
        # 应依据当前单元的标签确定下一单元，避免竞争条件导致相反结果。
        if self.label == 'work':
            config.set('cycle_unit_type', 'breath')
            # print("show_countdown: setting cycle_unit_type -> breath (from work)")
        else:
            # 如果不是 work（可能是 breath 或 rest ），则统一切换到 work
            config.set('cycle_unit_type', 'work')
            # print("show_countdown: setting cycle_unit_type -> work (from breath)")
        # time.sleep(1)
        return
    
    # 持续时间显示方法，用于rest单元（大休息：standby 待机）
    def show_duration(self, title: str, color: str = None):
        start_time = time.time()
        try:
            while True:
                if getattr(self, '_stopped', False):
                    print()
                    break
                elapsed = int(time.time() - start_time)
                m = elapsed // 60
                s = elapsed % 60
                text = f"[{title}] 已经持续时间: {m:02d}:{s:02d}"
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

    # 响铃
    def ring(self):
        sound_file = config.get(f"{self.label}_bell")
        work_bell_volume = int(config.get(f"{self.label}_bell_volume"))
        bell_duration = int(config.get('bell_duration'))
        bell_thread = threading.Thread(target=play_alert, args=(sound_file, work_bell_volume, bell_duration))
        bell_thread.start()

    def run(self):

        # print(f"Starting {self.label} for {self.duration} seconds")

        # 播放提示音,RestBlock例外
        if self.label != "rest":
            self.ring()

        # 清除停止标志，开始新的倒计时
        self._stopped = False

        # 模拟倒计时，RestBlock则显示持续时间
        if self.label == "rest":
            self.show_duration(self.label, self.color)
        else:
            self.show_countdown(self.label, self.duration / 60, self.color)

        # print(f"{self.label} completed")
        return
    
    #提前结束本循环单元的方法
    def end(self):
        # print(f"Ending {self.label}_cycle_unit early")
        # config.set('cycle_unit_type', 'work' if self.label != 'work' else 'breath')
        self._stopped = True

    # 执行下一个循环单元的方法
    def next(self):
        
        # config.set('cycle_unit_type', 'work' if self.label != 'work' else 'breath')
        # 基于当前单元标签来决定下一个单元类型，避免读取已被外部修改的配置
        if self.label == 'work':
            config.set('cycle_unit_type', 'breath')
        else:
            config.set('cycle_unit_type', 'work')
        
        # print(f"goto next cycle unit \"{config.get('cycle_unit_type')}\" from {self.label}")
        # print(config.get('cycle_unit_type'))

        #返回一个新的循环单元
        if self.label == "work":
            return BreathBlock()
        else:
            return WorkBlock()

    #延长本循环单元的方法
    def extend(self, extra_time):
        self.duration += extra_time
        print(f"Extended {self.label} by {extra_time} seconds")
    # 获取单元信息的方法
    def info(self):
        return f"{self.label}: {self.duration} seconds"
    

# 工作单元
class WorkBlock(CycleUnit):
    def __init__(self):
        super().__init__(label="work", color="BLUE")
        
    def run(self):
        print(Fore.BLUE + "🔴 工作开始！" + Style.RESET_ALL if HAS_COLOR else "🔴 工作开始！")
        super().run()
        print(Fore.LIGHTMAGENTA_EX + "🔔 工作时间结束！" + Style.RESET_ALL if HAS_COLOR else "🔔 工作时间结束！")
        return

# 小憩单元
class BreathBlock(CycleUnit):
    def __init__(self):
        super().__init__(label="breath", color="YELLOW")

    def run(self):
        print(Fore.YELLOW + "🟢 休息时间！" + Style.RESET_ALL if HAS_COLOR else "🟢 休息时间！")
        super().run()
        print(Fore.LIGHTMAGENTA_EX + "🔔 休息时间结束！" + Style.RESET_ALL if HAS_COLOR else "🔔 休息时间结束！")
        return

# 中断单元（大休息，无倒计时，自主结束，进入下一循环单元：工作）
class RestBlock(CycleUnit):
    def __init__(self):
        super().__init__(label="rest", color="GREEN")

    # def end(self):
    #     print("Ending rest time")
    #     self._stopped = True

    def run(self):
        print(Fore.GREEN + "🔵 待机时间！请自行安排时间，按 Ctrl+W/B 键直接进入“工作/小憩”循环单元" + Style.RESET_ALL if HAS_COLOR else "🔵 待机时间！请自行安排时间，按 Ctrl+W/B 键直接进入“工作/小憩”循环单元")
        
        # # 在后台线程中监听 Enter 键，按下时调用 end() 以终止 show_duration 循环
        # def _wait_enter_and_end():
        #     try:
        #         input()
        #         self.end()
        #     except Exception:
        #         pass

        # t = threading.Thread(target=_wait_enter_and_end, daemon=True)
        # t.start()

        super().run()

        # t.stop = True  # 停止监听输入线程

        print(Fore.LIGHTMAGENTA_EX + "🔔 待机时间结束！" + Style.RESET_ALL if HAS_COLOR else "🔔 待机时间结束！")

        return
    
    


