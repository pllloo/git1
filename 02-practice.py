import re

text = 'Action: get_weather(city="北京"， weather="sunny")'

# 第 1 段：抓工具名（对应脚本第 202 行）
m1 = re.search(r"(\w+)\(", text)
print("第1段 工具名:", m1.group(1))

# 第 2 段：抓括号里的参数（对应脚本第 203 行）
m2 = re.search(r"\((.*)\)", text)
print("第2段 参数原文:", m2.group(1))

# 第 3 段：把 名字="值" 配对抓成字典（对应脚本第 204 行）
pairs = re.findall(r'(\w+)="([^"]*)"', m2.group(1))
print("第3段 参数字典:", dict(pairs))
