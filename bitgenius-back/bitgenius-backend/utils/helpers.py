from typing import Dict, List, Optional, Any
from datetime import datetime
import json

def format_timestamp(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def sats_to_btc(sats: int) -> float:
    return sats / 100000000.0

def btc_to_sats(btc: float) -> int:
    return int(btc * 100000000)

def format_btc_amount(sats: int, include_unit: bool = True) -> str:
    btc = sats_to_btc(sats)
    if include_unit:
        return f"{btc:.8f} BTC"
    return f"{btc:.8f}"

def filter_logs_by_action(logs: List[Dict], action: str) -> List[Dict]:
    return [log for log in logs if log.get("action") == action]

def filter_logs_by_status(logs: List[Dict], status: str) -> List[Dict]:
    return [log for log in logs if log.get("status") == status]

def calculate_success_rate(logs: List[Dict]) -> float:
    if not logs:
        return 0.0
    
    success_count = len([log for log in logs if log.get("status") == "success"])
    return (success_count / len(logs)) * 100.0

def parse_clarity_value(clarity_value: Dict) -> Any:
    if not clarity_value:
        return None
    
    value_type = clarity_value.get("type")
    value = clarity_value.get("value")
    
    if value_type == "uint":
        return int(value)
    elif value_type == "bool":
        return value.lower() == "true"
    elif value_type == "string-ascii" or value_type == "string-utf8":
        return value
    elif value_type == "optional":
        if value is None:
            return None
        return parse_clarity_value(value)
    elif value_type == "tuple":
        result = {}
        for key, val in value.items():
            result[key] = parse_clarity_value(val)
        return result
    elif value_type == "list":
        return [parse_clarity_value(item) for item in value]
    else:
        return value

def format_clarity_response(response: Dict) -> Dict:
    if "value" in response:
        return parse_clarity_value(response["value"])
    return response
