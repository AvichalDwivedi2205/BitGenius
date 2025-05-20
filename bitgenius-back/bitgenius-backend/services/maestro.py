import os
import requests
from typing import Dict, List, Optional, Any
import json

class MaestroClient:
    def __init__(self):
        self.api_key = os.environ.get("MAESTRO_API_KEY")
        self.base_url = "https://api.maestro.co/v1"
        self.contract_address = os.environ.get("CONTRACT_ADDRESS")
        self.contract_name = "bitgenius-agent"
        
        if not self.api_key:
            raise ValueError("MAESTRO_API_KEY environment variable not set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=self.headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=self.headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code != 200:
            raise Exception(f"Maestro API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def get_agent_by_id(self, agent_id: int) -> Dict:
        """Get agent details by ID using the get-agent-by-id read-only function"""
        endpoint = f"/stacks/v1/read-only-call"
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "get-agent-by-id",
            "function_args": [{"type": "uint", "value": str(agent_id)}]
        }
        return self._make_request("POST", endpoint, payload)
    
    def get_agents_by_owner(self, owner: str) -> List[Dict]:
        """Get all agents owned by a specific principal"""
        # Since there's no direct function for this in the contract,
        # we need to get the agent count and then check each agent
        agent_count = self.get_agent_count()
        agents = []
        
        for i in range(1, agent_count + 1):
            agent = self.get_agent_by_id(i)
            if agent and agent.get("owner") == owner:
                agents.append(agent)
        
        return agents
    
    def get_agent_status(self, agent_id: int) -> str:
        """Get the current status of an agent"""
        endpoint = f"/stacks/v1/read-only-call"
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "get-agent-status",
            "function_args": [{"type": "uint", "value": str(agent_id)}]
        }
        response = self._make_request("POST", endpoint, payload)
        return response.get("value", {}).get("value", "unknown")
    
    def get_agent_count(self) -> int:
        """Get the total number of agents"""
        endpoint = f"/stacks/v1/read-only-call"
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "get-agent-count",
            "function_args": []
        }
        response = self._make_request("POST", endpoint, payload)
        return int(response.get("value", {}).get("value", "0"))
    
    def get_agent_templates(self) -> List[Dict]:
        """Get all available agent templates"""
        endpoint = f"/stacks/v1/read-only-call"
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "get-all-templates",
            "function_args": []
        }
        response = self._make_request("POST", endpoint, payload)
        template_ids = response.get("value", {}).get("value", [])
        
        templates = []
        for template_id in template_ids:
            template = self.get_agent_template(template_id)
            if template:
                templates.append({
                    "template_id": template_id,
                    **template
                })
        
        return templates
    
    def get_agent_template(self, template_id: str) -> Dict:
        """Get details of a specific agent template"""
        endpoint = f"/stacks/v1/read-only-call"
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "get-agent-template",
            "function_args": [{"type": "string-ascii", "value": template_id}]
        }
        response = self._make_request("POST", endpoint, payload)
        return response.get("value", {}).get("value", {})
    
    def get_agent_logs(self, agent_id: int, timestamp: Optional[int] = None) -> Dict:
        """Get logs for a specific agent"""
        endpoint = f"/stacks/v1/read-only-call"
        
        if timestamp:
            payload = {
                "contract_address": self.contract_address,
                "contract_name": self.contract_name,
                "function_name": "get-log",
                "function_args": [
                    {"type": "uint", "value": str(agent_id)},
                    {"type": "uint", "value": str(timestamp)}
                ]
            }
        else:
            payload = {
                "contract_address": self.contract_address,
                "contract_name": self.contract_name,
                "function_name": "get-most-recent-log",
                "function_args": [{"type": "uint", "value": str(agent_id)}]
            }
        
        return self._make_request("POST", endpoint, payload)
    
    def get_agent_performance(self, agent_id: int, period: int) -> Dict:
        """Get performance metrics for an agent"""
        endpoint = f"/stacks/v1/read-only-call"
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "get-agent-performance",
            "function_args": [
                {"type": "uint", "value": str(agent_id)},
                {"type": "uint", "value": str(period)}
            ]
        }
        return self._make_request("POST", endpoint, payload)
    
    def prepare_register_agent_tx(self, agent_data: Dict) -> Dict:
        """Prepare a transaction payload for registering a new agent"""
        endpoint = "/stacks/v1/transactions/build"
        
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "register-agent",
            "function_args": [
                {"type": "string-ascii", "value": agent_data["name"]},
                {"type": "string-ascii", "value": agent_data["agent_type"]},
                {"type": "string-ascii", "value": agent_data["strategy"]},
                {"type": "string-ascii", "value": agent_data["trigger_condition"]},
                {"type": "bool", "value": str(agent_data["privacy_enabled"]).lower()},
                {"type": "uint", "value": str(agent_data["allocation"])}
            ],
            "sender_address": agent_data["sender"]
        }
        
        return self._make_request("POST", endpoint, payload)
    
    def prepare_update_agent_status_tx(self, agent_id: int, new_status: str, sender: str) -> Dict:
        """Prepare a transaction payload for updating agent status"""
        endpoint = "/stacks/v1/transactions/build"
        
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "update-agent-status",
            "function_args": [
                {"type": "uint", "value": str(agent_id)},
                {"type": "string-ascii", "value": new_status}
            ],
            "sender_address": sender
        }
        
        return self._make_request("POST", endpoint, payload)
    
    def prepare_log_agent_action_tx(self, log_data: Dict, sender: str) -> Dict:
        """Prepare a transaction payload for logging an agent action"""
        endpoint = "/stacks/v1/transactions/build"
        
        # Prepare optional arguments
        tx_id = log_data.get("transaction_id")
        if tx_id:
            tx_id_arg = {"type": "optional", "value": {"type": "buff", "value": tx_id}}
        else:
            tx_id_arg = {"type": "optional", "value": None}
            
        amount = log_data.get("amount")
        if amount is not None:
            amount_arg = {"type": "optional", "value": {"type": "uint", "value": str(amount)}}
        else:
            amount_arg = {"type": "optional", "value": None}
            
        fee = log_data.get("fee")
        if fee is not None:
            fee_arg = {"type": "optional", "value": {"type": "uint", "value": str(fee)}}
        else:
            fee_arg = {"type": "optional", "value": None}
        
        payload = {
            "contract_address": self.contract_address,
            "contract_name": self.contract_name,
            "function_name": "log-agent-action",
            "function_args": [
                {"type": "uint", "value": str(log_data["agent_id"])},
                {"type": "string-ascii", "value": log_data["action"]},
                {"type": "string-ascii", "value": log_data["status"]},
                tx_id_arg,
                amount_arg,
                fee_arg,
                {"type": "string-ascii", "value": log_data["details"]}
            ],
            "sender_address": sender
        }
        
        return self._make_request("POST", endpoint, payload)

# Create a singleton instance
maestro_client = MaestroClient()
