import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import DecisionInput
from src.workflow.debate_workflow import DebateWorkflow

def ask_question():
    print("=" * 60)
    print("🤖 AI Debate System - Ask Any Decision Question")
    print("=" * 60)
    print("\n📝 Examples:")
    print("  • Should we migrate to microservices?")
    print("  • Should we use AWS or Azure?")
    print("  • Should we hire more developers or outsource?")
    print("  • Should we build or buy our CRM system?")
    print("-" * 60)
    
    # Get user input
    problem = input("\n❓ What decision do you want to analyze?\n> ")
    
    if not problem:
        print("❌ Please enter a question.")
        return
    
    # Let user add options
    print("\n📋 Enter options (one per line, press Enter twice when done):")
    options = []
    while True:
        opt = input("> ")
        if not opt:
            break
        options.append(opt)
    
    if not options:
        options = ["Yes", "No", "Alternative approach"]
    
    # Let user add criteria
    print("\n📊 Enter evaluation criteria (one per line, press Enter twice when done):")
    criteria = []
    while True:
        crit = input("> ")
        if not crit:
            break
        criteria.append(crit)
    
    if not criteria:
        criteria = ["Cost", "Performance", "Risk", "Scalability", "Security"]
    
    # Create decision
    decision = DecisionInput(
        problem=problem,
        options=options,
        criteria=criteria,
        constraints=[],
        context="Real-world business/technical decision"
    )
    
    print("\n" + "=" * 60)
    print("🤖 Starting Multi-Agent Debate...")
    print("=" * 60)
    
    # Run the debate
    workflow = DebateWorkflow()
    result = workflow.run_debate(decision)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 FINAL RECOMMENDATION")
    print("=" * 60)
    
    print(f"\n📋 Decision: {result.decision_input.problem}")
    print(f"\n📌 Recommendation: {result.final_recommendation['recommendation']}")
    print(f"📈 Confidence: {result.final_recommendation['confidence']:.2f} ({result.final_recommendation['confidence']*100:.0f}%)")
    
    print("\n✅ Supporting Arguments:")
    for arg in result.final_recommendation['arguments']:
        print(f"  • {arg}")
    
    print("\n⚠️ Risks:")
    for risk in result.final_recommendation['risks']:
        print(f"  • {risk}")
    
    print("\n" + "=" * 60)
    print("✅ Debate Complete!")
    print("=" * 60)

if __name__ == "__main__":
    ask_question()