import asyncio
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import SocietyOfMindAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from agents.resume_processor import getResumeAgent
from agents.jd_analysis import getJDAnalystAgent
from agents.ats_scorer import getATS_scorerAgent

def getTeamA(model):
    resume_agent=getResumeAgent(model)
    ats_scorer_Agent=getATS_scorerAgent(model)
    jd_analysis_agent=getJDAnalystAgent(model)

    inner_team=RoundRobinGroupChat(participants=[resume_agent,jd_analysis_agent],max_turns=2)
    data_process_agent = SocietyOfMindAgent("society_of_mind", team=inner_team, model_client=model)

    main_team=RoundRobinGroupChat(participants=[data_process_agent,ats_scorer_Agent],max_turns=2)
    return main_team


