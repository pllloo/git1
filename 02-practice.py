# import re

# text = 'Action: get_weather(city="北京"， weather="sunny")'

# # 第 1 段：抓工具名（对应脚本第 202 行）
# m1 = re.search(r"(\w+)\(", text)
# print("第1段 工具名:", m1.group(1))

# # 第 2 段：抓括号里的参数（对应脚本第 203 行）
# m2 = re.search(r"\((.*)\)", text)
# print("第2段 参数原文:", m2.group(1))

# # 第 3 段：把 名字="值" 配对抓成字典（对应脚本第 204 行）
# pairs = re.findall(r'(\w+)="([^"]*)"', m2.group(1))
# print("第3段 参数字典:", dict(pairs))

class ChatAgent:
    def __init__(self):
        self.prompt_history = []           # 初始化空历史

    def add_user_message(self, message: str):
        self.prompt_history.append(f"用户请求: {message}")

agent = ChatAgent()
print(agent.prompt_history)                # []

agent.add_user_message("今天天气如何")      # 调用：只传一个字符串
print(agent.prompt_history)                # ['用户请求: 今天天气如何']

agent.add_user_message("帮我推荐景点")
print(agent.prompt_history)                # 两条了

result = agent.add_user_message("hi")      # 看返回值
print(result)                              # None ← 验证：没有 return
