## LangChain
### 1.LangChain的结构
1. LLM 通过API接入大模型
2. Prompt 提示词
3. Chains 
4. indexes 索引，LLM需要访问训练数据中未包含的外部数据源，如内部文件和外部文档
    1. DOCLoad 文档加载器
    2. 矢量数据库
    3. 文本分割器
5. memory
6. agents
## LangGraph
### 1. 三要素
    1. 状态：整个图的执行过程都围绕着全局状态进行，这个状态通常被定义为一个 Python 的 TypedDict，它可以包含任何你需要追踪的信息，如对话历史、中间结果、迭代次数等。所有的节点都能读取和更新这个中心状态。
```python
    from typing import TypedDict, List

    # 定义全局状态的数据结构
    class AgentState(TypedDict):
        messages: List[str]      # 对话历史
        current_task: str        # 当前任务
        final_answer: str        # 最终答案
        # ... 任何其他需要追踪的状态
```
    2. 节点：接受当前状态作为输入，返回更新后的状态作为输出，节点是执行具体工作的单元
```python
# 定义一个“规划者”节点函数
def planner_node(state: AgentState) -> AgentState:
    """根据当前任务制定计划，并更新状态。"""
    current_task = state["current_task"]
    # ... 调用LLM生成计划 ...
    plan = f"为任务 '{current_task}' 生成的计划..."
    
    # 将新消息追加到状态中
    state["messages"].append(plan)
    return state

# 定义一个“执行者”节点函数
def executor_node(state: AgentState) -> AgentState:
    """执行最新计划，并更新状态。"""
    latest_plan = state["messages"][-1]
    # ... 执行计划并获得结果 ...
    result = f"执行计划 '{latest_plan}' 的结果..."
    
    state["messages"].append(result)
    return state
```
    3. 边：常规边（跳转至下一个固定节点）、工作边（通过函数动态决定下一个动作的跳转方向）
```python
def should_continue(state: AgentState) -> str:
    """条件函数：根据状态决定下一步路由。"""
    # 假设如果消息少于3条，则需要继续规划
    if len(state["messages"]) < 3:
        # 返回的字符串需要与添加条件边时定义的键匹配
        return "continue_to_planner"
    else:
        state["final_answer"] = state["messages"][-1]
        return "end_workflow"
```
**组装**
```python
from langgraph.graph import StateGraph, END

# 初始化一个状态图，并绑定我们定义的状态结构
workflow = StateGraph(AgentState)

# 将节点函数添加到图中
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)

# 设置图的入口点
workflow.set_entry_point("planner")

# 添加常规边，连接 planner 和 executor
workflow.add_edge("planner", "executor")

# 添加条件边，实现动态路由
workflow.add_conditional_edges(
    # 起始节点
    "executor",
    # 判断函数
    should_continue,
    # 路由映射：将判断函数的返回值映射到目标节点
    {
        "continue_to_planner": "planner", # 如果返回"continue_to_planner"，则跳回planner节点
        "end_workflow": END               # 如果返回"end_workflow"，则结束流程
    }
)

# 编译图，生成可执行的应用
app = workflow.compile()

# 运行图
inputs = {"current_task": "分析最近的AI行业新闻", "messages": []}
for event in app.stream(inputs):
    print(event)
```
---
## question
### 1. 今天的任务是交互式程序。什么是交互式程序？
程序运行中会停下来等待用户输入，根据输入继续执行，一轮轮对话知道主动退出
### 2. 为什么不用改配置了？
```python
Dialogue_System.py 第 32-37 行：
    model=os.getenv("LLM_MODEL_ID", "gpt-4o-mini")   ← 从 .env 读"LLM_MODEL_ID"
    api_key=os.getenv("LLM_API_KEY")                 ← 从 .env 读"LLM_API_KEY"
    base_url=os.getenv("LLM_BASE_URL", ...)          ← 从 .env 读"LLM_BASE_URL"
```
直接从已经配置好的.env文件读取了三件套，所以不用修改配置，这就是环境变量
如果把"YOUR_API_KEY" 这种占位符写死在代码里，就属于硬编码

### 3. vscode可以直接新建终端
### 4. 程序骨架怎么看，到底哪些是骨架
    骨架回答三个问题：分几块？数据怎么流？入口在哪？ 其余一切（打印、异常提示、计数变量）都是外壳。
    
| 遍 | 花多少精力 | 只看什么 | 完成标准 |
| --- | --- | --- | --- |
| 第 1 遍 | 30% | 只看骨架：`import`、`class`/函数定义（不看函数体）、`main` 入口、`add_edge` 类"结构声明" | 能不看代码复述结构 + 画出数据流图 |
| 第 2 遍 | 50% | 只深入主干：每个节点函数的核心逻辑（`understand` 怎么拼 prompt、`search` 怎么调 API） | 能回答"想加一个节点/改一个步骤，动哪里" |
| 第 3 遍 | 20% | 按需看细节：哪里要改才看哪里（如 `astream` 的用法、异常处理） | 具体动手时查 |

