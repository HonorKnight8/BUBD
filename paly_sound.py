
# 加载 pygame ，用于播放 mp3（优先），若未安装则使用 winsound 或蜂鸣声
import os
import sys
import time
import winsound


try:
    import pygame
except Exception:
    pygame = None
    print("pygame module not found. using winsound or beep instead.")
    # exit()

def play_alert(sound_file: str = None, volume: float = None, duration: int = None):
    """
    播放铃声：优先使用 pygame 播放指定文件（若存在）；
    否则回退到 winsound 或终端蜂鸣。
    `volume` 范围 0.0-1.0；若提供 1-100 的整数也会被接受并归一化。
    """
    # 规范化音量
    vol = None
    if volume is not None:
        try:
            vol = float(volume)
            if vol > 1:
                vol = max(0.0, min(1.0, vol / 100.0))
        except Exception:
            vol = None

    # 尝试使用 pygame 播放文件
    if sound_file and pygame:
        # 解析相对路径（优先当前目录，其次 sounds/ 子目录）
        candidate = sound_file
        if not os.path.isabs(candidate):
            # 脚本目录
            base = os.path.dirname(os.path.abspath(__file__))
            p1 = os.path.join(base, candidate)
            p2 = os.path.join(base, 'sounds', candidate)
            if os.path.exists(p1):
                candidate = p1
            elif os.path.exists(p2):
                candidate = p2
        if os.path.exists(candidate):
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(candidate)
                if vol is not None:
                    try:
                        pygame.mixer.music.set_volume(vol)
                    except Exception:
                        pass
                pygame.mixer.music.play(-1)
                if duration is not None:
                    try:
                        time.sleep(max(1, int(duration)))
                        pygame.mixer.music.stop()
                        pygame.mixer.quit()
                    except Exception:
                        pass
                return
            except Exception:
                # fallthrough to other methods
                try:
                    pygame.mixer.quit()
                except Exception:
                    pass

    # 回退：使用 winsound 或控制台蜂鸣
    if winsound:
        # 用短促蜂鸣重复直到达到时长或固定三声
        if duration and duration > 0:
            end = time.time() + max(1, int(duration))
            while time.time() < end:
                try:
                    winsound.Beep(750, 200)
                except Exception:
                    try:
                        winsound.MessageBeep()
                    except Exception:
                        sys.stdout.write('\a')
                        sys.stdout.flush()
                time.sleep(0.2)
        else:
            for _ in range(3):
                try:
                    winsound.Beep(750, 200)
                except Exception:
                    try:
                        winsound.MessageBeep()
                    except Exception:
                        sys.stdout.write('\a')
                        sys.stdout.flush()
                time.sleep(0.15)
    else:
        if duration and duration > 0:
            end = time.time() + max(1, int(duration))
            while time.time() < end:
                sys.stdout.write('\a')
                sys.stdout.flush()
                time.sleep(0.5)
        else:
            for _ in range(3):
                sys.stdout.write('\a')
                sys.stdout.flush()
                time.sleep(0.15)