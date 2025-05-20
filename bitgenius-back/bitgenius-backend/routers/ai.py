from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional

from services.gemini import gemini_client

router = APIRouter()

@router.get("/suggest-name")
async def suggest_agent_name(goal: str):
    """Get AI-generated agent name suggestions"""
    try:
        names = await gemini_client.generate_agent_names(goal)
        return {"suggestions": names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating name suggestions: {str(e)}")

@router.post("/validate-trigger")
async def validate_trigger(trigger: str):
    """Validate a trigger condition"""
    try:
        validation = await gemini_client.validate_trigger(trigger)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating trigger: {str(e)}")

@router.post("/summarize-logs")
async def summarize_logs(logs: List[Dict]):
    """Summarize a set of agent logs"""
    try:
        summary = await gemini_client.summarize_logs(logs)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing logs: {str(e)}")

@router.get("/help")
async def get_ai_help(context: str):
    """Get AI help based on context"""
    try:
        help_data = await gemini_client.get_ai_help(context)
        return help_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AI help: {str(e)}")

@router.post("/explain-strategy")
async def explain_strategy(strategy: str):
    """Get AI explanation of a strategy"""
    try:
        prompt = f"Explain this Bitcoin trading strategy in simple terms: {strategy}"
        explanation = await gemini_client.model.generate_content_async(prompt)
        return {"explanation": explanation.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining strategy: {str(e)}")
