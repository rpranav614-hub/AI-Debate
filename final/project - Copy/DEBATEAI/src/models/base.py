from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class AgentRole(str, Enum):
    SUPERVISOR = "supervisor"
    TECHNICAL = "technical"
    COST = "cost"
    RISK = "risk"
    SECURITY = "security"
    BUSINESS = "business"
    CRITIC = "critic"
    VERIFICATION = "verification"
    DECISION = "decision"

class Argument(BaseModel):
    position: str = Field(description="The stance or position taken")
    arguments: List[str] = Field(description="List of supporting arguments")
    evidence: Optional[List[str]] = Field(default=[], description="Supporting evidence")
    assumptions: Optional[List[str]] = Field(default=[], description="Assumptions made")
    risks: Optional[List[str]] = Field(default=[], description="Identified risks")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")

class DecisionInput(BaseModel):
    problem: str = Field(description="The decision problem to analyze")
    options: List[str] = Field(description="Available options")
    criteria: Optional[List[str]] = Field(default=[], description="Evaluation criteria")
    constraints: Optional[List[str]] = Field(default=[], description="Constraints")
    context: Optional[str] = Field(default="", description="Additional context")
    custom_perspectives: Optional[List[str]] = Field(default=[], description="Custom agent perspectives")

class AgentOutput(BaseModel):
    agent_role: AgentRole
    analysis: str = Field(description="Detailed analysis from agent")
    structured_arguments: Argument
    metadata: Optional[Dict[str, Any]] = Field(default={})
    timestamp: datetime = Field(default_factory=datetime.now)

class DebateState(BaseModel):
    decision_input: DecisionInput
    agent_outputs: List[AgentOutput] = Field(default=[])
    critique_rounds: List[Dict[str, Any]] = Field(default=[])
    verified_claims: List[Dict[str, Any]] = Field(default=[])
    final_recommendation: Optional[Dict[str, Any]] = None
    status: str = "initiated"