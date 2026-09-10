from src.agents.base_agent import BaseAgent
from src.models import AgentRole, DecisionInput, AgentOutput
from src.agents.prompts import AgentPrompts
from typing import List

class DecisionAgent(BaseAgent):
    """Agent that synthesizes final recommendation"""
    
    def __init__(self):
        super().__init__(AgentRole.DECISION)
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.DECISION
    
    def get_user_prompt(self, decision_input: DecisionInput) -> str:
        return f"""
        Please make a final decision recommendation:
        
        Problem: {decision_input.problem}
        Options: {', '.join(decision_input.options)}
        Criteria: {', '.join(decision_input.criteria) if decision_input.criteria else 'Not specified'}
        Constraints: {', '.join(decision_input.constraints) if decision_input.constraints else 'Not specified'}
        Context: {decision_input.context or 'Not provided'}
        
        Provide your final recommendation with position, arguments, evidence, assumptions, risks, and confidence.
        """
    
    def synthesize_decision(self, decision_input: DecisionInput, agent_outputs: List[AgentOutput]) -> str:
        """Synthesize all agent outputs into final decision"""
        summaries = []
        for output in agent_outputs:
            summaries.append(f"""
            {output.agent_role.value.upper()}:
            Position: {output.structured_arguments.position}
            Key Arguments: {', '.join(output.structured_arguments.arguments[:2])}
            Confidence: {output.structured_arguments.confidence}
            """)
        
        return f"""
        Based on the following analysis, make a final recommendation:
        
        Decision: {decision_input.problem}
        Options: {', '.join(decision_input.options)}
        
        Agent Analyses:
        {chr(10).join(summaries)}
        
        Provide:
        1. Final recommendation
        2. Supporting arguments
        3. Counterarguments
        4. Conditions that could change the decision
        5. Confidence level
        """