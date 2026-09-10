from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import List, Optional
from src.models import DecisionInput
from src.workflow.debate_workflow import DebateWorkflow
from src.utils.file_parser import extract_text_from_file

router = APIRouter()
workflow = DebateWorkflow()

@router.post("/debate")
async def start_debate(
    question: str = Form(...),
    context: Optional[str] = Form(None),
    options: Optional[str] = Form(None),
    constraints: Optional[str] = Form(None),
    files: List[UploadFile] = File(None)
):
    """
    Start a new debate with optional file attachments.
    Supported file types: PDF, DOCX, TXT, PNG, JPG, JPEG.
    Extracted text from files is appended to the context.
    """
    try:
        # Parse comma-separated options/constraints if provided
        options_list = [o.strip() for o in options.split(',')] if options else []
        constraints_list = [c.strip() for c in constraints.split(',')] if constraints else []

        # Extract text from uploaded files
        file_texts = []
        if files:
            for file in files:
                contents = await file.read()
                text = extract_text_from_file(file.filename, contents)
                if text:
                    file_texts.append(f"--- Content from {file.filename} ---\n{text}\n")

        # Merge file content into context
        combined_context = context or ""
        if file_texts:
            combined_context += "\n\n" + "\n".join(file_texts)

        # Build the DecisionInput object (adjust fields according to your model)
        decision = DecisionInput(
            question=question,
            context=combined_context,
            options=options_list,
            constraints=constraints_list
            # add any other fields your model expects
        )

        # Run the debate workflow
        result = workflow.run_debate(decision)
        summary = workflow.get_summary(result)

        return {
            "status": "success",
            "debate": summary,
            "full_results": result.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep your other endpoints unchanged
@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Debate System"}

@router.get("/agents")
async def list_agents():
    return {
        "agents": [
            "Supervisor",
            "Technical",
            "Cost",
            "Risk",
            "Security",
            "Business",
            "Critic",
            "Decision"
        ]
    }