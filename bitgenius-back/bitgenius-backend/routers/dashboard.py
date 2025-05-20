from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional

from services.maestro import maestro_client
from services.firebase import firestore_client
from services.btc import btc_client
from models.agent import AgentOverview
from models.log import Notification

router = APIRouter()

@router.get("/summary", response_model=Dict)
async def get_dashboard_summary():
    """Get summary data for the dashboard"""
    try:
        # Get the number of agents
        agent_count = maestro_client.get_agent_count()
        
        # Get BTC price
        btc_price = btc_client.get_btc_price()
        
        return {
            "agent_count": agent_count,
            "btc_price": btc_price,
            "active_agents": agent_count // 2,  # Placeholder logic
            "latest_performance": 5.2  # Placeholder value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard summary: {str(e)}")

@router.get("/market", response_model=Dict)
async def get_market_data():
    """Get market data for the dashboard"""
    try:
        btc_price = btc_client.get_btc_price()
        
        # Placeholder market data
        return {
            "btc_price": btc_price,
            "price_change_24h": 1.2,
            "volume_24h": 28765430000,
            "market_cap": 864532100000,
            "chart_data": [
                {"timestamp": 1656043200, "price": 20100},
                {"timestamp": 1656046800, "price": 20200},
                {"timestamp": 1656050400, "price": 20150},
                {"timestamp": 1656054000, "price": 20300},
                {"timestamp": 1656057600, "price": 20250}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market data: {str(e)}")

@router.get("/overview/{principal}", response_model=AgentOverview)
async def get_dashboard_overview(principal: str):
    """Get overview data for the dashboard"""
    try:
        agents = maestro_client.get_agents_by_owner(principal)
        
        active_count = 0
        idle_count = 0
        stopped_count = 0
        
        for agent in agents:
            status = agent.get("status", "").lower()
            if status == "online":
                active_count += 1
            elif status == "idle":
                idle_count += 1
            elif status == "stopped":
                stopped_count += 1
        
        total_count = len(agents)
        
        wallet_balance = 0.0
        
        return {
            "agent_count": total_count,
            "active_agents": active_count,
            "idle_agents": idle_count,
            "stopped_agents": stopped_count,
            "wallet_balance": wallet_balance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard overview: {str(e)}")

@router.get("/live-console/{agent_id}")
async def get_live_console(agent_id: int, limit: int = Query(10, ge=1, le=100)):
    """Get the latest logs for the live console"""
    try:
        logs = firestore_client.get_agent_logs(agent_id, limit)
        
        if not logs:
            contract_log = maestro_client.get_agent_logs(agent_id)
            if contract_log:
                logs = [contract_log]
        
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live console data: {str(e)}")

@router.get("/performance/{agent_id}")
async def get_performance_metrics(agent_id: int, period: Optional[str] = "day"):
    """Get performance metrics for an agent"""
    try:
        period_value = 1  
        if period == "week":
            period_value = 7
        elif period == "month":
            period_value = 30
        
        metrics = maestro_client.get_agent_performance(agent_id, period_value)
        
        return {"metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching performance metrics: {str(e)}")

@router.get("/wallet/{btc_address}")
async def get_wallet_info(btc_address: str):
    """Get wallet balance and transaction history"""
    try:
        address_info = btc_client.get_address_info(btc_address)
        
        transactions = btc_client.get_address_transactions(btc_address, 10)
        
        btc_price = btc_client.get_btc_price()
        
        return {
            "address": btc_address,
            "balance_sats": address_info.get("chain_stats", {}).get("funded_txo_sum", 0) - 
                           address_info.get("chain_stats", {}).get("spent_txo_sum", 0),
            "transactions": transactions,
            "btc_price_usd": btc_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wallet information: {str(e)}")

@router.get("/notifications/{principal}", response_model=List[Notification])
async def get_notifications(principal: str, limit: int = Query(10, ge=1, le=50)):
    """Get notifications for a user"""
    try:
        notifications = firestore_client.get_notifications(principal, limit)
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@router.post("/notifications/{principal}/{notification_id}/read")
async def mark_notification_read(principal: str, notification_id: str):
    """Mark a notification as read"""
    try:
        firestore_client.mark_notification_as_read(principal, notification_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")
