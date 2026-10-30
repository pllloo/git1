import os
# from hello_agents import ToolRegistry
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM
import numpy as np
NOTES_DIR = "d:/za9za10/git"          # 笔记目录：定死，不允许读别的目录
from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-zh-v1.5")   # 首次运行会下载模型

NOTE_FILES = [
    # ① 你填空：列出"允许读"的笔记文件名——去 git 文件夹看实际文件名，
    #    抄你的学习笔记 md（提示：挑 8 个以内的笔记，别贪多）
    "01-studynote.md",
    "02-studynote.md",
    "03-studynote.md",
    "04-studynot.md",
    "05-studynote.md",
    "06-1004-stunote.md",
    "07-1005-stunote.md",
    "08-1006-stunote.md",
    "09-1008-stunote.md",
    "10-1009-stunote.md"
]
load_dotenv()    # 自动向上找到仓库根目录的 .env（DeepSeek 配置）
llm = HelloAgentsLLM()

# def create_note_registry():
#     registry = ToolRegistry()
#     registry.register_function(
#         name="read_note",
#         description="""读取学习笔记。可用文件：
# - 01-studynote.md：Git 基本操作
# - 02-studynote.md：旅游助手代码考点（FirstAgentTest.py 对照表）
# - 03-studynote.md：旅游助手主循环（ReAct 循环结构）
# - 04-studynot.md：ch4 工具与 try/except
# - 05-studynote.md：低代码平台
# - 06-1004-stunote.md：LangGraph
# - 07-1005-stunote.md：ch7 框架四层设计
# - 08-1006-stunote.md：ch7 框架代码与双记忆机制
# 调用格式：read_note[文件名]""",
#         func=read_note
#     )
#     return registry
def embed_text(text):
    return list(model.embed([text]))[0]     # 取第一句的向量


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def read_note(filename: str) -> str:
    """按文件名读笔记，返回文件内容"""
    # 安全白名单：文件名不在清单里 → 拒绝
    if filename not in NOTE_FILES:
        return f"错误：'{filename}' 不在笔记清单中"

    # 拼完整路径：目录 + 文件名
    note_path = os.path.join(NOTES_DIR, filename)
    return load_and_chunk(note_path)  # 调用分块函数


def load_and_chunk(note_path):
    """加载笔记文件并按章节分块"""
    try:
        with open(note_path, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"跳过 {note_path}: {e}")   # 错误打印给人看
        return []                          # 返回空列表——类型和正常路径一致

    # 按章节分块：以 "### " 为分隔符
    chunks = text.split("\n##")
    return chunks[1:]


def load_all_notes():
    all_chunks = []
    for filename in NOTE_FILES:
        path = os.path.join(NOTES_DIR, filename)
        chunks = load_and_chunk(path)
        all_chunks.extend(chunks)      # ← 新零件：把 chunks 的元素"铺开"加进总列表
    return all_chunks



def retrieve_chunks(chunks, chunk_vecs,  rewritten_question, top_k=2):
    """检索与问题最相关的笔记块"""
    q_vec = embed_text(rewritten_question)
    pairs = []
    for vec, chunk in zip(chunk_vecs, chunks):   # 拉链配对（上午学的 zip 派上用场）
        sim = cosine_similarity(q_vec, vec)      # 问题向量 vs 每块向量
        pairs.append((sim, chunk))
    pairs.sort(reverse=True)                     # 相似度从高到低（还是那个排序三步法！）
    return pairs[:top_k]

def keyword_score(words, chunk):
    """计算关键词在块中出现的次数"""
    return sum(chunk.count(word) for word in words)
def retrieve_keyword(chunks, words, top_k=2):
    """按关键词检索笔记块"""
    pairs = []
    for chunk in chunks:
        score = keyword_score(words, chunk)
        pairs.append((score, chunk))
    pairs.sort(reverse=True)
    return pairs[:top_k]

def rewrite_query(question):
    """重写问题：根据检索到的笔记块，生成更具体的问题"""
    prompt = f"你是一个查询改写助手。 你的任务是将用户问题改写为适合在学习笔记里搜的短查询，必须换成笔记里可能出现的术语，禁止输出原句，只输出几个词，不要句子，不要解释，不要回答问题。举个例子：git怎么推送→git push 推送。 \n用户问题：{question}\n短查询："
    messages = [{"role": "user", "content": prompt}]
    rewritten_question = llm.invoke(messages).content
    return rewritten_question
def answer_question(question, chunks, chunk_vecs):
    """回答问题：检索笔记块并返回答案"""
    top_chunks = retrieve_chunks(chunks, chunk_vecs, question, top_k=2)
    top_note = "\n".join([chunk for score, chunk in top_chunks])
    prompt = f"你是一个学习笔记问答助手。请仅根据下面的笔记片段回答用户问题,如果片段中没有相关信息，请如实说明'笔记中没有相关内容'。根据以下笔记内容回答问题：\n{top_note}\n问题：{question}\n"
    messages = [{"role": "user", "content": prompt}]

    answer = llm.invoke(messages).content     # invoke 返回 LLMResponse，取 .content（版本适配课的肌肉记忆）
    return answer


# 自测：直接运行本文件时执行
if __name__ == "__main__":
    chunks =load_all_notes()
    chunk_vecs = [embed_text(chunk) for chunk in chunks]
    question = "双记忆机制是什么"
    words = ["前缀", "原始字符串"]

    print("=== 语义 ===")
    rewritten_question = rewrite_query(question)
    print(f"原问题：{question} → 重写后：{rewritten_question}")
    for score, chunk in retrieve_chunks(chunks, chunk_vecs, rewritten_question, top_k=2):
        print(f"[得分 {score}] {chunk[:80]}")

    print("=== 关键词 ===")
    for score, chunk in retrieve_keyword(chunks, words, top_k=2):
        print(f"[得分 {score}] {chunk[:80]}")

# if __name__ == "__main__":
#     question = "总结全部笔记"
#     print(rewrite_query(question))
