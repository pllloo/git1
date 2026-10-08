# 05-practice.py —— 双记忆机制演示：工作记忆 vs 长期记忆
# 运行: python 05-practice.py  （不依赖任何 API，纯 Python 模拟）

class DemoAgent:
    """简化版 Agent：演示 ReAct 的双记忆机制"""

    def __init__(self):
        self._history = []          # 长期记忆 = 笔记本（跨任务保留）
        self.current_history = []   # 工作记忆 = 草稿纸（每个任务清空）

    def think_and_act(self, question):
        """模拟一轮 ReAct 循环"""
        # ① 任务开始：草稿纸清空（旧任务的草稿不干扰新任务）
        self.current_history = []
        print(f"\n{'='*50}")
        print(f"新任务: {question}")
        print(f"任务开始时: 草稿纸={self.current_history}  笔记本={len(self._history)}条")

        # ② 循环中：每一步都把轨迹写进草稿纸（工作记忆）
        for step in range(3):
            action = f"Action: 执行工具{step+1}"
            observation = f"Observation: 得到结果{step+1}"
            self.current_history.append(action)      # 写草稿纸
            self.current_history.append(observation)
            # 模型每轮决策读到的都是"当前草稿纸"
            print(f"  第{step+1}步后 模型看到的草稿纸: {self.current_history}")

        # ③ 任务结束：只把"问题+最终答案"写进笔记本（长期记忆）
        final_answer = f"'{question}' 的答案是 42"
        self._history.append(f"用户: {question}")     # 写笔记本
        self._history.append(f"助手: {final_answer}")
        print(f"任务结束: 笔记本={self._history}")

        return final_answer


# 连续三个任务，观察两种记忆各自的变化规律
agent = DemoAgent()
agent.think_and_act("1+1 等于几？")
agent.think_and_act("今天星期几？")
agent.think_and_act("天上有几颗星星？")

print(f"\n{'='*50}")
print(f"最终状态:")
print(f"  草稿纸（工作记忆，只剩最后任务的）: {agent.current_history}")
print(f"  笔记本（长期记忆，三个任务都在）: {agent._history}")
