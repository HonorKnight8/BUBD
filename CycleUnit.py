import sys
import time

# 用于多线程播放铃声
import threading

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
        GREEN = ''
        YELLOW = ''
        CYAN = ''
        MAGENTA = ''
    class Style:
        RESET_ALL = ''

# 循环单元基类
class CycleUnit:
    def __init__(self, cfg, label, color):
        self.cfg = cfg
        self.label = label
        self.color = color
        # self.duration = cfg['duration']  # 默认持续时间，单位秒
        if label == "work":
            self.duration = cfg.get('work_minutes', 25) * 60
        elif label == "rest":
            self.duration = cfg.get('rest_minutes', 5) * 60
        elif label == "break":
            self.duration = 0

    def show_countdown(self, title: str, minutes: int, color: str = None):
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
    
    # 响铃
    def ring(self):
        sound_file = self.cfg.get(f"{self.label}_bell")
        work_bell_volume = int(self.cfg[f"{self.label}_bell_volume"])
        bell_duration = int(self.cfg['bell_duration'])
        bell_thread = threading.Thread(target=play_alert, args=(sound_file, work_bell_volume, bell_duration))
        bell_thread.start()

    def run(self):

        # print(f"Starting {self.label} for {self.duration} seconds")

        # 播放提示音
        self.ring()

        # 模拟倒计时
        self.show_countdown(self.label, self.duration / 60, self.color)
        
        # print(f"{self.label} completed")
        return
    
    #提前结束本循环单元的方法
    def end(self):
        print(f"Ending {self.label} early")
    #延长本循环单元的方法
    def extend(self, extra_time):
        self.duration += extra_time
        print(f"Extended {self.label} by {extra_time} seconds")
    # 获取单元信息的方法
    def info(self):
        return f"{self.label}: {self.duration} seconds"
    

# 工作单元
class WorkBlock(CycleUnit):
    def __init__(self, cfg):
        super().__init__(cfg=cfg, label="work", color="GREEN")
        print(Fore.GREEN + "🔴 工作开始！" + Style.RESET_ALL if HAS_COLOR else "🔴 工作开始！")
    def run(self):
        super().run()
        print(Fore.CYAN + "🔔 工作时间结束！" + Style.RESET_ALL if HAS_COLOR else "🔔 工作时间结束！")
        return

# 小憩单元
class RestBlock(CycleUnit):
    def __init__(self, cfg):
        super().__init__(cfg=cfg, label="rest", color="YELLOW")
        print(Fore.YELLOW + "🟢 休息时间！" + Style.RESET_ALL if HAS_COLOR else "🟢 休息时间！")
    def run(self):
        super().run()
        print(Fore.CYAN + "🔔 休息时间结束！" + Style.RESET_ALL if HAS_COLOR else "🔔 休息时间结束！")
        return

# 中断单元（大休息，无倒计时，自主结束，进入下一循环单元：工作）
class BreakBlock(CycleUnit):
    def __init__(self, cfg):
        super().__init__(cfg=cfg, label="break", color="CYAN")
    def run(self):
        print(Fore.MAGENTA + "🔵 大休息时间！请自行安排时间，按 Enter 键继续..." + Style.RESET_ALL if HAS_COLOR else "🔵 大休息时间！请自行安排时间，按 Enter 键继续...")
        input()
        print(Fore.CYAN + "🔔 大休息结束！" + Style.RESET_ALL if HAS_COLOR else "🔔 大休息结束！")
        return

