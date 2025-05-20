from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AgentTemplate(BaseModel):
    template_id: str
    description: str
    default_strategy: str

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    agent_type: str = Field(..., min_length=1, max_length=20)
    strategy: str = Field(..., min_length=1, max_length=100)
    trigger_condition: str = Field(..., min_length=1, max_length=100)
    privacy_enabled: bool = False
    allocation: int = Field(..., gt=0)
    sender: str = Field(..., min_length=1)

class Agent(BaseModel):
    agent_id: int
    owner: str
    name: str
    agent_type: str
    strategy: str
    status: str
    trigger_condition: str
    privacy_enabled: bool
    allocation: int
    created_at: int
    last_active: int

class UserSettings(BaseModel):
    default_agent_type: str
    privacy_default: bool
    notification_level: str
    execution_mode: str
    runtime_cap: int

class AgentStatus(BaseModel):
    agent_id: int
    status: str
    last_active: int

class AgentOverview(BaseModel):
    agent_count: int
    active_agents: int
    idle_agents: int
    stopped_agents: int
    wallet_balance: float
