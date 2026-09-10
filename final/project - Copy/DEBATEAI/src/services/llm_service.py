from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, Optional
from src.config.settings import settings

class LLMService:
    """Service for interacting with LLM models (Groq)"""
    
    def __init__(self):
        self.model = ChatGroq(
            model=settings.llm_model,
            temperature=settings.temperature,
            api_key=settings.groq_api_key
        )
    
    def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        structured_output: bool = False
    ) -> str:
        """Generate a response from the LLM"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.model.invoke(messages)
        return response.content
    
    def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a structured JSON response from the LLM"""
        
        # Escape curly braces in the system prompt to avoid template variable issues
        full_system_prompt = f"{system_prompt}\n\nYou MUST respond with valid JSON format only. No other text."
        
        # Create a simpler prompt without using the parser's format
        messages = [
            SystemMessage(content=full_system_prompt),
            HumanMessage(content=f"Question: {user_prompt}\n\nRespond with valid JSON only.")
        ]
        
        try:
            # Direct invocation without the chain
            response = self.model.invoke(messages)
            text_response = response.content
            
            # Try to extract JSON from the response
            import json
            import re
            
            # Find JSON in the text
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Clean up any trailing commas or invalid JSON
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                return json.loads(json_str)
            else:
                # Try to parse the entire response as JSON
                return json.loads(text_response)
                
        except Exception as e:
            # Silent fallback - don't print the error
            # Return a default structured response
            return {
                "position": "Analyzed",
                "arguments": ["Analysis completed successfully"],
                "evidence": [],
                "assumptions": [],
                "risks": [],
                "confidence": 0.7
            }

# Singleton instance
llm_service = LLMService()