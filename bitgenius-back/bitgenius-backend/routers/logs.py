from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional
import csv
import io
import json

from services.maestro import maestro_client
from services.firebase import firestore_client
from models.log import LogEntry, PerformanceMetrics, Transaction

router = APIRouter()

@router.get("/live/{agent_id}")
async def get_live_logs(agent_id: int, limit: int = Query(10, ge=1, le=100)):
    """Get the latest logs for an agent"""
    try:
        # Get logs from Firebase
        logs = firestore_client.get_agent_logs(agent_id, limit)
        
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live logs: {str(e)}")

@router.get("/range")
async def get_logs_by_range(
    agent_id: int, 
    start: int = Query(..., description="Start timestamp"),
    end: int = Query(..., description="End timestamp")
):
    """Get logs within a specific time range"""
    try:
        logs = firestore_client.get_agent_logs_by_range(agent_id, start, end)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs by range: {str(e)}")

@router.get("/txs/{agent_id}")
async def get_transactions(agent_id: int, limit: int = Query(20, ge=1, le=100)):
    """Extract transaction data from logs"""
    try:
        logs = firestore_client.get_agent_logs(agent_id, limit=100) 
        tx_logs = [log for log in logs if log.get("transaction_id")]
        tx_logs = tx_logs[:limit]
        
        transactions = []
        for log in tx_logs:
            transactions.append({
                "tx_id": log.get("transaction_id"),
                "timestamp": log.get("timestamp"),
                "amount": log.get("amount", 0),
                "fee": log.get("fee", 0),
                "status": log.get("status"),
                "details": log.get("details", "")
            })
        
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")

@router.get("/performance/{agent_id}")
async def get_performance(agent_id: int, period: str = Query("day", enum=["day", "week", "month"])):
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

@router.get("/export/{agent_id}")
async def export_logs(
    agent_id: int, 
    format: str = Query("json", enum=["json", "csv"]),
    start: Optional[int] = None,
    end: Optional[int] = None
):
    """Export logs in JSON or CSV format"""
    try:
        if start and end:
            logs = firestore_client.get_agent_logs_by_range(agent_id, start, end)
        else:
            logs = firestore_client.get_agent_logs(agent_id, limit=1000)
        
        if format == "json":
            return {"logs": logs}
        else:
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(["timestamp", "action", "status", "transaction_id", "amount", "fee", "details"])

            for log in logs:
                writer.writerow([
                    log.get("timestamp", ""),
                    log.get("action", ""),
                    log.get("status", ""),
                    log.get("transaction_id", ""),
                    log.get("amount", ""),
                    log.get("fee", ""),
                    log.get("details", "")
                ])
            
            output.seek(0)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=agent_{agent_id}_logs.csv"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting logs: {str(e)}")
