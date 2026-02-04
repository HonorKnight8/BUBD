# TOML 解析：Python 3.11+ 内置 tomllib，用于读取配置文件
# import tomllib
try:
    import tomllib
    # print(tomllib)
except Exception:
    print("tomllib module not found. run 'pip install tomllib' to install it.")
    exit()

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# 获取所有配置的方法
def getall():
    return config

def get(key, default=None):
    return config.get(key, default)

def set(key, value):
    config[key] = value

