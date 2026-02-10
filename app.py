import streamlit as st
import os
from dotenv import load_dotenv
from agent.coordinator_agent import DroneCoordinatorAgent
from services.google_sheets import GoogleSheetsService
from services.conflict_detector import ConflictDetector

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Drone Operations Coordinator AI",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .dataframe {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_agent():
    """Initialize the agent and services (cached for performance)."""
    try:
        sheets_service = GoogleSheetsService()
        conflict_detector = ConflictDetector(sheets_service)
        agent = DroneCoordinatorAgent(sheets_service, conflict_detector)
        return agent, sheets_service
    except Exception as e:
        st.error(f"Failed to initialize: {str(e)}")
        st.info("💡 Make sure to configure Google Sheets credentials and Groq API key in Streamlit secrets.")
        return None, None


# Initialize
agent, sheets_service = initialize_agent()

# Header
st.markdown('<h1 class="main-header">🚁 Drone Operations Coordinator AI</h1>', unsafe_allow_html=True)
st.markdown("---")

if agent is None:
    st.stop()

# Sidebar - Data Views
with st.sidebar:
    st.header("📊 Current Status")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        sheets_service.refresh_all()
        st.cache_resource.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Tabs for different data views
    tab1, tab2, tab3 = st.tabs(["👨‍✈️ Pilots", "🚁 Drones", "📋 Missions"])
    
    with tab1:
        try:
            pilots_df = agent.get_pilots_data()
            st.dataframe(
                pilots_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Quick stats
            available = len(pilots_df[pilots_df['status'] == 'Available'])
            assigned = len(pilots_df[pilots_df['status'] == 'Assigned'])
            on_leave = len(pilots_df[pilots_df['status'] == 'On Leave'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Available", available, delta=None)
            col2.metric("Assigned", assigned)
            col3.metric("On Leave", on_leave)
            
        except Exception as e:
            st.error(f"Error loading pilots: {e}")
    
    with tab2:
        try:
            drones_df = agent.get_drones_data()
            st.dataframe(
                drones_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Quick stats
            available = len(drones_df[drones_df['status'] == 'Available'])
            assigned = len(drones_df[drones_df['status'] == 'Assigned'])
            maintenance = len(drones_df[drones_df['status'] == 'Maintenance'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Available", available)
            col2.metric("Assigned", assigned)
            col3.metric("Maintenance", maintenance)
            
        except Exception as e:
            st.error(f"Error loading drones: {e}")
    
    with tab3:
        try:
            missions_df = agent.get_missions_data()
            st.dataframe(
                missions_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Priority breakdown
            urgent = len(missions_df[missions_df['priority'] == 'Urgent'])
            high = len(missions_df[missions_df['priority'] == 'High'])
            standard = len(missions_df[missions_df['priority'] == 'Standard'])
            
            st.markdown("**Priority Breakdown:**")
            st.write(f"🔴 Urgent: {urgent}")
            st.write(f"🟡 High: {high}")
            st.write(f"🟢 Standard: {standard}")
            
        except Exception as e:
            st.error(f"Error loading missions: {e}")

# Main chat interface
st.header("💬 Chat with Coordinator Agent")

# Info box with examples
with st.expander("💡 Example Questions", expanded=False):
    st.markdown("""
    **Roster Management:**
    - "Show me all available pilots in Bangalore"
    - "Which pilots have mapping skills?"
    - "Update pilot P001 status to On Leave"
    
    **Assignment Tracking:**
    - "Find pilots suitable for project PRJ001"
    - "Who is assigned to Client A's project?"
    
    **Drone Inventory:**
    - "Show all available drones with thermal capability"
    - "Update drone D002 status to Maintenance"
    
    **Conflict Detection:**
    - "Check conflicts for assigning pilot P001, drone D001 to project PRJ002"
    - "Can we assign Arjun to the urgent project?"
    
    **Urgent Reassignments:**
    - "I need to handle an urgent reassignment for PRJ002"
    - "Find replacement for pilot P002 on Client A project"
    """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! I'm your Drone Operations Coordinator AI. I can help you with pilot assignments, drone inventory, mission coordination, and conflict detection. What would you like to know?"
        }
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about drone operations..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                response = agent.run(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.85rem;'>
    🚁 Skylark Drones Operations Coordinator | Powered by Groq (Llama 3.1) + LangChain + Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
