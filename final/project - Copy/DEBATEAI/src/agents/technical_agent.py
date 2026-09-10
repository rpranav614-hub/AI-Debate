from src.agents.base_agent import BaseAgent
from src.models import AgentRole, DecisionInput
from src.agents.prompts import AgentPrompts

class TechnicalAgent(BaseAgent):
    """Agent that analyzes technical feasibility and architecture"""
    
    def __init__(self):
        super().__init__(AgentRole.TECHNICAL)
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.TECHNICAL
    
    def get_user_prompt(self, decision_input: DecisionInput) -> str:
        return f"""
        Please analyze this decision from a technical perspective:
        
        Problem: {decision_input.problem}
        Options: {', '.join(decision_input.options)}
        Criteria: {', '.join(decision_input.criteria) if decision_input.criteria else 'Not specified'}
        Constraints: {', '.join(decision_input.constraints) if decision_input.constraints else 'Not specified'}
        Context: {decision_input.context or 'Not provided'}
        
        Provide your analysis with position, arguments, evidence, assumptions, risks, and confidence.
        """