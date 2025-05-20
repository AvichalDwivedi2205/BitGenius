import os
import google.generativeai as genai
from typing import Dict, List, Optional

class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def generate_agent_names(self, goal: str, count: int = 5) -> List[str]:
        """Generate agent name suggestions based on a goal"""
        prompt = f"Suggest {count} creative and descriptive names for a Bitcoin trading agent with this goal: {goal}. Return only the names as a comma-separated list without numbering or explanations."
        
        response = await self.model.generate_content_async(prompt)
        
        names_text = response.text.strip()
        names = [name.strip() for name in names_text.split(",")]
        
        return names[:count]  
    
    async def validate_trigger(self, trigger: str) -> Dict:
        """Validate and analyze a trigger condition"""
        prompt = f"""
        Analyze this Bitcoin agent trigger condition: "{trigger}"
        
        Check for:
        1. Syntax errors
        2. Logical consistency
        3. Clarity compatibility
        
        Return a JSON with these fields:
        - valid: boolean indicating if the trigger is valid
        - errors: array of error messages (empty if valid)
        - suggestions: array of improvement suggestions
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            import json
            return json.loads(response.text)
        except:
            return {
                "valid": False,
                "errors": ["Could not parse AI response"],
                "suggestions": ["Try simplifying your trigger condition"]
            }
    
    async def summarize_logs(self, logs: List[Dict]) -> Dict:
        """Summarize a set of agent logs and add insights"""
        if not logs:
            return {"summary": "No logs to summarize", "insights": []}
        
        logs_text = "\n".join([
            f"Log {i+1}: {log.get('action', 'Unknown')} - {log.get('status', 'Unknown')} - {log.get('details', 'No details')}"
            for i, log in enumerate(logs[:10])  # Limit to 10 logs
        ])
        
        prompt = f"""
        Analyze these Bitcoin agent logs and provide a summary and insights:
        
        {logs_text}
        
        Return a JSON with these fields:
        - summary: a concise summary of agent activity
        - insights: array of insights or recommendations
        - tags: array of relevant tags for these logs
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            import json
            return json.loads(response.text)
        except:
            return {
                "summary": "Log analysis completed",
                "insights": ["Could not generate detailed insights"],
                "tags": ["agent-activity"]
            }
    
    async def get_ai_help(self, context: str) -> Dict:
        """Get AI help and tips based on context"""
        prompt = f"""
        Provide helpful tips and guidance for a user working with a Bitcoin agent platform.
        
        Current context: {context}
        
        Return a JSON with these fields:
        - title: a short, helpful title
        - tips: array of helpful tips (3-5 items)
        - example: a relevant example if applicable
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            import json
            return json.loads(response.text)
        except:
            return {
                "title": "Tips for Bitcoin Agents",
                "tips": ["Start with small allocations", "Test your strategy thoroughly", "Monitor performance regularly"],
                "example": "Example: A DCA strategy that buys $10 of BTC weekly"
            }

gemini_client = GeminiClient()
