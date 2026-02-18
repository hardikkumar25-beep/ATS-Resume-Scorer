from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from uuid import uuid4
from langchain_groq import ChatGroq
import os
from models.groq_openai import GetGroqModelClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from dotenv import load_dotenv
load_dotenv()

class ResumeDetails(BaseModel):
    name: str = Field(description="Full name of the candidate. Use 'Not Found' if missing.")
    email: str = Field(description="Email address. Use 'Not Found' if missing.")
    phone: str = Field(description="Phone number. Use 'Not Found' if missing.")
    experience: str = Field(description="Work experience. Use 'Not Found' if missing.")
    skills: str = Field(description="Skills. Use 'Not Found' if missing.")
    education: str = Field(description="Education details. Use 'Not Found' if missing.")
    certifications: str = Field(description="Certifications. Use 'Not Found' if missing.")
    projects: str = Field(description="Projects. Use 'Not Found' if missing.")

def load_resume(file_path: str):
    if file_path.endswith(".pdf"):
        return PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        return Docx2txtLoader(file_path)
    elif file_path.endswith(".txt"):
        return TextLoader(file_path)
    else:
        raise ValueError("Unsupported resume format")

def process_resume(llm,resume_path: str) -> dict:
    """Extract structured data from resume"""
    
    loader = load_resume(resume_path)
    docs = loader.load()
    
    full_text = "\n\n".join([doc.page_content for doc in docs])
    
    output_parser = JsonOutputParser(pydantic_object=ResumeDetails)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract resume details..."),
        ("human", "Resume text:\n\n{resume_text}\n\n{format_instructions}")
    ])
    
    chain = prompt | llm | output_parser
    
    return chain.invoke({
        "resume_text": full_text,
        "format_instructions": output_parser.get_format_instructions()
    })

# resume_extractor_tool = FunctionTool(
#     process_resume,
#     description="Extracts structured information from a resume file and returns JSON with candidate details"
# )
# SYSTEM_MESSAGE = """You are a Resume Processor Agent.

# Your job is to help extract resume information using your resume extraction tool.

# When asked to process a resume:
# 1. Use the extract_resume_with_langchain tool with the file path
# 2. The tool will return structured JSON data
# 3. Analyze the returned data for completeness
# 4. Report the extracted information to the user

# If the tool returns an error, explain what went wrong and suggest fixes.
# """
# def getResumeAgent(model):
#     resume_agent=AssistantAgent(
#         name="ResumeProcessor",
#         model_client=model,
#         tools=[resume_extractor_tool],
#         description="Processes resumes and extracts structured candidate information",
#         system_message=SYSTEM_MESSAGE,
#         reflect_on_tool_use=True)
#     return resume_agent
    

