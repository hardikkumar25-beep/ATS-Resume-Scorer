import asyncio
from pyexpat import model
from config.docker import getDocker, startDocker, stopDocker
from models.openrouter import getOpenRouterModel
from models.groq_openai import GetGroqModelClient
from agents.resume_processor import process_resume
from agents.jd_analysis import getJDAnalystAgent
from agents.ats_scorer import getATS_scorerAgent
from agents.improvment_agent import getImprovementAgent
from agents.visualisation_agent import getCodeExecutorAgent
from agents.visualisation_agent import VisualAgent
from teams.insights import getTeamInsights


def extract_message_by_source(response, source_name: str):
    """
    Safely extract the latest message from a specific agent source.
    """
    for message in reversed(response.messages):
        if getattr(message, "source", None) == source_name:
            return message.content
    raise ValueError(f"No message found from source: {source_name}")

async def main():
    model=getOpenRouterModel()
    llm=GetGroqModelClient()
    docker=getDocker()
    resume_path=r"C:\Users\hardi\OneDrive\Desktop\ats_resume_scorer\hardik_resume.pdf"
    jd_text="""Job Title: AI / Machine Learning Engineer (Entry-Level)
Location: Remote / Bangalore
Experience Required: 0–2 Years

Role Overview
We are hiring an entry-level AI / Machine Learning Engineer to work on intelligent systems involving data processing, model training, and AI-powered applications. The role focuses on practical implementation of ML and NLP solutions rather than pure research.

Key Responsibilities
Build and deploy machine learning models using Python
Work on NLP tasks such as text classification and information extraction
Assist in developing AI pipelines for document processing and scoring systems
Integrate ML models with backend services and APIs
Perform data cleaning, preprocessing, and feature engineering
Required Skills
Proficiency in Python
Understanding of machine learning fundamentals
Experience with scikit-learn, TensorFlow, or PyTorch
Knowledge of NLP concepts and transformer-based models
Familiarity with vector databases or embeddings (FAISS, Pinecone, etc.)

Preferred Qualifications
Experience working with LangChain, RAG pipelines, or LLMs
Exposure to resume parsing or ATS systems
Knowledge of SQL or NoSQL databases
Familiarity with Docker or basic cloud deployment

Education
B.Tech / B.E. in Computer Science, AI, Data Science, or related fields

Additional Notes
This role is suitable for fresh graduates or final-year students with strong project experience in AI and machine learning."""
    try:
        print("Processing Resume...")
        resume_details= process_resume(llm,resume_path)
        if not resume_details:
            raise ValueError("Resume processing failed.")

        print("Analyzing Job Description...")
        jd_agent=getJDAnalystAgent(model)
        jd_analysis= await jd_agent.run(task=jd_text)
        if not jd_analysis:
            raise ValueError("JD analysis failed.")
        jd_json=extract_message_by_source(jd_analysis,"JDAnalystAgent")

        print("Ats Scoring Resume...")
        ats_scorer_agent=getATS_scorerAgent(model)
        task=f"""
            "resume_details": {resume_details},
            "jd_analysis": {jd_json}
        """
        ats_score= await ats_scorer_agent.run(task =task)
        ats_json=extract_message_by_source(ats_score,"ATS_Scorer")
        if not ats_score:
            raise ValueError("ATS scoring failed.")
        print("\n--- ATS SCORE OUTPUT ---\n")
        print(ats_json)

        print("Giving improvments...")
        imrpovement_agent=getImprovementAgent(model)
        imp_res=await imrpovement_agent.run(task=ats_json)
        impro_details=extract_message_by_source(imp_res,"ImprovementAgent")
        print("\n--- IMPROVEMENT SUGGESTIONS ---\n")
        print(impro_details)
    #     await startDocker(docker)
    #     insights_team = getTeamInsights(docker, model)

    #     async for message in insights_team.run_stream(task=ats_json):
    #         print(message)
    except Exception as e:
        print(f"\nError occurred: {e}")

    # finally:
    #     await stopDocker(docker)


if __name__ == "__main__":
    asyncio.run(main())




     


