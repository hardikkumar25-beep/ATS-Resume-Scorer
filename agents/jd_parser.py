from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()

class JDDetails(BaseModel):
    job_title: str = Field(description="Job title")
    preferred_skills: List[str] = Field(description="Preferred skills. Use 'Not Found' if missing.")
    required_skills: List[str] = Field(description="Required skills. Use 'Not Found' if missing.")
    experience_years: int = Field(description="Work experience. Use 'Not Found' if missing.")
    education: str = Field(description="Education details. Use 'Not Found' if missing.")
    keywords: List[str] = Field(description="Important keywords extracted from resume")


def process_jd(llm,jd: str) -> dict:
    """Extract structured data from job description"""
    jd_text = jd
    output_parser = JsonOutputParser(pydantic_object=JDDetails)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract job description details..."),
        ("human", "Job description text:\n\n{jd_text}\n\n{format_instructions}")
    ])
    
    chain = prompt | llm | output_parser
    
    return chain.invoke({
        "jd_text": jd_text,
        "format_instructions": output_parser.get_format_instructions()
    })