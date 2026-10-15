# MCP 客户端代码逐行解析（my_mcp_client.py）

> 今日晨课复习：把昨天写的 MCP 最小示例客户端逐行吃透。

## 一、逐行注释版

```python
import asyncio                                    # 异步编程支持（async/await 用）
import os                                         # 路径处理
import sys                                        # sys.executable：当前 python 解释器路径

from mcp import ClientSession, StdioServerParameters   # 会话类 + 服务器启动参数类
from mcp.client.stdio import stdio_client         # stdio 传输通道（管道）


async def main():                                 # 异步函数：可以"暂停等待"的函数
    # 1. 描述要连接的服务器：用 python 启动 my_mcp_server.py（stdio 管道）
    server_dir = os.path.dirname(os.path.abspath(__file__))  # 取本脚本所在目录的绝对路径
    server = StdioServerParameters(               # 实例化"服务器名片"（描述怎么拉起服务器）
        command=sys.executable,                   # 用当前 venv 的 python（保证 mcp 包可用）
        args=["my_mcp_server.py"],                # 命令行参数：运行服务器脚本
        cwd=server_dir,                           # 子进程工作目录（相对路径的解析基准）
    )

    # 2. 建立连接（服务器作为子进程被启动）
    async with stdio_client(server) as (read, write):   # 启动子进程，拿到管道读写两端；用完自动断开
        async with ClientSession(read, write) as session:  # 会话层：按 MCP 协议收发消息
            await session.initialize()            # 握手：互报协议版本与能力

            # 3. 调用远程工具：查北京天气
            result = await session.call_tool("get_weather", {"city": "北京"})  # 调工具：工具名+参数字典
            print("【北京】", result.content[0].text)   # 结果取法：content 块列表→第0块→.text 文本

            # 4. 再查一个不存在的城市（负面测试）
            result2 = await session.call_tool("get_weather", {"city": "火星"})  # 故意错输入看容错
            print("【火星】", result2.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())                           # 启动异步函数的标准写法
```

## 二、重要概念补充

**1. async / await（异步）**：
- 普通函数遇到"等待"原地干等（打电话，占线）；异步函数遇到 `await` 让出位置干别的（微信，回复到了再处理）
- `await` 出现的行 = 暂停点。本文三处 await 分别等：**握手确认、工具执行结果、第二次工具执行结果**
- 服务器崩了时 await 等来的是异常：`MCPError: Connection closed`（亲历）

**2. async with = 异步版"用完自动关门"**：普通 `with open(...)` 自动关文件；`async with stdio_client(...)` 自动挂断连接、关闭子进程。

**3. 为什么 `command=sys.executable` 而不是 `"python"`**：`sys.executable` 是当前 venv 的 python 完整路径——mcp 包装在 venv 里，用系统 python 会 ModuleNotFoundError。

**4. 为什么需要 `cwd=server_dir`**：相对路径 `my_mcp_server.py` 以子进程的工作目录为基准解析。不写 cwd 就相对于"启动客户端时的目录"——恰好在那目录下跑没事，换个目录就 FileNotFoundError。写死 cwd = 路径稳健。

**5. 为什么结果是 `result.content[0].text` 而不是 `result`**：MCP 工具的返回是**消息块列表**（可能多块、多种类型：文本/图片/文件……），统一设计成"块列表"以兼容各种内容。取文本要逐层钻：`.content`（列表）→ `[0]`（第一块）→ `.text`（文本）。——"对内丰富，对外兼容"的又一体现。

**6. StdioServerParameters 三个参数 = 启动程序三要素**：command（用什么程序/骑手）、args（跑什么/送什么菜）、cwd（在哪跑/哪个店取餐）。

## 三、今日问答记录

- Q：`command` 换成 `"python"` 会怎样？→ A：ModuleNotFoundError（mcp 在 venv 里，系统 python 没有）
- Q：删掉 `cwd=server_dir` 会怎样？→ A：相对路径改为相对于"启动客户端时的目录"解析——在正确目录下跑碰巧没事，换个目录就找不到文件
- Q：`await session.initialize()` 等什么？→ A：客户端与服务器的握手过程（互报协议版本与能力）
- Q：`await session.call_tool(...)` 等什么？→ A：等服务器执行工具并返回结果；服务器崩了则抛 `MCPError: Connection closed`
- Q：`result.content[0].text` 为什么不能写成 `result`？→ A：result 是 CallToolResult 对象，content 是消息块列表（可多块多类型），要逐层取到文本

---

## 四、知识点：返回值 vs 变量名（局部变量作用域）

**核心规则一句话：函数里的变量是"局部变量"——函数结束，变量名销毁，只有 return 的"值"能出来。**

**房间类比**：

```
load_and_chunk 房间：
    chunks = [...]        ← 房间里的箱子，名叫 chunks
    return chunks[1:]     ← 把箱子里的【东西】递出门
    # 函数结束关门——"chunks"这个名字随房间一起消失

__main__ 房间（客厅）：
    print(read_note(...)) ← 只把递出来的【东西】打印看一眼，没放进自己的箱子
    len(chunks)           ← 💣 客厅里没有叫 chunks 的箱子！名字不存在
```

- 递出门的是"东西"（列表值），不是"箱子"（变量名 chunks）
- 客厅要用，必须自己准备箱子接住：`chunks = load_and_chunk(...)`——这个 chunks 是客厅自己的箱子，和厨房那个**碰巧同名，但不是同一个**
- 配套规则：return 把值送回调用处，调用处要用 `变量 = 函数(...)` 接住，值才归你管

**30 秒验证**：

```python
def 厨房():
    dish = "红烧肉"     # 厨房房间里的名字
    return dish          # 递出门的是"红烧肉"这个值

菜 = 厨房()              # 客厅用自己的名字"菜"接住
print(菜)               # 红烧肉 ✓
print(dish)             # NameError: name 'dish' is not defined ← 厨房的名字客厅看不见
```

**踩坑记录（v1 步骤 1）**：自测时 `print(read_note(...))` 只打印返回值没接住，随后 `len(chunks)` 报 NameError——值出来了，名字没出来。

---

## 五、知识点：顶层放"机器"，函数放"材料"

**判断标准就一个问题：这个值在程序运行期间变不变？**

| 类型 | 例子 | 放哪 |
|---|---|---|
| 不变（机器/配置） | `llm` 客户端、`load_dotenv()`、`NOTES_DIR`、`NOTE_FILES` | **顶层**，创建一次 |
| 每次变（输入/结果） | `prompt`、`messages`、检索结果 `top_note` | **函数内**，每次现拼 |

**原因**：
- 机器（llm 客户端）创建有开销，造一次用多次——"机器造一次，按钮按多次"
- prompt/messages 依赖每次调用才有的变量（question、检索块），放顶层时这些变量还不存在

**踩坑记录（v1 重构）**：把 prompt/messages 提到顶层 → 引用的 `top_note`、`question` 在顶层不存在 → `NameError: name 'top_note' is not defined`。正确姿势：llm 上顶层，prompt/messages 留在 answer_question 里每次现拼。

---

## 六、毕业作品 v1：知识库问答 Agent（简版 RAG）

**三步流水线**：

```
① load_all_notes()            数据层：遍历 NOTE_FILES → 逐个切块 → extend 合并成总块列表（22 块）
② retrieve_chunks(chunks, q)  检索层：关键词切分 → 逐块计命中分 → 排序取 top 2
③ answer_question(q, chunks)  问答层：检索 → 拼 prompt（角色+片段+问题+反幻觉约束）→ LLM 回答
```

### 关键认知 1：候选池 = 答案上限

检索只能从"你喂给它的块"里选——**喂进去什么，最多就答什么**。只加载一个文件，跨文件的问题永远命中不了。所以知识库必须 `load_all_notes()` 自动扫全部笔记，而不是让调用者指定文件（用户问问题时根本不知道答案在哪篇）。

### 关键认知 2：评分三步法（通用"排序取 top"模式）

```python
# ① 双重循环计命中数
for chunk in chunks:
    score = 0
    for kw in keywords:
        if kw in chunk:
            score += 1
# ② (分数, 块) 元组配对——分数在前，排序才按分数
    pairs.append((score, chunk))
# ③ 排序取前 N
pairs.sort(reverse=True)
return pairs[:top_k]
```

踩坑：元组顺序写成 (块, 分数) → 排序按文本排不按分数；没排序直接切片 → 输出"碰巧对"纯属运气，换输入就崩。

### 关键认知 3：反幻觉 prompt 的实战验证

prompt 里写"仅根据片段回答，没有就明说"——实测效果：

> 问"LangChain 和 LangGraph 的区别"（笔记里没有对比内容）→ 模型答："笔记中没有相关内容。笔记中分别记录了……但没有对两者进行对比或说明它们之间的区别。"

**模型诚实说"没有"，而不是编造对比**——这是"约束幻觉"的第一手证据，面试讲项目时的黄金素材：不是"我加了防幻觉提示词"，而是"我实测了它真的会拒绝编造"。

## 任务
今日任务卡（10/13）：毕业作品 v1 起手 ⭐
目标：搭出"个人知识库问答 Agent"最小可跑版（v1 只求跑通，不求完美）。

v1 的最小定义（三件事串起来就够）：

数据层：把你的笔记 md 读进来、切成小块（chunk）
检索层：问题来了，找出最相关的笔记块（v1 可用最简方案）
问答层：检索结果拼进 prompt → LLM 回答
你已有的积木（都在你手上）：

read_note（读文件）→ 数据层雏形
ch8 学的向量检索概念 → 检索层（v1 可先用关键词匹配顶上，向量化明天加）
HelloAgentsLLM / ch7 的 Agent → 问答层
今天打卡点：一个能回答"我学过哪些关于 XXX 的内容？"的脚本，跑通一个真实问题。

两个建议：① 新建项目文件夹 d:/za9za10/hello-agents/my-projects/kb-qa/（课程代码和你的作品分开）② 今晚顺带把周复盘补了（三格：打卡数/卡住的点/下周调整）。

先想想 v1 的架构怎么搭（不用急着写代码，把你的设计思路说给我听，我批改后你再动手）。