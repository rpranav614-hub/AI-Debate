from src.agents.base_agent import BaseAgent
from src.models import AgentRole, DecisionInput, AgentOutput
from src.agents.prompts import AgentPrompts
from typing import List

class CriticAgent(BaseAgent):
    """Agent that critiques arguments and identifies weaknesses"""
    
    def __init__(self):
        super().__init__(AgentRole.CRITIC)
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.CRITIC
    
    def get_user_prompt(self, decision_input: DecisionInput) -> str:
        return f"""
        Please critique the arguments for this decision:
        
        Problem: {decision_input.problem}
        Options: {', '.join(decision_input.options)}
        Context: {decision_input.context or 'Not provided'}
        
        Provide your critique with position, arguments, evidence, assumptions, risks, and confidence.
        """
    
    def critique_arguments(self, decision_input: DecisionInput, agent_outputs: List[AgentOutput]) -> str:
        """Critique all agent arguments"""
        critiques = []
        for output in agent_outputs:
            critiques.append(f"""
            Agent: {output.agent_role.value}
            Position: {output.structured_arguments.position}
            Arguments: {', '.join(output.structured_arguments.arguments)}
            Risks: {', '.join(output.structured_arguments.risks)}
            """)
        
        return f"""
        Please critique these arguments:
        
        {chr(10).join(critiques)}
        
        Identify:
        1. Weak arguments
        2. Contradictions
        3. Missing factors
        4. Unsupported assumptions
        """