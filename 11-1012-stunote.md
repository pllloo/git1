任务 1（上午）：给 Agent 加记忆模块
材料：code/chapter8/——先浏览 01、02（记忆工具基础操作和架构），重点跑 08_Agent_Tool_Integration.py（记忆工具集成进 Agent 的正主）

步骤：

读 ch8 文档 8.2 节（记忆工具设计，你昨天速读过一半）
跑 08_Agent_Tool_Integration.py（跑之前先看它 import 了什么，依赖不齐就报错发我）
打卡点：跑通后回答两题——
① 这个例子里 Agent 的"记忆"存在哪里？和昨天学的"四类记忆"哪一类对应？
② 怎么验证 Agent 真的"记住"了上一轮对话？输出里找证据
任务 2（下午）：MCP
材料：code/chapter10/ + 读 ch10 文档 MCP 部分

步骤：

速读 ch10 文档（重点 MCP，A2A/ANP 浏览即可）
跑课程自带的天气 MCP 示例：先跑 14_weather_mcp_server.py（本地 MCP 服务器），再跑 14_weather_agent.py（Agent 通过 MCP 调天气）
打卡点：跑通后回答——MCP 解决了什么问题？对比你 ch7 的 tool_registry.execute_tool（工具在 Agent 内部注册），MCP 的工具调用有什么本质不同？（提示：工具在哪运行、怎么被发现）
⚠️ 两个预警
MCP 版本坑（之前预警过）：教程代码可能基于旧版 MCP 规范，若报版本不兼容/缺包，别死磕——把报错发我，我们一起对照最新规范处理
时间预案：若 MCP 卡住超过 45 分钟，按压缩规则执行——降级为"看懂概念 + 跑通 01_TestConnect.py"，把完整 MCP 接 Agent 留到毕业作品里练

---

## 今日实战记录与核心概念（10/12 补课日）

### 一、记忆模块（新版框架 API 最小验证）

课程 ch8 代码全部基于旧框架 API（`MemoryTool(user_id=..., memory_types=...)`），新版框架已重构。用新版 API 跑通了最小验证（my_memory_demo.py）：

```
MemoryStore(path, user_id, task_id)  建记忆库（持久化到 .db 文件）
  → MemoryTool(store)                 建记忆工具
  → add(content, source, kind)        存记忆
  → search(query, limit)              查记忆
```

**三个关键概念**：
1. **持久化**：记忆存进 .db 文件，程序退出不丢——对比 `current_history` 是进程内"草稿纸"
2. **重复记忆问题**：每次 add 都新增记录（内容相同也加）→ 第 N 次运行 search 命中 N 条；新版 API 的 `revise`（修订替代）和 `retract`（撤回）就是为解决它
3. **语义检索**：query="他喜欢什么运动" 能命中"喜欢打篮球"——语义匹配而非关键词（呼应 ch8 的向量化）

### 二、MCP 必掌握概念（⭐ 面试高频）

1. **MCP 是什么**：Model Context Protocol——连接 AI 应用与外部工具/数据的**开放标准协议**（Anthropic 2024 发布，现为业界主流）
2. **解决什么问题**：工具与 Agent **解耦**。传统方式工具写死在 Agent 进程内（同语言、同部署、每 Agent 各写一遍）；MCP 让工具成为**独立服务**（任何语言、任何机器），Agent 通过标准协议远程调用
3. **类比**：ch7 工具 = 自家厨房；MCP = 餐厅（统一标准，任何顾客都能点同一家）；或 USB——工具是 USB 设备，Agent 是电脑
4. **进程**：正在运行的程序，独立内存、互不干扰、可并行。今天的 demo 是双进程结构：客户端进程用 `StdioServerParameters` **启动服务器子进程**，两进程通过 stdio 管道通信
5. **@mcp.tool() 装饰器**：函数定义上方的一行"加工标签"，自动把函数注册为 MCP 工具（函数名=工具名、docstring=说明书）——对比 `register_function` 手动登记三样，装饰器更简洁
6. **版本注意**：mcp 2.x 把 FastMCP 改名 MCPServer；主流教程基于 1.x → `pip install "mcp<2"`

### 三、今日问答记录

- **什么是进程**：正在运行的程序；今天的 demo 是"客户端进程启动服务器子进程"的双进程结构，工具定义在服务器进程，客户端通过管道"打电话"调用
- **代码跑不了怎么办**：①判断类型（环境问题 vs 逻辑问题——今天的 `No module named 'hello_agents.protocols'` 是环境问题，课程 API 已死，不是我的错）②环境问题找替代路径（课程代码失效 → 换官方 mcp SDK）③**目标不变，路径可变**——跑通文件只是手段，学会概念才是目的
- **45 分钟卡点原则**：卡壳前 45 分钟自由尝试（读报错四步法/git diff/改代码试跑），超时二选一——带"试过什么+报错全文"问 Claude，或按压缩规则降级任务

### 四、自我评估

今日双课日超负荷，掌握约 50%——**但拿下的恰好是概念核心**（进程/解耦/装饰器/持久化），代码细节待毕业作品中补强。今日文件：my_memory_demo.py、my_mcp_server.py、my_mcp_client.py（均在课程仓库 chapter8/chapter10 下）。

