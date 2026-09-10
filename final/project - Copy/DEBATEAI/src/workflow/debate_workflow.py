from typing import Dict, Any, List
from src.models import DecisionInput, AgentOutput, DebateState
from src.agents import (
    TechnicalAgent, CostAgent, RiskAgent, SecurityAgent, 
    BusinessAgent, SupervisorAgent, CriticAgent, DecisionAgent
)
from src.rag.rag_service import RAGService

class DebateWorkflow:
    """Orchestrates the multi-agent debate process"""
    
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.technical = TechnicalAgent()
        self.cost = CostAgent()
        self.risk = RiskAgent()
        self.security = SecurityAgent()
        self.business = BusinessAgent()
        self.critic = CriticAgent()
        self.decision = DecisionAgent()
        self.rag = RAGService()
    
    def run_debate(self, decision_input: DecisionInput, show_details: bool = True) -> DebateState:
        """Run the complete debate workflow"""
        
        print("=" * 70)
        print("🤖 STARTING MULTI-AGENT DEBATE".center(70))
        print("=" * 70)
        print(f"\n📋 Decision: {decision_input.problem}")
        if decision_input.options:
            print(f"📌 Options: {', '.join(decision_input.options)}")
        if decision_input.criteria:
            print(f"📊 Criteria: {', '.join(decision_input.criteria)}")
        print("-" * 70)
        
        # Step 1: Retrieve relevant evidence using RAG
        print("\n📚 RETRIEVING EVIDENCE (RAG)...")
        evidence = self.rag.search(decision_input.problem, k=3)
        if evidence:
            print(f"   ✅ Found {len(evidence)} relevant documents")
            for i, doc in enumerate(evidence, 1):
                print(f"      {i}. {doc['content'][:100]}...")
        else:
            print("   ⚠️ No relevant documents found")
        
        # Step 2: Supervisor analyzes the problem
        print("\n👔 SUPERVISOR AGENT: Analyzing problem...")
        supervisor_output = self.supervisor.analyze(decision_input)
        print(f"   Position: {supervisor_output.structured_arguments.position}")
        print(f"   Confidence: {supervisor_output.structured_arguments.confidence:.2f}")
        
        # Step 3: DYNAMIC AGENT SELECTION
        print("\n" + "=" * 70)
        print("📊 AGENT DEBATE".center(70))
        print("=" * 70)
        
        agent_keywords = {
            "technical": ["technical", "architecture", "code", "system", "infrastructure", "programming", 
                         "language", "framework", "software", "technology", "microservices", "server", 
                         "database", "api", "backend", "frontend", "development", "engineering"],
            "cost": ["cost", "budget", "money", "financial", "price", "expensive", "cheap", "afford", 
                    "spend", "expense", "investment", "fund", "capital", "operational", "saving"],
            "risk": ["risk", "danger", "threat", "failure", "safety", "hazard", "uncertainty", 
                    "vulnerability", "loss", "breach", "issue", "problem", "challenge"],
            "security": ["security", "privacy", "data", "protection", "hack", "breach", 
                        "vulnerability", "auth", "encryption", "compliance", "gdpr", "hipaa", "safe"],
            "business": ["business", "market", "profit", "customer", "strategy", "revenue", "sales", 
                        "growth", "competition", "industry", "competitive", "profitability", "brand"]
        }
        
        analysis_lower = supervisor_output.analysis.lower()
        problem_lower = decision_input.problem.lower()
        combined_text = analysis_lower + " " + problem_lower
        
        needed_names = []
        
        if any(keyword in combined_text for keyword in agent_keywords["technical"]):
            needed_names.append("Technical")
        if any(keyword in combined_text for keyword in agent_keywords["cost"]):
            needed_names.append("Cost")
        if any(keyword in combined_text for keyword in agent_keywords["risk"]):
            needed_names.append("Risk")
        if any(keyword in combined_text for keyword in agent_keywords["security"]):
            needed_names.append("Security")
        if any(keyword in combined_text for keyword in agent_keywords["business"]):
            needed_names.append("Business")
        
        if not needed_names:
            needed_names = ["Technical", "Cost", "Risk", "Security", "Business"]
        
        agent_map = {
            "Technical": self.technical,
            "Cost": self.cost,
            "Risk": self.risk,
            "Security": self.security,
            "Business": self.business
        }
        
        agents_to_run = [(name, agent_map[name]) for name in needed_names if name in agent_map]
        
        print(f"\n📋 Agents activated: {', '.join(needed_names)}")
        print("-" * 50)
        
        agent_outputs = []
        for name, agent in agents_to_run:
            print(f"\n{name} AGENT:")
            output = agent.analyze(decision_input)
            agent_outputs.append(output)
            
            args = output.structured_arguments
            print(f"   Position: {args.position}")
            print(f"   Confidence: {args.confidence:.2f}")
            print(f"   Reasons:")
            for arg in args.arguments[:3]:
                print(f"      • {arg}")
            if args.risks:
                print(f"   Risks:")
                for risk in args.risks[:2]:
                    print(f"      • {risk}")
        
        # Step 4: Critic evaluates all arguments
        print("\n" + "=" * 70)
        print("🔍 CRITIC AGENT: Evaluating arguments...".center(70))
        print("=" * 70)
        critic_output = self.critic.analyze(decision_input)
        print(f"   Position: {critic_output.structured_arguments.position}")
        print(f"   Confidence: {critic_output.structured_arguments.confidence:.2f}")
        print(f"   Reasons:")
        for arg in critic_output.structured_arguments.arguments[:3]:
            print(f"      • {arg}")
        
        # Step 5: Decision synthesis
        print("\n" + "=" * 70)
        print("⚖️  DECISION AGENT: Synthesizing final recommendation...".center(70))
        print("=" * 70)
        decision_output = self.decision.analyze(decision_input)
        
        # Step 6: Verify claims using RAG
        print("\n🔬 VERIFICATION: Checking claims against evidence...")
        verification_results = self._verify_claims(decision_output.structured_arguments.arguments)
        print(f"   ✅ Verified {verification_results['verified']}/{verification_results['total']} claims")
        
        # Show final recommendation
        print("\n" + "=" * 70)
        print("📊 FINAL RECOMMENDATION".center(70))
        print("=" * 70)
        print(f"\n📌 Recommendation: {decision_output.structured_arguments.position}")
        print(f"📈 Confidence: {decision_output.structured_arguments.confidence:.2f} ({decision_output.structured_arguments.confidence*100:.0f}%)")
        
        print("\n✅ Supporting Arguments:")
        for arg in decision_output.structured_arguments.arguments:
            print(f"   • {arg}")
        
        if decision_output.structured_arguments.risks:
            print("\n⚠️  Risks:")
            for risk in decision_output.structured_arguments.risks:
                print(f"   • {risk}")
        
        print("\n" + "=" * 70)
        print("✅ DEBATE COMPLETE".center(70))
        print("=" * 70)
        
        state = DebateState(
            decision_input=decision_input,
            agent_outputs=agent_outputs,
            critique_rounds=[{"critique": critic_output.analysis}],
            verified_claims=verification_results.get('results', []),
            final_recommendation={
                "recommendation": decision_output.structured_arguments.position,
                "arguments": decision_output.structured_arguments.arguments,
                "risks": decision_output.structured_arguments.risks,
                "confidence": decision_output.structured_arguments.confidence,
                "evidence": decision_output.structured_arguments.evidence
            },
            status="completed"
        )
        
        return state
    
    def _verify_claims(self, claims: List[str]) -> Dict[str, Any]:
        """Verify claims against evidence"""
        results = []
        for claim in claims:
            evidence = self.rag.search(claim, k=1)
            if evidence and evidence[0]['score'] > 0.5:
                results.append({
                    "claim": claim,
                    "verified": True,
                    "evidence": evidence[0]['content'][:150],
                    "score": evidence[0]['score']
                })
            else:
                results.append({
                    "claim": claim,
                    "verified": False,
                    "evidence": "No supporting evidence found",
                    "score": 0
                })
        return {
            "total": len(claims),
            "verified": sum(1 for r in results if r['verified']),
            "results": results
        }
    
    def get_summary(self, state: DebateState) -> Dict[str, Any]:
        """Get a summary of the debate"""
        return {
            "problem": state.decision_input.problem,
            "options": state.decision_input.options,
            "recommendation": state.final_recommendation,
            "agent_count": len(state.agent_outputs),
            "status": state.status
        }