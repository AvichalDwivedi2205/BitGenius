import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

db = None

def initialize_firebase():
    global db
    
    if firebase_admin._apps:
        return
    
    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "firebase_admin.json")
    
    try:
        # For test/dev environment, create a mock if file doesn't exist
        if not os.path.exists(cred_path):
            logging.warning(f"Firebase credentials file {cred_path} not found. Using mock implementation")
            db = MockFirestore()
            return
            
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        logging.warning(f"Error initializing Firebase: {e}. Using mock implementation")
        db = MockFirestore()

# Mock implementation for testing
class MockFirestore:
    def __init__(self):
        self.collections = {}
        
    def collection(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

class MockCollection:
    def __init__(self, name):
        self.name = name
        self.documents = {}
        
    def document(self, doc_id):
        if doc_id not in self.documents:
            self.documents[doc_id] = MockDocument(doc_id)
        return self.documents[doc_id]
    
    def where(self, field, op, value):
        return self
    
    def order_by(self, field, direction=None):
        return self
    
    def limit(self, n):
        return self
    
    def stream(self):
        return self.documents.values()

class MockDocument:
    def __init__(self, doc_id):
        self.id = doc_id
        self.data = {}
        self.collections = {}
    
    def collection(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]
    
    def set(self, data, merge=False):
        if merge:
            self.data.update(data)
        else:
            self.data = data
        return self
    
    def update(self, data):
        self.data.update(data)
        return self
    
    def get(self):
        return self
    
    def to_dict(self):
        return self.data
    
    @property
    def exists(self):
        return True

class FirestoreClient:
    def __init__(self):
        global db
        if not db:
            initialize_firebase()
        self.db = db
    
    def add_log(self, log_data: Dict) -> str:
        """Add a new log entry to Firebase"""
        agent_id = log_data.get("agent_id")
        if not agent_id:
            raise ValueError("agent_id is required")
            
        return self.store_agent_log(agent_id, log_data)
    
    def get_all_logs(self, limit: int = 50) -> List[Dict]:
        """Get logs from all agents, limited to the specified count"""
        try:
            # Query for all agent documents
            agents_ref = self.db.collection("agent-logs").limit(20)
            
            all_logs = []
            
            # For each agent, get their logs
            for agent_doc in agents_ref.stream():
                agent_id = agent_doc.id
                
                # Get logs for this agent
                logs_ref = (
                    self.db.collection("agent-logs")
                    .document(agent_id)
                    .collection("logs")
                    .order_by("timestamp", direction=firestore.Query.DESCENDING if hasattr(firestore.Query, 'DESCENDING') else None)
                    .limit(limit // 10)  # Divide limit across agents
                )
                
                for log_doc in logs_ref.stream():
                    log_data = log_doc.to_dict()
                    log_data["id"] = log_doc.id
                    log_data["agent_id"] = agent_id
                    all_logs.append(log_data)
            
            # Sort all logs by timestamp, descending
            all_logs.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            return all_logs[:limit]
        except Exception as e:
            logging.error(f"Error getting all logs: {e}")
            return []
    
    def store_agent_log(self, agent_id: int, log_data: Dict) -> str:
        try:
            if "timestamp" not in log_data:
                log_data["timestamp"] = int(datetime.now().timestamp())
            
            agent_id_str = str(agent_id)
            
            doc_ref = self.db.collection("agent-logs").document(agent_id_str).collection("logs").document()
            doc_ref.set(log_data)
            
            return doc_ref.id
        except Exception as e:
            logging.error(f"Error storing agent log: {e}")
            return "mock-log-id"
    
    def get_agent_logs(self, agent_id: int, limit: int = 10) -> List[Dict]:
        try:
            agent_id_str = str(agent_id)
            
            logs_ref = (
                self.db.collection("agent-logs")
                .document(agent_id_str)
                .collection("logs")
                .order_by("timestamp", direction=firestore.Query.DESCENDING if hasattr(firestore.Query, 'DESCENDING') else None)
                .limit(limit)
            )
            
            logs = []
            for doc in logs_ref.stream():
                log_data = doc.to_dict()
                log_data["id"] = doc.id
                logs.append(log_data)
            
            return logs
        except Exception as e:
            logging.error(f"Error getting agent logs: {e}")
            return []
    
    def get_agent_logs_by_range(self, agent_id: int, start_time: int, end_time: int) -> List[Dict]:
        try:
            agent_id_str = str(agent_id)
            
            logs_ref = (
                self.db.collection("agent-logs")
                .document(agent_id_str)
                .collection("logs")
                .where("timestamp", ">=", start_time)
                .where("timestamp", "<=", end_time)
                .order_by("timestamp", direction=firestore.Query.DESCENDING if hasattr(firestore.Query, 'DESCENDING') else None)
            )
            
            logs = []
            for doc in logs_ref.stream():
                log_data = doc.to_dict()
                log_data["id"] = doc.id
                logs.append(log_data)
            
            return logs
        except Exception as e:
            logging.error(f"Error getting agent logs by range: {e}")
            return []
    
    def update_agent_status(self, agent_id: int, status: str) -> None:
        try:
            agent_id_str = str(agent_id)
            
            self.db.collection("agents").document(agent_id_str).set(
                {"status": status, "updated_at": int(datetime.now().timestamp())},
                merge=True
            )
        except Exception as e:
            logging.error(f"Error updating agent status: {e}")
    
    def get_agent_status(self, agent_id: int) -> Dict:
        try:
            agent_id_str = str(agent_id)
            
            doc = self.db.collection("agents").document(agent_id_str).get()
            if doc.exists:
                return doc.to_dict()
            return {"status": "unknown"}
        except Exception as e:
            logging.error(f"Error getting agent status: {e}")
            return {"status": "unknown"}
    
    def store_notification(self, user: str, notification: Dict) -> str:
        try:
            if "timestamp" not in notification:
                notification["timestamp"] = int(datetime.now().timestamp())
            
            doc_ref = self.db.collection("notifications").document(user).collection("items").document()
            doc_ref.set(notification)
            
            return doc_ref.id
        except Exception as e:
            logging.error(f"Error storing notification: {e}")
            return "mock-notification-id"
    
    def get_notifications(self, user: str, limit: int = 10) -> List[Dict]:
        try:
            notifications_ref = (
                self.db.collection("notifications")
                .document(user)
                .collection("items")
                .order_by("timestamp", direction=firestore.Query.DESCENDING if hasattr(firestore.Query, 'DESCENDING') else None)
                .limit(limit)
            )
            
            notifications = []
            for doc in notifications_ref.stream():
                notification = doc.to_dict()
                notification["id"] = doc.id
                notifications.append(notification)
            
            return notifications
        except Exception as e:
            logging.error(f"Error getting notifications: {e}")
            return []
    
    def mark_notification_as_read(self, user: str, notification_id: str) -> None:
        try:
            self.db.collection("notifications").document(user).collection("items").document(notification_id).update(
                {"read": True}
            )
        except Exception as e:
            logging.error(f"Error marking notification as read: {e}")

firestore_client = FirestoreClient()
