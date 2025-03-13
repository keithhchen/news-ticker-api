from langchain_core.prompts import ChatPromptTemplate

CONTEXT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个金融分析师，请根据给定的新闻内容，分析以下几个方面：
    1. 新闻主题和核心观点
    2. 涉及的行业和公司
    3. 可能的市场影响
    4. 相关的政策和监管信息
    请用中文回答。
    """),
    ("user", "{input_text}")
])

ANALYST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的金融分析师，请根据给定的新闻内容和初步分析，提供以下深度分析：
    1. 对行业的长期影响
    2. 对相关公司的影响
    3. 投资建议和风险提示
    4. 需要关注的关键指标
    请用中文回答。
    """),
    ("user", """新闻内容：{input_text}
    初步分析：{context_analysis}""")
])

WB_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个金融研报写手，请根据给定的新闻内容和分析，生成一份简短的研报，包含：
    1. 标题
    2. 核心观点
    3. 投资建议
    4. 风险提示
    请用中文回答，使用markdown格式。
    """),
    ("user", """新闻内容：{input_text}
    上下文分析：{context_analysis}
    深度分析：{analyst_analysis}""")
])