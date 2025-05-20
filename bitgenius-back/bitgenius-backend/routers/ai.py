from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional

from services.gemini import gemini_client

router = APIRouter()

@router.post("/strategy", response_model=Dict)
async def get_strategy_recommendations(request_data: Dict):
    """Get strategy recommendations based on market conditions and risk preference"""
    try:
        market_condition = request_data.get("market_condition", "neutral")
        risk_preference = request_data.get("risk_preference", "moderate")
        
        prompt = f"""
        Based on a {market_condition} market condition and a {risk_preference} risk preference,
        recommend 3 Bitcoin investment strategies. For each strategy, provide:
        1. A name
        2. A brief description
        3. Expected risk level (low, medium, high)
        4. Potential reward
        5. Recommended time horizon
        Format your response as structured data only, no introductions or conclusions.
        """
        
        response = await gemini_client.model.generate_content_async(prompt)
        
        return {
            "market_condition": market_condition,
            "risk_preference": risk_preference,
            "recommendations": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating strategy recommendations: {str(e)}")

@router.post("/analyze", response_model=Dict)
async def analyze_market(request_data: Dict):
    """Analyze market based on specified indicators"""
    try:
        timeframe = request_data.get("timeframe", "daily")
        indicators = request_data.get("indicators", ["rsi"])
        
        prompt = f"""
        Provide a detailed market analysis for Bitcoin based on the {timeframe} timeframe,
        focusing on the following indicators: {', '.join(indicators)}.
        Include current market conditions, key support and resistance levels,
        and a short-term outlook (next 24-48 hours).
        Format your response as structured data only, no introductions or conclusions.
        """
        
        response = await gemini_client.model.generate_content_async(prompt)
        
        return {
            "timeframe": timeframe,
            "indicators": indicators,
            "analysis": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating market analysis: {str(e)}")

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
