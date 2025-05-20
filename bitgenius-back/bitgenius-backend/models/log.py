from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class LogEntry(BaseModel):
    agent_id: int
    timestamp: int
    action: str
    status: str
    transaction_id: Optional[str] = None
    amount: Optional[int] = None
    fee: Optional[int] = None
    details: str

class PerformanceMetrics(BaseModel):
    agent_id: int
    period: int
    actions_count: int
    success_count: int
    failure_count: int
    total_fees: int
    total_volume: int

class Transaction(BaseModel):
    tx_id: str
    timestamp: int
    amount: int
    fee: int
    status: str
    details: str

class Notification(BaseModel):
    id: str
    user: str
    timestamp: int
    title: str
    message: str
    type: str
    read: bool = False
    agent_id: Optional[int] = None
