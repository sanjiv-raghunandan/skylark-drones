import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from agent.tools import get_all_tools
from agent.prompts import COORDINATOR_SYSTEM_PROMPT


class DroneCoordinatorAgent:
    """Main agent orchestrator using LangGraph and Groq."""
    
    def __init__(self, sheets_service, conflict_detector):
        """Initialize the agent with services and LLM."""
        self.sheets_service = sheets_service
        self.conflict_detector = conflict_detector
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Get all tools
        tools = get_all_tools(sheets_service, conflict_detector)
        
        # Create LangGraph ReAct agent (no state_modifier parameter)
        self.agent = create_react_agent(self.llm, tools)
        
        # Store system prompt separately
        self.system_message = SystemMessage(content=COORDINATOR_SYSTEM_PROMPT)
    
    def run(self, query: str) -> str:
        """Run the agent with a user query."""
        try:
            # Invoke the agent with system message prepended
            result = self.agent.invoke({
                "messages": [
                    self.system_message,
                    ("user", query)
                ]
            })
            
            # Extract the final response
            messages = result.get("messages", [])
            if messages:
                # Get the last AI message
                for msg in reversed(messages):
                    if hasattr(msg, 'content') and msg.type == 'ai':
                        return msg.content
                # Fallback to last message
                return messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
            
            return "No response generated."
            
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower():
                return "❌ Error: Groq API key not configured. Please add GROQ_API_KEY to .env file."
            elif "rate limit" in error_msg.lower():
                return "⚠️ Rate limit reached. Please wait a moment and try again."
            else:
                return f"❌ Error: {error_msg}"
    
    def get_pilots_data(self):
        """Get current pilots data for UI display."""
        return self.sheets_service.get_pilots()
    
    def get_drones_data(self):
        """Get current drones data for UI display."""
        return self.sheets_service.get_drones()
    
    def get_missions_data(self):
        """Get current missions data for UI display."""
        return self.sheets_service.get_missions()