import time
import keyboard


class Hotkeys:
	"""
	Hotkeys 快捷键管理类。

	支持快捷键：
	- Ctrl+1..Ctrl+9, Ctrl+0: 分别延长 1..9, 10 分钟（回调：on_extend(minutes)）
	- Ctrl+N: 提前结束当前循环单元，进入下一个循环单元（回调：on_next()）
	- Ctrl+W: 结束当前循环单元，进入“工作”循环单元（回调：on_set_mode('work')）
	- Ctrl+R: 结束当前循环单元，进入“小憩”循环单元（回调：on_set_mode('short_breath')）
	- Ctrl+B: 结束当前循环单元，进入“休息”循环单元（回调：on_set_mode('rest')）
	- Ctrl+Q: 退出程序（回调：on_quit()）

	回调均由外部注入，便于与主程序集成。
	"""

	def __init__(self, on_extend=None, on_next=None, on_set_mode=None, on_quit=None):
		
		# 注册回调函数
		self.on_extend = on_extend or (lambda minutes: None)
		self.on_next = on_next or (lambda: None)
		self.on_set_mode = on_set_mode or (lambda mode: None)
		self.on_quit = on_quit or (lambda: None)

		self._running = True
		self._hotkeys = []
		self._hotkey_descriptions = []
		self._register_hotkeys()
		# 在创建后打印已注册的快捷键信息
		self.print_registered_hotkeys()

	def _register_hotkeys(self):
		# Ctrl+1..9 -> 延长 1..9 分钟
		for i in range(1, 10):
			handler = lambda m=i: self._handle_extend(m)
			hk = keyboard.add_hotkey(f'ctrl+{i}', handler)
			self._hotkeys.append(hk)
			self._hotkey_descriptions.append(f'Ctrl+{i} -> extend {i} minute(s)')

		# Ctrl+0 -> 延长 10 分钟
		hk0 = keyboard.add_hotkey('ctrl+0', lambda: self._handle_extend(10))
		self._hotkeys.append(hk0)
		self._hotkey_descriptions.append('Ctrl+0 -> extend 10 minute(s)')

		# 其他控制键
		self._hotkeys.append(keyboard.add_hotkey('ctrl+n', self._handle_next))
		self._hotkey_descriptions.append('Ctrl+N -> next')
		self._hotkeys.append(keyboard.add_hotkey('ctrl+w', lambda: self._handle_set_mode('work')))
		self._hotkey_descriptions.append("Ctrl+W -> set_mode 'work'")
		self._hotkeys.append(keyboard.add_hotkey('ctrl+b', lambda: self._handle_set_mode('breath')))
		self._hotkey_descriptions.append("Ctrl+B -> set_mode 'breath'")
		self._hotkeys.append(keyboard.add_hotkey('ctrl+r', lambda: self._handle_set_mode('rest')))
		self._hotkey_descriptions.append("Ctrl+R -> set_mode 'rest'")
		self._hotkeys.append(keyboard.add_hotkey('ctrl+q', self._handle_quit))
		self._hotkey_descriptions.append('Ctrl+Q -> quit')

	def print_registered_hotkeys(self):
		print('已注册快捷键：')
		print(
			" 按 Ctrl+1 延长 1 分钟 \n"
			" 按 Ctrl+2..9 依此类推 \n"
			" 按 Ctrl+0 延长 10 分钟 \n"
            " 按 Ctrl+N 提前结束当前循环单元，进入下一个循环单元 \n"
			" 按 Ctrl+W 切换到“工作”循环单元 \n"
            " 按 Ctrl+B 切换到“小憩”循环单元 \n"
            " 按 Ctrl+R 切换到“休息”循环单元 \n"
            " 按 Ctrl+Q 退出程序 \n"
			" 按 Ctrl+C 退出程序 \n"
			)
		# for i, desc in enumerate(self._hotkey_descriptions, start=1):
		# 	print(f'  {i}. {desc}')

	def _handle_extend(self, minutes: int):
		try:
			self.on_extend(minutes)
		except Exception:
			pass

	def _handle_next(self):
		try:
			self.on_next()
		except Exception:
			pass

	def _handle_set_mode(self, mode: str):
		try:
			self.on_set_mode(mode)
		except Exception:
			pass

	def _handle_quit(self):
		# 先调用回调，让上层做清理
		try:
			self.on_quit()
		except Exception:
			pass
		self.stop()

	def stop(self):
		"""注销所有快捷键并停止等待循环"""
		try:
			keyboard.unhook_all_hotkeys()
		except Exception:
			pass
		self._running = False

	def wait(self):
		"""阻塞等待，直到调用 `stop()`（例如按 Ctrl+Q）"""
		try:
			while self._running:
				time.sleep(0.2)
		except KeyboardInterrupt:
			self.stop()



if __name__ == '__main__':
	# 示例用法：在独立运行时可以测试这些快捷键
	def example_extend(m):
		print(f'收到延长请求：{m} 分钟')

	def example_next():
		print('收到：提前结束当前循环单元，进入下一个')

	def example_set_mode(mode):
		print(f'切换到循环单元：{mode}')

	def example_quit():
		print('收到退出请求，程序即将退出')

	hk = Hotkeys(on_extend=example_extend, on_next=example_next, on_set_mode=example_set_mode, on_quit=example_quit)
	print('快捷键已注册：Ctrl+1..Ctrl+0 延长 1..10 分钟，Ctrl+N/W/R/B 切换，Ctrl+Q 退出')
	hk.wait()