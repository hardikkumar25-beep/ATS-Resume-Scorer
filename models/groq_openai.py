from langchain_groq import ChatGroq

def GetGroqModelClient():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0)