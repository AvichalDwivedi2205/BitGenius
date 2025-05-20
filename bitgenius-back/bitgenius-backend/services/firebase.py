import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional, Any
from datetime import datetime

db = None

def initialize_firebase():
    global db
    
    if firebase_admin._apps:
        return
    
    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise

class FirestoreClient:
    def __init__(self):
        global db
        if not db:
            initialize_firebase()
        self.db = db
    
    def store_agent_log(self, agent_id: int, log_data: Dict) -> str:

        if "timestamp" not in log_data:
            log_data["timestamp"] = int(datetime.now().timestamp())
        

        agent_id_str = str(agent_id)
        
        doc_ref = self.db.collection("agent-logs").document(agent_id_str).collection("logs").document()
        doc_ref.set(log_data)
        
        return doc_ref.id
    
    def get_agent_logs(self, agent_id: int, limit: int = 10) -> List[Dict]:
        agent_id_str = str(agent_id)
        
        logs_ref = (
            self.db.collection("agent-logs")
            .document(agent_id_str)
            .collection("logs")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        logs = []
        for doc in logs_ref.stream():
            log_data = doc.to_dict()
            log_data["id"] = doc.id
            logs.append(log_data)
        
        return logs
    
    def get_agent_logs_by_range(self, agent_id: int, start_time: int, end_time: int) -> List[Dict]:
        agent_id_str = str(agent_id)
        
        logs_ref = (
            self.db.collection("agent-logs")
            .document(agent_id_str)
            .collection("logs")
            .where("timestamp", ">=", start_time)
            .where("timestamp", "<=", end_time)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        
        logs = []
        for doc in logs_ref.stream():
            log_data = doc.to_dict()
            log_data["id"] = doc.id
            logs.append(log_data)
        
        return logs
    
    def update_agent_status(self, agent_id: int, status: str) -> None:
        agent_id_str = str(agent_id)
        
        self.db.collection("agents").document(agent_id_str).set(
            {"status": status, "updated_at": int(datetime.now().timestamp())},
            merge=True
        )
    
    def get_agent_status(self, agent_id: int) -> Dict:
        agent_id_str = str(agent_id)
        
        doc = self.db.collection("agents").document(agent_id_str).get()
        if doc.exists:
            return doc.to_dict()
        return {"status": "unknown"}
    
    def store_notification(self, user: str, notification: Dict) -> str:
        if "timestamp" not in notification:
            notification["timestamp"] = int(datetime.now().timestamp())
        
        doc_ref = self.db.collection("notifications").document(user).collection("items").document()
        doc_ref.set(notification)
        
        return doc_ref.id
    
    def get_notifications(self, user: str, limit: int = 10) -> List[Dict]:
        notifications_ref = (
            self.db.collection("notifications")
            .document(user)
            .collection("items")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        notifications = []
        for doc in notifications_ref.stream():
            notification = doc.to_dict()
            notification["id"] = doc.id
            notifications.append(notification)
        
        return notifications
    
    def mark_notification_as_read(self, user: str, notification_id: str) -> None:
        self.db.collection("notifications").document(user).collection("items").document(notification_id).update(
            {"read": True}
        )

firestore_client = FirestoreClient()
