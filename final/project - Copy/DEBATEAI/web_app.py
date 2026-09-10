import sys
import os
# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from src.models.base import DecisionInput
from src.workflow.debate_workflow import DebateWorkflow
from src.services.chat_history import ChatHistory
from src.services.llm_service import llm_service
from pathlib import Path
import uvicorn
import json
import re
import io
import PyPDF2
from PIL import Image
import pytesseract

app = FastAPI(title="AI Debate System")

# Initialize Chat History
chat_history = ChatHistory()

# Path to HTML template
TEMPLATE_PATH = Path(__file__).parent / "templates" / "index.html"


def get_html_content() -> str:
    """Read HTML template from file"""
    if TEMPLATE_PATH.exists():
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Template not found</h1>"


def generate_followup_questions(problem: str, recommendation: str, arguments: list) -> list:
    """Generate intelligent follow-up questions using LLM"""
    
    prompt = f"""
You are a helpful assistant. Based on the following conversation, suggest 4 relevant follow-up questions.

USER QUESTION: "{problem}"

AI RECOMMENDATION: "{recommendation}"

SUPPORTING ARGUMENTS:
{chr(10).join(['• ' + arg for arg in arguments[:3]])}

IMPORTANT: Generate 4 follow-up questions that:
1. Are directly related to the user's original question
2. Help the user explore the topic further
3. Are practical and actionable
4. Cover different aspects of the decision

Return ONLY a JSON array of 4 questions. No other text.
Example format: ["Question 1?", "Question 2?", "Question 3?", "Question 4?"]
"""
    
    try:
        response = llm_service.generate_response(
            system_prompt="You are a helpful assistant that generates relevant follow-up questions.",
            user_prompt=prompt
        )
        
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group())
            if isinstance(questions, list) and len(questions) >= 4:
                return questions[:4]
        
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        questions = []
        for line in lines:
            clean = re.sub(r'^[\d]+\.\s*', '', line)
            clean = clean.strip('"\'')
            if clean and clean.endswith('?'):
                questions.append(clean)
        
        return questions[:4] if questions else _get_fallback_questions(problem)
        
    except Exception as e:
        print(f"Error generating follow-up questions: {e}")
        return _get_fallback_questions(problem)


def _get_fallback_questions(problem: str) -> list:
    """Fallback questions if LLM fails"""
    return [
        f"What are the next steps after this decision?",
        f"What resources are needed to implement this?",
        f"What are the potential risks of this decision?",
        f"How can we measure the success of this decision?"
    ]


@app.get("/", response_class=HTMLResponse)
async def home():
    return get_html_content()


# ============ CHAT HISTORY ENDPOINTS ============

@app.get("/history")
async def get_history(limit: int = 50):
    """Get recent chat history"""
    history = chat_history.get_history(limit)
    return {"history": history}


@app.get("/history/search")
async def search_history(q: str):
    """Search chat history by question"""
    history = chat_history.get_history_by_question(q)
    return {"history": history}


@app.delete("/history/{chat_id}")
async def delete_history(chat_id: int):
    """Delete a specific chat"""
    chat_history.delete_history(chat_id)
    return {"status": "deleted"}


@app.delete("/history/clear")
async def clear_history():
    """Clear all history"""
    chat_history.clear_all()
    return {"status": "cleared"}


@app.post("/upload_context")
async def upload_context_api(file: UploadFile = File(...)):
    """Extract text from uploaded PDF or Image file"""
    text = ""
    try:
        content = await file.read()
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image)
        else:
            text = f"[Unsupported file type: {file.filename}]"
    except Exception as e:
        text = f"[Error processing file {file.filename}: {str(e)}]"
    
    return {"text": text.strip()}


@app.post("/debate")
async def debate_api(decision: DecisionInput):
    """Run debate and return enriched results for the enterprise UI"""
    workflow = DebateWorkflow()
    result = workflow.run_debate(decision)

    # Extract agent names used
    agents_used = [output.agent_role.value for output in result.agent_outputs]

    # Save to chat history
    chat_history.save_chat(
        question=decision.problem,
        answer=result.final_recommendation['recommendation'],
        confidence=result.final_recommendation['confidence'],
        agents_used=agents_used
    )

    # Agent role details mapping
    role_titles = {
        "technical": "Technical Architecture",
        "cost": "Cost & ROI Analyst",
        "risk": "Risk & Vulnerability",
        "security": "Security & Compliance",
        "business": "Business Strategy",
        "supervisor": "Workflow Orchestrator",
        "critic": "Adversarial Critic",
        "decision": "Decision Synthesizer",
        "verification": "Evidence Verifier"
    }

    role_emojis = {
        "technical": "🏗️",
        "cost": "💰",
        "risk": "⚠️",
        "security": "🔒",
        "business": "💼",
        "supervisor": "👔",
        "critic": "🔍",
        "decision": "⚖️",
        "verification": "🔬"
    }

    # Get enriched agent outputs
    agent_outputs = []
    for output in result.agent_outputs:
        role_val = output.agent_role.value
        agent_outputs.append({
            "role": role_val,
            "name": role_val.capitalize(),
            "title": role_titles.get(role_val, "Specialist Agent"),
            "emoji": role_emojis.get(role_val, "🤖"),
            "position": output.structured_arguments.position,
            "confidence": output.structured_arguments.confidence,
            "arguments": output.structured_arguments.arguments or [],
            "risks": output.structured_arguments.risks or [],
            "evidence": output.structured_arguments.evidence or [],
            "assumptions": output.structured_arguments.assumptions or [],
            "analysis": output.analysis
        })

    critiques = []
    if hasattr(result, 'critique_rounds') and result.critique_rounds:
        for c in result.critique_rounds:
            critiques.append(c.get("critique", ""))

    # Generate follow-up questions
    followup_questions = generate_followup_questions(
        decision.problem,
        result.final_recommendation['recommendation'],
        result.final_recommendation['arguments']
    )

    return {
        "problem": decision.problem,
        "options": decision.options or [],
        "criteria": decision.criteria or [],
        "constraints": decision.constraints or [],
        "context": decision.context or "",
        "recommendation": result.final_recommendation['recommendation'],
        "confidence": result.final_recommendation['confidence'],
        "arguments": result.final_recommendation['arguments'],
        "risks": result.final_recommendation['risks'],
        "evidence": result.final_recommendation.get('evidence', []),
        "verified_claims": getattr(result, 'verified_claims', []),
        "critiques": critiques,
        "agent_outputs": agent_outputs,
        "followup_questions": followup_questions
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🌐 AI Debate System - Modern Web Interface")
    print("=" * 60)
    print("\n🚀 Starting server at: http://127.0.0.1:8000")
    print("📝 Open your browser and visit the URL above")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)