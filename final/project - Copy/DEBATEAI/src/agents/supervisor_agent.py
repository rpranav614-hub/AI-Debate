from src.agents.base_agent import BaseAgent
from src.models import AgentRole, DecisionInput
from src.agents.prompts import AgentPrompts

class SupervisorAgent(BaseAgent):
    """Agent that coordinates the debate workflow"""
    
    def __init__(self):
        super().__init__(AgentRole.SUPERVISOR)
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.SUPERVISOR
    
    def get_user_prompt(self, decision_input: DecisionInput) -> str:
        return f"""
        Please analyze this decision and identify which perspectives are needed:
        
        Problem: {decision_input.problem}
        Options: {', '.join(decision_input.options)}
        Criteria: {', '.join(decision_input.criteria) if decision_input.criteria else 'Not specified'}
        Constraints: {', '.join(decision_input.constraints) if decision_input.constraints else 'Not specified'}
        Context: {decision_input.context or 'Not provided'}
        
        Identify the key perspectives needed for this decision and provide your analysis.
        """