# Hello-Agents 学习框架(8 周版)

> 基于 [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) 定制
> 学习者画像:Agent 新手、Windows 11、国内网络
> 节奏:每周 6~10 小时,可弹性伸缩

---

## 学习资源(国内友好)

| 资源 | 地址 |
|------|------|
| 在线阅读(国内加速) | https://hello-agents.datawhale.cc |
| PDF 下载(国内) | https://www.datawhale.cn/learn/summary/239 |
| GitHub 仓库 | https://github.com/datawhalechina/hello-agents (clone 需走代理) |
| 环境配置教程 | Extra07-环境配置.md(仓库内 Extra-Chapter 目录) |
| 常见问题 | Extra04-DatawhaleFAQ.md |

**API 推荐**(课程需要调 LLM):
- DeepSeek:便宜、OpenAI 兼容,新用户送额度 → https://platform.deepseek.com
- 通义千问(DashScope):新用户有免费额度 → https://dashscope.aliyun.com

**pip 加速**(Windows 命令):
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <包名>
```

---

## 学习总路线

```
准备期 → 理论基础(ch1-3)→ 核心实战(ch4-7)→ 高级扩展(ch8-12)→ 综合案例(ch13-15)→ 毕业设计(ch16)
```

---

## 第 0 周:准备期(开工前)

**目标:把路铺平,不把时间浪费在环境上**

- [ ] Python 自检:能写函数、类、字典、循环;会 pip 装包;会用 venv 虚拟环境
  - 不过关 → 先花 3~5 天过一遍 [Python 官方教程前 8 章](https://docs.python.org/zh-cn/3/tutorial/) 或 B 站任意入门视频
- [ ] 安装 Python 3.10+ 和 VS Code
- [ ] 注册 DeepSeek / 通义千问,拿到 API Key(存好,不要提交到 git)
- [ ] 跑通最小验证:一个 Python 脚本调用 LLM API 并收到回复
- [ ] 按 Extra07 配置课程环境
- [ ] clone 课程仓库:
  ```bash
  git -c http.proxy=http://127.0.0.1:7890 -c https.proxy=http://127.0.0.1:7890 clone https://github.com/datawhalechina/hello-agents.git
  ```

✅ **检验标准:能用 10 行代码让 LLM 回复你一句话。**

---

## 第 1 周:理论基础(ch1-3)

**目标:建立概念地图,不求全懂,只求有框架**

| 章节 | 内容 | 学习要点 |
|------|------|----------|
| ch1 初识智能体 | 定义、类型、范式 | 能用自己的话解释"Agent 和普通聊天机器人差在哪" |
| ch2 发展史 | 符号主义 → LLM 驱动 | 了解即可,快速过 |
| ch3 LLM 基础 | Transformer、提示工程、局限 | 重点理解"模型为什么会犯错",这是 Agent 设计的前提 |

**本周围绕一个核心问题学习:Agent 的本质是什么?(= LLM + 循环 + 工具 + 记忆)**

✅ **检验标准:写一篇 500 字笔记,用自己的话讲清 Agent 四大组件。**

---

## 第 2 周:经典范式(ch4)⭐ 全课程最重要一章

**目标:手写 ReAct,这是理解一切 Agent 框架的钥匙**

- [ ] 跟教程手写 ReAct(推理→行动→观察循环)
- [ ] 手写 Plan-and-Solve
- [ ] 手写 Reflection(自我反思)
- [ ] 三个范式都用你自己的 API Key 真正跑起来
- [ ] 做对比实验:同一个任务,三种范式表现有何不同?

✅ **检验标准:能不看教程,自己从零写出一个可运行的 ReAct 循环。**

> 卡住了很正常,这一周值得花 1.5 倍时间。卡壳时向 Claude Code 提问(用 @hello-agents 引用仓库文件)。

---

## 第 3 周:低代码平台 + 主流框架(ch5-6)

**目标:体验"用轮子",建立对工具生态的全局观**

- [ ] ch5:注册 Coze(扣子)/Dify,各搭一个简单 Agent,感受低代码的边界(什么事它做不了?)
- [ ] ch6:重点学 **LangGraph**(目前最主流),跑通教程示例
- [ ] AutoGen、AgentScope 浏览了解即可,不必深挖

✅ **检验标准:能在 Dify 上搭出一个带工具的 Agent,并说清它和手写 ReAct 的对应关系。**

---

## 第 4 周:从零构建自己的框架(ch7)

**目标:造轮子——把前两周学的融会贯通**

- [ ] 跟教程用 OpenAI 原生 API 构建 HelloAgents 框架
- [ ] 理解框架分层:模型层 / 工具层 / 循环控制层 / 记忆层
- [ ] 给自己定一个改造任务(如:加一个自己的工具、换一种输出格式)

✅ **检验标准:用你的框架实现第 2 周的 ReAct 任务,代码结构比之前更清晰。**

> 完成此章 = 你已经超过大多数"只会用框架"的人。

---

## 第 5 周:记忆与检索 + 上下文工程(ch8-9)

**目标:让 Agent 从"金鱼记忆"变成"有记性"**

- [ ] ch8:记忆系统(短期/长期)、RAG、向量存储
- [ ] ch9:上下文工程——如何设计 prompt、何时压缩上下文
- [ ] 实战:给你第 4 周的框架加上记忆模块

✅ **检验标准:你的 Agent 能记住上一次对话说过的话。**

---

## 第 6 周:通信协议 + 评估(ch10、ch12)

**目标:理解 Agent 如何"接轨世界"**

- [ ] ch10:**MCP 是重点**(当前行业标准),看懂并自己接一个 MCP 服务器;A2A、ANP 了解即可
- [ ] ch12:评估指标、基准测试,学会给自己的 Agent 打分
- [ ] ch11(Agentic-RL)涉及模型训练,**可选学**,时间不够就跳过

✅ **检验标准:你的框架能通过 MCP 调用一个外部工具(如文件系统/搜索)。**

---

## 第 7 周:综合案例二选一(ch13 或 ch14)

**目标:完整走一遍"设计→实现→打磨"的工程流程**

- [ ] 方案 A:ch13 智能旅行助手(MCP + 多智能体协作,贴近生活)
- [ ] 方案 B:ch14 复现 DeepResearch Agent(更硬核,适合想深入了解研究型 Agent)
- [ ] ch15 赛博小镇(Agent 模拟社会)当娱乐项目看,感兴趣再玩

✅ **检验标准:项目能跑通,并给自己写一份复盘(踩了哪些坑、哪些设计可以更好)。**

---

## 第 8 周:毕业设计(ch16)

**目标:做出一个属于你自己的作品**

选题建议(从易到难):
1. 个人知识库问答 Agent(你学过的笔记 → RAG)
2. 微信/飞书机器人助手(接通知、查天气、定时提醒)
3. 把第 7 周案例改造成自己的场景(如:求职简历优化 Agent、食谱 Agent)
4. 好玩向:赛博小镇式小游戏、会自己写日报的 Agent

✅ **检验标准:项目发布到 GitHub(记得用你的代理配置),README 写清楚功能和使用方法。**

---

## 学习方法论(贯穿全程)

1. **输出倒逼输入**:每周写一篇学习笔记(发 CSDN/掘金/个人博客),讲不清楚 = 没学会
2. **跑通比看懂重要**:所有代码必须亲手运行,把报错当作学习机会
3. **善用 Claude Code**:遇到不懂的,直接在仓库目录里 @ 引用章节文件提问
4. **80/20 原则**:ch1-3 和 ch5 快速过,ch4、ch7 死磕,高级篇按兴趣取舍
5. **遇到大坑先查** Extra09(踩坑经验)和 Extra04(FAQ)
6. **加入社区**:Datawhale 有学习群,有问题别憋着

## 进阶弹药库(学完后)

- Extra 系列:面试题(Extra01)、Agent Skills(Extra05)、GUI/Web Agent(Extra06/11)、自进化(Extra10)
- [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code):把你天天用的 Claude Code 拆开看
- [huggingface/agents-course](https://huggingface.co/learn/agents-course):体系化进阶
