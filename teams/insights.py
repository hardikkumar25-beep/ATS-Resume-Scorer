from autogen_agentchat.agents import SocietyOfMindAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from agents.improvment_agent import getImprovementAgent
from agents.visualisation_agent import getCodeExecutorAgent
from agents.visualisation_agent import VisualAgent

def getTeamInsights(docker,model):
    improvement_agent=getImprovementAgent(model)
    code_executor_agent=getCodeExecutorAgent(docker)
    data_visual_agent=VisualAgent(model)
    termination_cond=TextMentionTermination('STOP')
    inner_team=RoundRobinGroupChat(participants=[code_executor_agent,data_visual_agent],max_turns=2,termination_condition=termination_cond)
    codeplusvisual_agent = SocietyOfMindAgent("society_of_mind", team=inner_team, model_client=model)

    main_team=RoundRobinGroupChat(participants=[improvement_agent,codeplusvisual_agent],max_turns=2)
    return main_team

