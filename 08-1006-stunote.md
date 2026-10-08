# 七章代码
目标：框架整体跑通课程示例——这是"四层架构"最后一块拼图。

流程四步（按顺序来）：

跑 test_simple_agent.py（约 4 个测试：基础对话 / 工具增强 / 流式 / 动态添加工具）——你自己在终端跑，卡住贴报错
读 my_simple_agent.py——带着三个问题读：
它继承了谁？（class MySimpleAgent(SimpleAgent)——基类是框架自带的，不是课程那个 ABC 演示版）
__init__ 里四件套（name/llm/system_prompt/config）是怎么"继承"来的？（找 super().__init__）
它的 run() 是"填血肉"——run 里干了什么？
跑 test_react_agent.py——框架化的 ReAct，你会看到似曾相识的 Thought/Action 输出
读 my_react_agent.py——重点对比：和你 ch4 手写的 ReAct.py 比，循环还在吗？工具调用走什么？历史记录（记忆）走什么？
打卡标准（两个测试跑通后，回答两道题）
① 用一句话说明：框架版 ReAct 和你 ch4 手写的 ReAct.py，两处相同、两处不同（提示：循环逻辑相同吗？工具调用方式相同吗？记忆存储相同吗？代码量相同吗？）

② 四层架构里的"记忆层"：在框架里谁在写 _history、谁在读它？（提示：从基类 Agent 的 self._history 开始追）

## 摘要、重点整理
1. >my_simpleagent中 工具循环流程

```python
用户提问
   │
   ▼
run(input_text)
   ├─ ① 组装消息：system(增强提示词) + history(读记忆) + user(当前问题)
   ├─ ② 分流：enable_tool_calling?
   │     ├─ 否 → 直接 llm.invoke → 存记忆 → 返回答案 ──────────→ 结束
   │     └─ 是 → 进入 _run_with_tools 循环 ↓
   │
   ▼
循环（每轮开头先查 current_iteration < max_tool_iterations ← 上限刹车）
   ├─ ③ 调用 LLM
   ├─ ④ 正则检测工具调用（_parse_tool_calls）
   │     ├─ 有调用：
   │     │    ├─ 执行工具（_execute_tool_call：参数解析 → 注册表执行）
   │     │    ├─ 结果拼回 messages（干净回复 + 工具结果两段）
   │     │    └─ continue → 回到循环顶（再问模型，模型决定下一步）
   │     └─ 无调用：
   │          ├─ final_response = response（标记最终回答）
   │          └─ break 跳出
   │
   ├─ 兜底②：轮数耗尽仍无答案 → 强制再 invoke 一次
   ▼
收尾
   ├─ 写记忆：add_message(用户问题) + add_message(最终回答)
   └─ return final_response → 用户拿到答案
```
_get_enhanced_system_prompt + llm = 模型层接口；
add_tool/_execute_tool_call = 工具层；
run/_run_with_tools = 循环控制层；
_history + add_message = 记忆层

2. MySimpleAgent 类结构总览

```python
MySimpleAgent(SimpleAgent)              ← 继承框架内置 SimpleAgent
│
├─ __init__                             ← 出厂配置：super() 接力四件套
│
├─ run()                                ← 前台：组装消息 + 分流转交
├─ _run_with_tools()                    ← 后台：工具循环主战场
│
├─ 解析三件套（工具循环的零件）：
│   ├─ _parse_tool_calls()              ← 回复 → 工具调用列表
│   ├─ _parse_tool_parameters()         ← 参数原文 → 参数字典
│   └─ _execute_tool_call()             ← 查注册表 → 执行 → 包装结果
│
├─ _get_enhanced_system_prompt()        ← 拼系统提示词（含工具说明书）
│
└─ 对外接口（给调用方用，非内部流程）：
    ├─ stream_run()                     ← 流式对话版（yield，以后再学）
    ├─ add_tool() / remove_tool()       ← 动态加/移除工具
    └─ list_tools() / has_tools()       ← 查询工具箱状态
```

3. agent的双记忆机制
- Agent 同时拥有两种记忆：草稿纸（工作记忆，服务当前任务）和笔记本（长期记忆，跨任务累积）。
| 维度 | 工作记忆 `current_history` | 长期记忆 `_history` |
| --- | --- | --- |
| 类比 | 草稿纸 | 笔记本 |
| 存什么 | 本轮的 Action/Observation 执行轨迹 | 用户问题 + 最终回答 |
| 何时清空 | 每个任务开始（`run` 第 57 行 = `[]`） | 只增不清 |
| 谁在读 | 循环内每轮（第 68 行 `join` 进提示词） | 循环内不读；跨轮对话时读（如 `SimpleAgent` 的 `run`） |
| 类型 | 字符串列表 | Message 对象列表 |

- 代码落点（my_react_agent.py）
定义：第 51 行 self.current_history: List[str] = []
清空：第 57 行（run 开头）
写工作记忆：第 93-94 行 append(Action/Observation)
读工作记忆：第 68 行 history_str = "\n".join(self.current_history)
写长期记忆：第 85-86、98-99 行 add_message(...)（基类方法，写的是 _history）
- 为什么分成两个？
决策要干净：模型每轮只该看"我这题做到哪了"，不该被历史任务的轨迹干扰
上下文有限且贵：全部历史都塞进提示词，越长越烧 token、模型越容易"迷失中间"
各司其职：工作记忆管"当下"，长期记忆管"以后"（多轮对话、审计、导出）
## Question
1. >报错怎么读？
```python
① File "...my_simple_agent.py", line 91, in _run_with_tools
     tool_calls = self._parse_tool_calls(response)      ← 你的代码最后出现的位置
② File "...my_simple_agent.py", line 133, in _parse_tool_calls
     matches = re.findall(pattern, text)                ← 真正"爆炸"的一行
③ File "...re\__init__.py", line 278, in findall        ← 库内部，一般跳过
④ TypeError: expected string or bytes-like object, got 'LLMResponse'
```
第一步：从最后一行读起。 报错最后一行永远是"类型 + 人话原因"：正则想要字符串，你给的却是 LLMResponse 对象——信息量最大。

第二步：往上找"你自己的代码"的帧。 ②行 133：re.findall(pattern, text) 爆炸，说明实参 text 不是字符串。

第三步：再追一层找到病根。 ①行 91：_parse_tool_calls(response)——这个 response 就是上次那个 llm.invoke() 返回的 LLMResponse 对象，一路传进了正则。病根和上次一模一样：没取 .content。

第四步：跳过库内部的帧（③那些 re/__init__.py、pydantic 的帧）——除非你要改库源码，否则它们只是噪音。只看"你自己的文件"那几帧 + 最后一行。

2. >正则解析在哪里？
有对应的从模型回答的文本中解析工具的函数,正则解析在这里用到
```python
def _parse_tool_calls(self, text: str) -> list:
        """解析文本中的工具调用"""
          pattern = r'\[TOOL_CALL:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, text)

        tool_calls = []
        for tool_name, parameters in matches:
            tool_calls.append({
                'tool_name': tool_name.strip(),
                'parameters': parameters.strip(),
                'original': f'[TOOL_CALL:{tool_name}:{parameters}]'
            })

        return tool_calls
```
3. >enable_tool_calling,启用工具调用具体是如何执行的？
```python
① 出厂时定值：父类 SimpleAgent.__init__ 里
   self.enable_tool_calling = enable_tool_calling and tool_registry is not None
   （你传了 tool_registry 才会真正启用——光说"启用"没工具箱也不行）

② 使用时分流：MySimpleAgent.run() 里
   if not self.enable_tool_calling:     ← 没启用 → 直接 invoke 返回
       ...
   return self._run_with_tools(...)     ← 启用 → 进入工具循环
```
>什么是tool_registry
- 工具注册表

4. >while current_iteration < max_tool_iterations:  是为了限制工具调用的迭代次数，这应该是为了防止工具调用结果不清晰或者不理想或者其他情况，导致反复调用陷入循环或过多次数的迭代，在while current_iteration < max_tool_iterations: 中叫最大thought-action对数

5. > continue会继续while循环调用下一个工具并返回对应工具的结果，因为上一个工具调用后移除了标记，所以不会重复调用（这个工具调用的顺序是如何规定的？）
**这个理解不对** continue 跳回 while 开头后，下一轮第一件事是：
```python
response = self.llm.invoke(messages, **kwargs)    # ← 再次调用 LLM！
```
工具调用顺序由模型决定，
下一轮 messages 里多了"工具执行结果：...请基于这些结果给出完整的回答"，模型读到后自己决定：信息够了 → 直接回答；不够 → 再要求调另一个工具。程序从不规定顺序，程序只负责"每轮把最新消息交给模型"。这就是 ReAct 的本质：程序提供循环框架，模型做决策——和你 ch4 手写的 ReAct.py 一模一样。

6. >_parse_tool_parameters函数的作用
- 把“参数原文”变成“参数字典”
- 模型输出工具调用格式是 [TOOL_CALL:工具名:参数]（第 132 行正则）。_parse_tool_calls 拆出两样：工具名 + 参数字符串。但执行工具时，很多工具需要的是字典（tool.run({'action': 'search', 'query': 'Python'})）。中间差一步转换——_parse_tool_parameters 就是这步转换。
```python
"action=search,query=Python,limit=3"     ← 模型给的一串文字（字符串）
        ↓ _parse_tool_parameters
{'action': 'search', 'query': 'Python', 'limit': '3'}   ← 工具能用的字典
```
<details>
<summary>展开：具体函数</summary>

```python
def _parse_tool_parameters(self, tool_name: str, parameters: str) -> dict:
        """智能解析工具参数"""
        param_dict = {}

        if '=' in parameters:
            # 格式: key=value 或 action=search,query=Python
            if ',' in parameters:
                # 多个参数：action=search,query=Python,limit=3
                pairs = parameters.split(',')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        param_dict[key.strip()] = value.strip()
            else:
                # 单个参数：key=value
                key, value = parameters.split('=', 1)
                param_dict[key.strip()] = value.strip()
        else:
            # 直接传入参数，根据工具类型智能推断
            if tool_name == 'search':
                param_dict = {'query': parameters}
            elif tool_name == 'memory':
                param_dict = {'action': 'search', 'query': parameters}
            else:
                param_dict = {'input': parameters}

        return param_dict
```
</details>
## 代码示例

```python
# 这里放代码
```

## 我的理解 / 踩坑记录

> 用自己的话复述一遍，讲不清楚 = 没学会。

## 待办

- [ ] 还没搞懂的问题
- [x] 已解决：xxx（怎么解决的）
````

---

## 速记口诀

> **标记要空格，段落要空行，代码标语言，写完先预览。**