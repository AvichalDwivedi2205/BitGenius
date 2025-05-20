from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional

from services.maestro import maestro_client
from services.firebase import firestore_client
from services.gemini import gemini_client
from models.agent import AgentTemplate, AgentCreate, Agent

router = APIRouter()

@router.get("/templates", response_model=List[AgentTemplate])
async def get_agent_templates():
    """Get all available agent templates"""
    try:
        templates = maestro_client.get_agent_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent templates: {str(e)}")

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

@router.post("/create")
async def create_agent(agent: AgentCreate):
    """Create a new agent"""
    try:
        # Prepare transaction payload for registering the agent
        tx_payload = maestro_client.prepare_register_agent_tx({
            "name": agent.name,
            "agent_type": agent.agent_type,
            "strategy": agent.strategy,
            "trigger_condition": agent.trigger_condition,
            "privacy_enabled": agent.privacy_enabled,
            "allocation": agent.allocation,
            "sender": agent.sender
        })
        
        return {
            "transaction_payload": tx_payload,
            "message": "Transaction payload prepared successfully. Sign and broadcast this transaction using Stacks.js."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@router.post("/update-status/{agent_id}")
async def update_agent_status(agent_id: int, status: str, sender: str):
    """Update agent status"""
    try:
        # Validate status
        if status not in ["online", "idle", "stopped"]:
            raise HTTPException(status_code=400, detail="Invalid status. Must be 'online', 'idle', or 'stopped'")
        
        # Prepare transaction payload
        tx_payload = maestro_client.prepare_update_agent_status_tx(agent_id, status, sender)
        
        # Also update status in Firebase for immediate UI feedback
        firestore_client.update_agent_status(agent_id, status)
        
        return {
            "transaction_payload": tx_payload,
            "message": "Transaction payload prepared successfully. Sign and broadcast this transaction using Stacks.js."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating agent status: {str(e)}")

@router.get("/ai-help")
async def get_ai_help(context: str):
    """Get AI help based on context"""
    try:
        help_data = await gemini_client.get_ai_help(context)
        return help_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AI help: {str(e)}")

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: int):
    """Get agent details by ID"""
    try:
        agent = maestro_client.get_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent: {str(e)}")
