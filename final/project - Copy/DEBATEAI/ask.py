import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import DecisionInput
from src.workflow.debate_workflow import DebateWorkflow

print("=" * 60)
print("AI DEBATE AND DECISION-MAKING SYSTEM")
print("=" * 60)

question = input("\nEnter your decision question: ")

decision = DecisionInput(
    problem=question,
    options=[],
    criteria=[],
    constraints=[],
    context=""
)

workflow = DebateWorkflow()
result = workflow.run_debate(decision)  # ← REMOVED "question" from here

print("\n" + "=" * 60)
print("FINAL DECISION")
print("=" * 60)

rec = result.final_recommendation['recommendation']
conf = result.final_recommendation['confidence'] * 100

if conf >= 80:
    confidence_text = "High"
elif conf >= 60:
    confidence_text = "Medium"
else:
    confidence_text = "Low"

print(f"\nFINAL DECISION:")
print(f"{rec}")

print(f"\nRECOMMENDATION:")
for arg in result.final_recommendation['arguments']:
    print(f"• {arg}")

if result.final_recommendation['risks']:
    print(f"\nRISKS:")
    for risk in result.final_recommendation['risks']:
        print(f"• {risk}")

print(f"\nCONFIDENCE:")
print(f"{confidence_text} ({conf:.0f}%)")

print("\n" + "=" * 60)