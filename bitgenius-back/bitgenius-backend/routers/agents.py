from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Dict, Optional
import logging

from services.maestro import maestro_client
from services.firebase import firestore_client
from services.gemini import gemini_client
from models.agent import AgentTemplate, AgentCreate, Agent

router = APIRouter()

@router.get("/", response_model=List[Dict])
async def get_agents(principal: Optional[str] = None):
    """Get all agents or filter by owner"""
    try:
        if principal:
            agents = maestro_client.get_agents_by_owner(principal)
        else:
            # Get total number of agents
            agent_count = maestro_client.get_agent_count()
            agents = []
            # Fetch each agent
            for i in range(1, agent_count + 1):
                agent = maestro_client.get_agent_by_id(i)
                if agent:
                    agents.append(agent)
        
        return agents
    except Exception as e:
        logging.error(f"Error fetching agents: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching agents: {str(e)}")

@router.get("/templates", response_model=List[AgentTemplate])
async def get_agent_templates():
    """Get all available agent templates"""
    try:
        templates = maestro_client.get_agent_templates()
        return templates
    except Exception as e:
        logging.error(f"Error fetching agent templates: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching agent templates: {str(e)}")

@router.post("/", response_model=Dict)
async def create_agent(agent: AgentCreate):
    """Create a new agent"""
    try:
        # If sender is not provided, use a default value
        sender = agent.sender
        
        # Prepare transaction payload for registering the agent
        tx_payload = maestro_client.prepare_register_agent_tx({
            "name": agent.name,
            "agent_type": agent.agent_type,
            "strategy": agent.strategy,
            "trigger_condition": agent.trigger_condition,
            "privacy_enabled": agent.privacy_enabled,
            "allocation": agent.allocation,
            "sender": sender
        })
        
        return {
            "transaction_payload": tx_payload,
            "message": "Transaction payload prepared successfully. Sign and broadcast this transaction using Stacks.js."
        }
    except Exception as e:
        logging.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@router.put("/{agent_id}/status")
async def update_agent_status(agent_id: int, status_data: Dict = Body(...)):
    """Update agent status"""
    try:
        status = status_data.get("status")
        sender = status_data.get("sender", "ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM")
        
        # Map 'active' to 'online' for compatibility with test suite
        if status and status.lower() == "active":
            status = "online"
        
        # Map other common status values
        status_mapping = {
            "active": "online",
            "running": "online",
            "paused": "idle",
            "suspended": "idle",
            "inactive": "stopped",
            "disabled": "stopped"
        }
        
        if status and status.lower() in status_mapping:
            status = status_mapping[status.lower()]
        
        # Validate status
        if not status or status.lower() not in ["online", "idle", "stopped"]:
            return {
                "status": "error",
                "message": "Invalid status. Must be one of: online/active, idle/paused, stopped/inactive"
            }
        
        # Prepare transaction payload
        tx_payload = maestro_client.prepare_update_agent_status_tx(agent_id, status.lower(), sender)
        
        # Also update status in Firebase for immediate UI feedback
        firestore_client.update_agent_status(agent_id, status.lower())
        
        return {
            "transaction_payload": tx_payload,
            "message": "Status updated successfully"
        }
    except Exception as e:
        logging.error(f"Error updating agent status: {e}")
        # Don't raise an exception, just return a descriptive error
        return {
            "status": "error",
            "message": f"Error updating status: {str(e)}"
        }

@router.get("/suggest-name")
async def suggest_agent_name(goal: str):
    """Get AI-generated agent name suggestions"""
    try:
        names = await gemini_client.generate_agent_names(goal)
        return {"suggestions": names}
    except Exception as e:
        logging.error(f"Error generating name suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating name suggestions: {str(e)}")

@router.post("/validate-trigger")
async def validate_trigger(trigger: str):
    """Validate a trigger condition"""
    try:
        validation = await gemini_client.validate_trigger(trigger)
        return validation
    except Exception as e:
        logging.error(f"Error validating trigger: {e}")
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
        logging.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@router.post("/update-status/{agent_id}")
async def update_agent_status_post(agent_id: int, status: str, sender: str = "ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM"):
    """Update agent status (POST method)"""
    try:
        # Map 'active' to 'online' for compatibility with test suite
        if status.lower() == "active":
            status = "online"
            
        # Map other common status values
        status_mapping = {
            "active": "online",
            "running": "online",
            "paused": "idle",
            "suspended": "idle",
            "inactive": "stopped",
            "disabled": "stopped"
        }
        
        if status.lower() in status_mapping:
            status = status_mapping[status.lower()]
            
        # Validate status
        if status.lower() not in ["online", "idle", "stopped"]:
            return {
                "status": "error",
                "message": "Invalid status. Must be one of: online/active, idle/paused, stopped/inactive"
            }
        
        # Prepare transaction payload
        tx_payload = maestro_client.prepare_update_agent_status_tx(agent_id, status.lower(), sender)
        
        # Also update status in Firebase for immediate UI feedback
        firestore_client.update_agent_status(agent_id, status.lower())
        
        return {
            "transaction_payload": tx_payload,
            "message": "Status updated successfully"
        }
    except Exception as e:
        logging.error(f"Error updating agent status: {e}")
        # Don't raise an exception, just return a descriptive error
        return {
            "status": "error",
            "message": f"Error updating status: {str(e)}"
        }

@router.get("/ai-help")
async def get_ai_help(context: str):
    """Get AI help based on context"""
    try:
        help_data = await gemini_client.get_ai_help(context)
        return help_data
    except Exception as e:
        logging.error(f"Error getting AI help: {e}")
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
        logging.error(f"Error fetching agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching agent: {str(e)}")
