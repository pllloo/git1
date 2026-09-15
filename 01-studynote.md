# 学习笔记
## git使用
- git status                       # 确认改了哪些文件
- git diff 学习笔记1.md             # 查看具体改了什么（提交前检查，养成习惯）
- git add 学习笔记1.md
- git commit -m "补充第二章：xxx" #引号修改说明
- git push origin master

## DAY1
 ### 部署环境
 1. 注册Tavily, 负责联网搜索
 2. api写入.env文件
 ### LLM模型调用:test_1_llm.py
 1. 脚本基本框架
 2. 报错：理解.env和os.getenv()的关系：*os.getenv() 不直接读 .env 文件，它只查"环境变量"；是 load_dotenv() 负责把 .env 的内容注入环境变量。你之前说的"从 .env 文件读取"基本对，中间少了个 load_dotenv() 环节*
 3. 学会看报错信息
 4. 为什么要练习运行这个脚本？是在之后的程序或项目中会用到么？这个脚本是输入回答然后得到对应大模型的输出，这跟直接在官网向对应大模型提问有什么区别？--通过API调用，大模型成为一个可以任意组装的零件，反复循环调用。
 ### 旅行助手跑通
 1. thought循环
