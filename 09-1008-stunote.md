 # my_note_test my_note_tool;建立一个笔记读取工具

- 目标：新建 my_note_tool.py（课程仓库的 my_ 前缀 = "我的扩展"，和课程文件一个惯例），实现"按文件名读笔记"的工具，注册进 ReActAgent，跑通一个真实问答。


额外检验（安全白名单是否生效）：试试让 Agent 读一个清单外的文件（或你自己直接调用 read_note("../.env")），确认它被拒绝。
> 相关工作：
1. 建立一个笔记读取工具 my_note_tool
    - 主要框架：
    a. 定死笔记目录并列出允许读的笔记文件名
    b. 建立工具注册表 ，主要包含：1.工具名；2.工具描述；3.工具调用函数名
    c. 建立详细的工具调用函数
    d. 自测模块
2. 建立工具测试，测试文件内容不多，主体就是测试函数，作用就是将已建立的笔记读取工具放进注册表和调用已有的agent（课程中给出的my_react_agent）。

## Question

 1. 为什么 test_react_agent 有 try/except 注册块，你的不需要？
看 test_react_agent.py 输出里有一行——⚠️ 搜索工具未找到，跳过注册。它的 try/except 是在防御**"可选工具可能不存在"**：从框架里 import 工具，万一这个版本没有，就打印警告跳过去，不让整个测试崩掉。

而你的 create_note_registry() 是你自己写的、必然存在的函数——没有"可能导入失败"的风险，所以 try/except 是多余的防御。
 2.  模型 3 次调用都"解析失败"，框架熔断了
 原因：已在my_note_tool中注册了工具，对笔记读取工具进行了命名和详细描述，但是在my_note_test的测试文件中，我照搬了test_react_agent的计算机工具的注册块
 ```python
 # 注册读取笔记的工具
    try:
        from my_note_tool import read_note
        tool_registry.register_function(
            name="read_note",
            description="读取学习笔记。调用格式：read_note[文件名]",
            func=read_note
        )
        print("✅ 读取笔记工具注册成功")
    except ImportError:
        print("⚠️ 读取笔记工具未找到，跳过注册")
```
一方面是工具是自己创建的，一定能查找到，因此不同于python内置的calculate工具需要检测模块；另一方面是在这部分中又对工具进行了重新注册，而且模板没有修改，出事模板没有添加文件菜单和主题，把之前详细的工具描述覆盖掉了，因此模型收到问题后，无法找到对应的文件。踩坑过程：简版描述（无菜单）覆盖了完整版 → 模型瞎猜文件名 → 连续失败 → 框架熔断。注册顺序会覆盖，最后一次注册生效。
3. 为什么要再描述中建立一个详细目录？每个文件为什么要标明主题？
```python
没有主题的菜单:                   有主题的菜单:
- 01-studynote.md                - 01-studynote.md：Git 笔记
- 02-studynote.md                - 02-studynote.md：正则表达式笔记
- 03-studynote.md                - 03-studynote.md：xxx 笔记
- ...                            - ...
  ↓                                ↓
模型：我哪知道正则写在哪份里？    模型：正则 → 02-studynote.md！
要么全读一遍（浪费）             直接调 read_note[02-studynote.md]
要么瞎猜（读错文件）             一步到位
```
菜单 = 给模型的"文件索引"——每个文件名配一个内容概括，模型才能按问题选文件。你打开的 02-studynote.md，标题下写的是 FirstAgentTest 主循环和正则，那它的主题就概括成"FirstAgentTest 主循环与正则笔记"。
4. 白名单的安全意义
    "定死目录+白名单"不只是功能设计，是安全设计：防止模型（或使用者）读取 .env、../.env 等任意文件。配套的还有负面测试（自测里故意攻击自己的两行）——防御代码必须主动攻击自己验证防线有效

4. 踩坑记录（可加一节"踩坑"）

   - create_note_registry() 写在 __main__ 门外 → 每次 import 都注册一次（重复注册 ×2）
   - DEBUG print 加错位置 → messages 未定义（先使用后定义）
   - 新发现的框架特性：Circuit Breaker 熔断器（工具连续失败 3 次自动停止调用）