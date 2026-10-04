# Day4-Study
## chapter4-code-tools.py
1. try 是什么？怎么用？
try = "试着做一件可能失败的事，失败了有安全网接着"。

类比走钢丝：try 里的代码 = 钢丝上的动作；except = 安全网。没有网（不写 try），失误一次就摔死（程序崩溃）；有网，摔下来被接住，还能继续。

语法结构：


```python
try:
    print("第1步")
    result = 危险操作()
    print("第2步")
    return result
except Exception as e:
    return f"出错了：{e}"
```
三条关键规则：

try 里的代码一旦抛异常，从抛出点直接跳到 except，中间剩余的代码全部跳过
except 后面的 as e：e 就是那个"异常对象"，f"{e}" 能把错误描述变成文字（你之前看到的 KeyError: 'phone' 那类信息）
不抛异常就永远不进 except：try 里全部成功 → except 整段跳过
课程里工具函数的标准用法（背下这个模式，以后写工具就是套模板）：

```python
def 工具(输入):
    try:
        # 所有可能失败的步骤：读配置、联网、解析数据……
        return 成功的结果
    except Exception as e:
        return f"错误描述：{e}"   # 无论发生什么，都返回字符串
```
这个模式的精髓：函数永远不会崩溃，永远返回字符串——成功时返回内容，失败时返回错误描述。主循环拿到的 Observation 永远可用，Agent 永远能继续跑。

另外提醒你注意缩进：try 里的所有语句必须比 try: 多缩进恰好一级（4 个空格），像上面的示例那样整齐。你现在文件里的缩进看着乱（有的 12 格有的 16 格），改的时候用 VSCode 选中代码块按 Shift+Tab / Tab 统一调整，不然会报 IndentationError。
2. 把不安全的程序放进try循环里的原因：接住异常程序，防止整个项目直接崩溃。

---

## 今日其他问答整理（Claude Code 对话补充）

### 1. 异常"向上穿透"是什么意思？

炸弹沿调用链层层上报：底层炸了没人接 → 扔给上一层 → 每层剩余代码全跳过 → 到顶层程序崩溃。Traceback 从下往上读 = 炸弹的路线图。**谁接住（try/except）就停在哪层**，课程选择让工具在最底层接住（转成错误字符串），让主循环省心。实战演示在 03-practice.py（餐厅三场景）。

### 2. 改造代码时的"三问检查法"

复用别人的代码前问三个问题：①这段代码依赖的变量在这里存在吗？②它的业务文案在这里合适吗？③import 了吗？
今天把 ch1 代码改造成 Tavily 搜索工具时踩的五个坑：偷换 query 变量、模块顶层用未定义的 api_key、忘 import、except 残缺、文案没改干净。



### 4. 工具注册与说明书（ToolExecutor）

说明书**唯一的读者是模型**。链路：registerTool 存进工具箱 → getAvailableTools() 拼文字 → 填进提示词 {tools} → 模型读说明书决定何时调用哪个工具。
- 说明书要写三样：**是什么 + 什么时候用 + 调用格式**（如 `CurrentTime[now]`）
- `getTool` 用 `.get()` 查不到返回 None 而不是报错（对比 `[]` 的 KeyError）

### 5. 模板、format 与 __main__

- `{{tool_name}}` 双花括号 = 转义，让提示词里显示字面 `{tool_name}`；单 `{}` 是占位符。填空在 ReAct.py 第 43 行 `.format(...)`
- `if __name__ == '__main__':` 是"只给直接运行开的后门"：被 import 时门内代码不执行。零件文件（tools.py、llm_client.py）的演示代码必须装门，否则 import 时会误触发演示

### 6. 函数签名与参数传递

- **调用者传，函数收**：调用时括号里是"寄出的包裹"，定义时括号里是"收件箱"
- 数量必须匹配、名字随便起（按位置对应）、参数名只在函数体内有效
- **工具统一契约**：执行器永远传一个参数（`tool_function(tool_input)`），所以工具签名必须收一个参数——`def current_time():` 会 TypeError，必须 `def current_time(query):`
- `tool_function` 是**装函数的变量**：函数也是值，可以存字典、赋变量后调用

### 7. 今天的两个实战 bug

**Bug 1：模型反复调用 CurrentTime[] 直到最大步数**
根因链：模型写空括号 → `tool_input=""` → `if not tool_input` 拦截（空字符串是"假值"）→ 反馈"无效格式"太笼统 → 模型不知错在哪 → 死循环。
修复：说明书补调用格式。**深层教训：Agent 开发要预判"模型会怎么调用我的工具"，用说明书引导它。**

**Bug 2：NameError: name 'r' is not defined**
误编辑把一行拆成两行还混入 `r.`。排障神器 **`git diff`**：`-` 是原版、`+` 是改动，意外改动无所遁形。

### 8. 今日成果清单

- [x] 改造搜索工具：SerpApi → Tavily（第一个"个人修改"）
- [x] 跑通 ReAct（见证模型自我纠正：发现结果过时 → 主动换搜索词）
- [x] 添加 CurrentTime 工具全流程：注册 → 说明书 → 模型调用 → Finish
- [x] 验证"没配 Key 程序不崩"（返回错误字符串，Agent 继续跑）
- [ ] 待办：独立任务（无提示给 Agent 加工具）
- [ ] 待办：跑 Plan-and-Solve、Reflection，三范式对比实验

### 9. eval是python的内置计算函数，作为工具调用时不用再import，因为他不是一个包，也无法import到这个模块