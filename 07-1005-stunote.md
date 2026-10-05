

# 七章前半，理解框架四层设计

> 一句话说明这篇笔记讲什么。

## 核心概念
## 四层架构图（ch7 打卡）

### 模型层
- 职责：负责调用模型
- 为什么独立：为agent提供思考的大脑
- 代码落点：7.2

### 工具层
- 职责：提供agent可能用到的工具
- 为什么独立：方便工具管理和开发
- 代码落点：7.5

### 循环控制层
- 职责：### 循环控制层
- 职责：配合好LLM和工具的充分使用
- 代码落点：在 run里面

### 记忆层
- 职责：历史对话和模型输出
- 为什么独立：*循环逻辑与"用什么模型、有什么工具"解耦——换范式只改这一层，模型层和工具层纹丝不动*

- 代码落点：在 run里面

### 记忆层
- 职责：~~历史对话和模型输出~~保存对话历史（用户消息、模型输出、工具结果），供每轮决策参考
- 代码落点：分散


## Question
1. >重写 __init__ 方法以支持新供应商。目标是：当用户传入 provider="modelscope" 时，执行我们自定义的逻辑；否则，就调用父类 HelloAgentsLLM 的原始逻辑，使其能够继续支持 OpenAI 等其他内置的供应商。
条件分流，我的场景走我的代码，其余场景就交给父类
```python
class MyLLM(HelloAgentsLLM):              # 继承父类
    def __init__(self, provider="openai", **kwargs):
        if provider == "modelscope":
            # 【第一句话】执行我们自定义的逻辑：
            # 把 base_url 设成 ModelScope 的地址、处理它特殊的 Key 规则……
            kwargs["base_url"] = "https://api-inference.modelscope.cn/v1/"
            ...
        # 【第二句话】调用父类的原始逻辑：
        super().__init__(**kwargs)         # ← 父类接手，完成通用的初始化
```

2. >VLLM 和 Ollama 等优秀工具。它们通过连续批处理、PagedAttention 等技术，显著提升了模型的吞吐量和运行效率，并将模型封装为兼容 OpenAI 标准的 API 服务。这意味着，我们可以将它们无缝地集成到 HelloAgentsLLM 中。Vllm ollama到底是什么工具？有什么功能？如何运行？

大模型的"本体"是权重文件（几个 GB 到几百 GB），它不能像普通程序那样双击运行。你需要一套软件来：加载权重 → 接收请求 → 调度算力 → 返回结果。直接用 HuggingFace 的 transformers 库加载模型调用，慢且浪费显存（一次只处理一个请求）。

vLLM 和 Ollama 就是干"包装"这件事的：在你自己的电脑/服务器上跑起一个服务，然后像调 OpenAI 一样调它——只不过模型和数据都在本地。
>为什么要把模型包装成“本地API”服务？
| 理由 | 含义 | 类比 |
| --- | --- | --- |
| 标准化接口 | 包装成 OpenAI 兼容格式后，所有现成代码（HelloAgentsLLM、LangChain）零改动就能接本地模型——大家讲同一种语言 | 菜单标准化，客人都会点 |
| 高效调度 | 模型常驻显存（不用每次重新加载），能排队、批量处理多请求、高效管显存 | 厨师常驻后厨，不用每单重新生火备菜 |
| 服务化 | 一个服务供多个程序、多人同时用（你的代码、浏览器、团队共享一台 GPU） | 一个厨房服务一屋子客人 |
| 解耦 | 模型运行环境（GPU 服务器）和你的 Agent 业务代码分离，各自独立部署升级 | 你只管点菜，不必懂后厨 |

3. >实例化是什么意思？
实例化 = 按"类"（图纸）造出一个具体的"实例"（真东西）。 代码里表现为 类名(...)：

>  llm = HelloAgentsLLM()    
改行代码实例化的具体实现：
| 步骤 | 说明 |
| --- | --- |
| ① 按图纸造东西 | `HelloAgentsLLM` 是类（图纸），加括号 = 开动机器造一个实例 |
| ② 自动出厂配置 | 造的过程中自动执行 `__init__`（读取 `.env`、创建客户端……） |
| ③ 起个名字 | 造出来的实例存进变量 `llm`，以后用 `llm.think(...)` 按按钮 |

**其他实例化代码：**
```python
llm = HelloAgentsLLM()                          # 造一台"大脑机器"
client = OpenAI(api_key=..., base_url=...)      # 造一个 OpenAI 客户端
tool_executor = ToolExecutor()                  # 造一个工具箱
agent = ReActAgent(llm_client=..., ...)         # 造一个 Agent
tavily = TavilyClient(api_key=...)              # 造一个搜索客户端
```
**如何判断类里要不要传参？**
看这个类的 __init__ 定义：
```python
def __init__(self, model=None, apiKey=None, ...):     # 参数有 =None 默认值
    ...                                               # → 可以不传（HelloAgentsLLM）

def __init__(self, llm_client, tool_executor):        # 参数没有默认值
    ...                                               # → 必须传，否则报错（ReActAgent）
```

**实例化格式**
大写开头的名字 + 括号（HelloAgentsLLM()、OpenAI()）→ 实例化（类名首字母大写是 Python 约定）
小写开头的名字 + 括号（search()、registerTool()）→ 普通函数/方法调用
4. >这行代码什么意思？
 # 定义消息角色的类型，限制其取值
MessageRole = Literal["user", "assistant", "system", "tool"]

来自 OpenAI 的 API 规范。 
| 角色 | 含义 | 你见过的例子 |
| --- | --- | --- |
| `system` | 系统指令：设定身份、规则 | ch4 的 `AGENT_SYSTEM_PROMPT` 说明书 |
| `user` | 用户说的话 | 你的问题 |
| `assistant` | 模型的回复 | 模型输出的 Thought/Action |
| `tool` | 工具返回的结果 | ch7 后面的 FunctionCallAgent 会用 |
举例：
```python
messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': 'Hello!'},
]
```

5. to_dict() 方法是其核心功能之一，负责将内部使用的 Message 对象转换为与 OpenAI API 兼容的字典格式，体现了“对内丰富，对外兼容”的设计原则。

6. Agent抽象基类
```python
"""Agent基类"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from .message import Message
from .llm import HelloAgentsLLM
from .config import Config

class Agent(ABC):
    """Agent基类"""
    
    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self._history: list[Message] = []
    
    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent"""
        pass
    
    def add_message(self, message: Message):
        """添加消息到历史记录"""
        self._history.append(message)
    
    def clear_history(self):
        """清空历史记录"""
        self._history.clear()
    
    def get_history(self) -> list[Message]:
        """获取历史记录"""
        return self._history.copy()
    
    def __str__(self) -> str:
        return f"Agent(name={self.name}, provider={self.llm.provider})"
```
**其构造函数 __init__ 清晰地定义了 Agent 的核心依赖：名称、LLM 实例、系统提示词和配置。 ?**
>名称、LLM 实例、系统提示词和配置这四个是所有agent的“最小公共需求”，放在基类里定义，可以“只写一次，所有子类自动继承”
**该类的设计体现了面向对象中的抽象原则。首先，它通过继承 ABC 被定义为一个不能直接实例化的抽象类**
>*抽象*：只规定必须有什么，不规定 必须怎么做
>“不能直接实例化”：
```python
from abc import ABC, abstractmethod

class Agent(ABC):                    # 继承 ABC = 声明"我是抽象类"
    def __init__(self, name, llm, ...):  # 公共部分照常定义
        ...
    
    @abstractmethod                   # 声明抽象方法
    def run(self):                    # 只有声明，没有实现！
        pass                          # "每个 Agent 必须会 run，但怎么 run 各管各的"
```
# 工具部分-my_calculator_tool.py
```python
def my_calculate(expression: str) -> str:
    """简单的数学计算函数"""
    if not expression.strip():
        return "计算表达式不能为空"

    # 支持的基本运算
    operators = {
        ast.Add: operator.add,      # +
        ast.Sub: operator.sub,      # -
        ast.Mult: operator.mul,     # *
        ast.Div: operator.truediv,  # /
        # ast.Pow: operator.pow       # **
    }

    # 支持的基本函数
    functions = {
        'sqrt': math.sqrt,
        'pi': math.pi,
    }

    try:
        node = ast.parse(expression, mode='eval') #把字符串翻译成一棵"语法树"
        +                    ← 根节点：加法
       / \
   sqrt   *                  ← 左孩子：sqrt 调用；右孩子：乘法
    |    / \
   16   2   3                ← 叶子：数字

        result = _eval_node(node.body, operators, functions)
        return str(result)
    except:
        return "计算失败，请检查表达式格式"
        
def _eval_node(node, operators, functions):
    # print(f"进入调用，节点类型：{type(node).__name__}, 节点内容：{ast.dump(node)}")
    """简化的表达式求值"""
    if isinstance(node, ast.Constant): #返回数字
        return node.value
    elif isinstance(node, ast.BinOp): #左右子树
        left = _eval_node(node.left, operators, functions)
        right = _eval_node(node.right, operators, functions)
        op = operators.get(type(node.op)) #白名单字典有无运算
        return op(left, right)
    elif isinstance(node, ast.Call): #函数
        func_name = node.func.id
        if func_name in functions:
            args = [_eval_node(arg, operators, functions) for arg in node.args]
            return functions[func_name](*args)
    elif isinstance(node, ast.Name):
        if node.id in functions:
            return functions[node.id]
```
具体调用过程：
用户问题: 请帮我计算 sqrt(16) + 2 * 3
进入调用，节点类型：BinOp, 节点内容：BinOp(left=Call(func=Name(id='sqrt', ctx=Load()), args=[Constant(value=16)]), op=Add(), right=BinOp(left=Constant(value=2), op=Mult(), right=Constant(value=3)))
进入调用，节点类型：Call, 节点内容：Call(func=Name(id='sqrt', ctx=Load()), args=[Constant(value=16)])
进入调用，节点类型：Constant, 节点内容：Constant(value=16)
进入调用，节点类型：BinOp, 节点内容：BinOp(left=Constant(value=2), op=Mult(), right=Constant(value=3))
进入调用，节点类型：Constant, 节点内容：Constant(value=2)
进入调用，节点类型：Constant, 节点内容：Constant(value=3)
计算结果: ToolResponse(status=<ToolStatus.SUCCESS: 'success'>, text='10.0', data={'output': '10.0'}, error_info=None, stats={'time_ms': 0}, context={'tool_name': 'my_calculator', 'input': 'sqrt(16) + 2 * 3'})


① 根节点：+ （isinstance 检查从上往下：不是 Constant → 是 BinOp → 命中）
② 先递归左子树：Call(sqrt) 命中 ast.Call 分支
  ③ 再递归它的参数：Constant(16) → 返回 16
  → math.sqrt(16) = 4.0，左子树完成
④ 再递归右子树：BinOp(*) 命中
  ⑤ Constant(2) → 2
  ⑥ Constant(3) → 3
  → 2 * 3 = 6，右子树完成
⑦ 回到根节点：查白名单 operators[ast.Add] → 4.0 + 6 = 10.0
