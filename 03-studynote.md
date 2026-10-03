# Day3 studynote
## 旅游助手FirstAgentTest.py 主循环部分
整体结构：
for i in range(5):              防死循环，最多 5 轮
  ① 拼 prompt
       full_prompt = 把历史用换行拼成一段

  ② 问大脑
       llm_output = llm.generate(...)
       必要时截断多余的 Thought-Action
       把模型输出 append 进历史   #大脑具体是怎么工作的呢，其实就是前面把调用LLM封装起来的类，环境都已经配置好的，这里直接用，给输入，得到LLM的输出

  ③ 解析 Action
       抠出 Action: 后面的字
       抠不到 → 写成 Observation 错误，continue 下一轮
       以 Finish 开头 → 取出最终答案，break
       否则三连正则：工具名 + 参数原文 + 参数字典

  ④ 动手
       available_tools[tool_name](**kwargs)
       工具不存在 → 写成错误 Observation

  ⑤ 记观察
       Observation: ...  append 进历史
       （记忆变长，下一轮模型能看见这次结果）
       
| 轮次 | 历史里已有 | 模型决定 | 循环怎么走 |
| --- | --- | --- | --- |
| 1 | 只有用户请求 | `get_weather` | 走 ④⑤，不 break |
| 2 | 请求+输出1+天气 | `get_attraction` | 再走 ④⑤ |
| 3 | 上面全部+景点 | `Finish[...]` | 走 ③ 的 break |


| 理论 | 代码里是谁 |
| --- | --- |
| 感知 | 用户请求 + 每次的 Observation（211–222 行 append） |
| 思考 | `llm.generate`：输出 Thought + Action |
| 行动 | 215 行调工具，或 205 行 Finish |
| 观察 | 工具返回值写成 `Observation:` 喂回下一圈 |