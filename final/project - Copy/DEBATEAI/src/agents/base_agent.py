from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from src.models import AgentRole, Argument, AgentOutput, DecisionInput
from src.services.llm_service import llm_service

class BaseAgent(ABC):
    """Base class for all agents in the debate system"""
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.llm = llm_service
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    @abstractmethod
    def get_user_prompt(self, decision_input: DecisionInput) -> str:
        """Get the user prompt for this agent"""
        pass
    
    def _extract_list(self, value: Any) -> List[str]:
        """Safely extract a list from various formats"""
        if isinstance(value, list):
            return [str(item) for item in value]
        elif isinstance(value, dict):
            return [str(v) for v in value.values() if v]
        elif isinstance(value, str):
            # Split by commas if it's a string
            if ',' in value:
                return [item.strip() for item in value.split(',')]
            return [value]
        elif value is None:
            return []
        else:
            return [str(value)]
    
    def _extract_confidence(self, value: Any) -> float:
        """Safely extract confidence as float"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ['high', 'very high', 'strong']:
                return 0.9
            elif value_lower in ['medium', 'moderate', 'fair']:
                return 0.6
            elif value_lower in ['low', 'weak']:
                return 0.3
            else:
                try:
                    return float(value)
                except:
                    return 0.5
        else:
            return 0.5
    
    def analyze(self, decision_input: DecisionInput) -> AgentOutput:
        """Analyze the decision from this agent's perspective"""
        system_prompt = self.get_system_prompt()
        user_prompt = self.get_user_prompt(decision_input)
        
        # Add format instructions
        format_instructions = """
        You MUST respond in this EXACT JSON format:
        {
            "position": "your stance on the decision",
            "arguments": ["argument 1", "argument 2", "argument 3"],
            "evidence": ["evidence 1", "evidence 2"],
            "assumptions": ["assumption 1", "assumption 2"],
            "risks": ["risk 1", "risk 2", "risk 3"],
            "confidence": 0.85
        }
        All fields are required. Confidence must be a number between 0 and 1.
        """
        
        full_system_prompt = f"{system_prompt}\n\n{format_instructions}"
        
        response = self.llm.generate_structured_response(
            system_prompt=full_system_prompt,
            user_prompt=user_prompt,
            schema={}
        )
        
        # Safely extract values
        arguments = self._extract_list(response.get("arguments", []))
        evidence = self._extract_list(response.get("evidence", []))
        assumptions = self._extract_list(response.get("assumptions", []))
        risks = self._extract_list(response.get("risks", []))
        confidence = self._extract_confidence(response.get("confidence", 0.5))
        
        # Create structured arguments
        argument = Argument(
            position=response.get("position", "Undecided"),
            arguments=arguments if arguments else ["No specific arguments provided"],
            evidence=evidence,
            assumptions=assumptions,
            risks=risks,
            confidence=confidence
        )
        
        # Create agent output
        return AgentOutput(
            agent_role=self.role,
            analysis=self._format_analysis(argument),
            structured_arguments=argument,
            metadata={"raw_response": response}
        )
    
    def _format_analysis(self, argument: Argument) -> str:
        """Format the analysis as a readable string"""
        analysis = f"""
        Position: {argument.position}
        
        Arguments:
        {self._format_list(argument.arguments)}
        
        Evidence:
        {self._format_list(argument.evidence)}
        
        Assumptions:
        {self._format_list(argument.assumptions)}
        
        Risks:
        {self._format_list(argument.risks)}
        
        Confidence: {argument.confidence:.2f}
        """
        return analysis.strip()
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items with bullet points"""
        if not items:
            return "None"
        return "\n".join([f"• {item}" for item in items])