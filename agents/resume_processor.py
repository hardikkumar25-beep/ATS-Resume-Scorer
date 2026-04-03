from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()

class ExperienceEntry(BaseModel):
    title: str = Field(description="Job title or role")
    description: str = Field(description="Work done or responsibilities")
    duration: str = Field(description="Duration (e.g., 2025-2026)")

class ProjectEntry(BaseModel):
    name: str = Field(description="Project name")
    tech_stack: List[str] = Field(description="Technologies used in the project")
    description: str = Field(description="What the project does")

class EducationEntry(BaseModel):
    degree: str = Field(description="Degree name (e.g., B.Tech)")
    field: str = Field(description="Field of study (e.g., Computer Science)")
    institution: str = Field(description="College or school name")
    duration: str = Field(description="Years attended")

class Skills(BaseModel):
    technical: List[str] = Field(description="Programming languages and frameworks")
    tools: List[str] = Field(description="Tools and platforms (Docker, AWS, Git, etc.)")
    concepts: List[str] = Field(description="Concepts (ML, NLP, RAG, etc.)")

class ResumeDetails(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    skills: Skills
    experience: List[ExperienceEntry] = Field(description="List of work or project experiences")
    total_experience_years: Optional[float] = Field(description="Total years of experience if available")
    projects: List[ProjectEntry]
    education: List[EducationEntry]
    certifications: List[str] = Field(description="List of certifications. Empty list if none.")
    keywords: List[str] = Field(description="Important keywords extracted from resume")

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