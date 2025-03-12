from langchain_core.prompts import ChatPromptTemplate

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a text analyzer. Analyze the given text and provide key points."),
    ("user", "{input_text}")
])

SENTIMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a sentiment analyzer. Determine the sentiment of the text."),
    ("user", "{input_text}")
])

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a summarizer. Create a concise summary."),
    ("user", "{input_text}")
])

FINAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a report compiler. Combine the analysis, sentiment, and summary into a coherent report."),
    ("user", """Please compile a report using:
    Analysis: {analysis}
    Sentiment: {sentiment}
    Summary: {summary}""")
]) 