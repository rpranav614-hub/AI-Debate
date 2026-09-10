from src.agents.base_agent import BaseAgent
from src.models import AgentRole, DecisionInput
from src.agents.prompts import AgentPrompts

class SecurityAgent(BaseAgent):
    """Agent that evaluates security implications"""
    
    def __init__(self):
        super().__init__(AgentRole.SECURITY)
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.SECURITY
    
    def get_user_prompt(self, decision_input: DecisionInput) -> str:
        return f"""
        Please analyze this decision from a security perspective:
        
        Problem: {decision_input.problem}
        Options: {', '.join(decision_input.options)}
        Criteria: {', '.join(decision_input.criteria) if decision_input.criteria else 'Not specified'}
        Constraints: {', '.join(decision_input.constraints) if decision_input.constraints else 'Not specified'}
        Context: {decision_input.context or 'Not provided'}
        
        Provide your analysis with position, arguments, evidence, assumptions, risks, and confidence.
        """