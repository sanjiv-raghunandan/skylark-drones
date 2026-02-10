# 🚁 Drone Operations Coordinator AI Agent

An intelligent AI agent built with LangChain and Streamlit to automate drone operations coordination for Skylark Drones. The agent handles pilot roster management, drone fleet inventory, mission assignment, and conflict detection through a conversational interface.

## 🌟 Features

### 1. **Roster Management**
- Query pilot availability by skill, certification, and location
- View current assignments in real-time
- Update pilot status (Available/On Leave/Assigned) with Google Sheets sync

### 2. **Assignment Tracking**
- Match pilots to projects based on requirements
- Track active assignments across fleet
- Handle reassignments with conflict detection

### 3. **Drone Inventory**
- Query fleet by capability, availability, and location
- Track deployment status and maintenance schedules
- Update drone status with Google Sheets sync

### 4. **Conflict Detection**
- Double-booking detection (overlapping dates)
- Skill/certification mismatch warnings
- Location mismatch alerts (pilot-drone-project)
- Maintenance status validation

### 5. **Urgent Reassignments**
- Automated candidate scoring and ranking
- Priority-based reassignment recommendations
- Real-time availability checks

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Streamlit UI (app.py)            │  ← User Interface
│   - Chat interface                  │
│   - Data dashboards                 │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   LangChain Agent Layer            │  ← Orchestration
│   - ReAct Agent                     │
│   - Tool selection & execution      │
│   - Conversation memory             │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Custom Tools                      │  ← Business Logic
│   - query_pilots                    │
│   - update_pilot_status             │
│   - query_drones                    │
│   - update_drone_status             │
│   - query_missions                  │
│   - detect_conflicts                │
│   - match_pilot_to_project          │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   Services Layer                    │  ← Data & Logic
│   - GoogleSheetsService (2-way sync)│
│   - ConflictDetector                │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│   External Services                 │  ← Infrastructure
│   - Groq API (Free LLM)            │
│   - Google Sheets API               │
└─────────────────────────────────────┘
```

## 🛠️ Tech Stack

- **UI Framework**: Streamlit (Python web app)
- **Agent Framework**: LangChain (ReAct agent with custom tools)
- **LLM**: Groq API (llama-3.1-70b-versatile) - **100% FREE**
- **Data Storage**: Google Sheets (2-way sync)
- **Deployment**: Streamlit Community Cloud (FREE)

## 📋 Prerequisites

### Software to Install:
1. **Python 3.9+** - [Download](https://www.python.org/downloads/)
2. **Git** - [Download](https://git-scm.com/downloads)

### Free API Keys Needed:
1. **Groq API Key** (Free, no credit card)
   - Sign up at: https://console.groq.com
   - Create API key
   
2. **Google Cloud Service Account** (Free)
   - Create project at: https://console.cloud.google.com
   - Enable Google Sheets API
   - Create service account → Download JSON credentials

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/skylark-drones.git
cd skylark-drones
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Google Sheets
1. Upload the 3 CSV files to Google Sheets:
   - `pilot_roster.csv` → Sheet named "Pilot Roster"
   - `drone_fleet.csv` → Sheet named "Drone Fleet"
   - `missions.csv` → Sheet named "Missions"

2. Share the sheet with your service account email (from JSON):
   - Example: `your-service-account@project-id.iam.gserviceaccount.com`
   - Give **Editor** access

3. Copy the Sheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   ```

### 4. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env with your values:
GROQ_API_KEY=your_groq_api_key
GOOGLE_SHEET_ID=your_google_sheet_id
```

Place your Google service account JSON in:
```
config/service_account.json
```

### 5. Run Locally
```bash
streamlit run app.py
```

Open browser to: http://localhost:8501

## 🌐 Deploy to Streamlit Cloud (FREE)

### 1. Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Deploy
1. Go to: https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository
4. Main file: `app.py`
5. Click "Deploy"

### 3. Add Secrets
In Streamlit Cloud dashboard → Settings → Secrets:

```toml
# Groq API Key
GROQ_API_KEY = "your_groq_api_key_here"

# Google Sheet ID
GOOGLE_SHEET_ID = "your_google_sheet_id_here"

# Google Service Account (paste full JSON content)
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### 4. Access Your Live Demo
Your app will be available at: `https://your-app-name.streamlit.app`

## 📖 Usage Examples

### Query Operations
```
"Show me all available pilots in Bangalore"
"Which pilots have mapping and survey skills?"
"List all drones with thermal capability"
"Show urgent priority missions"
```

### Update Operations
```
"Update pilot P001 status to On Leave"
"Set drone D002 to Maintenance status"
"Mark pilot P003 as Available from 2026-02-15"
```

### Assignment & Conflict Detection
```
"Find pilots suitable for project PRJ001"
"Check conflicts for assigning pilot P001, drone D001 to project PRJ002"
"Can we assign Arjun to the urgent Mumbai project?"
```

### Urgent Reassignments
```
"I need to handle an urgent reassignment for PRJ002"
"Find replacement for pilot P002 currently on Client A project"
```

## 📁 Project Structure

```
skylark-drones/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
│
├── agent/                          # LangChain agent layer
│   ├── __init__.py
│   ├── coordinator_agent.py        # Main agent orchestrator
│   ├── tools.py                    # Custom LangChain tools
│   └── prompts.py                  # System prompts
│
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── google_sheets.py           # Google Sheets 2-way sync
│   └── conflict_detector.py        # Conflict detection logic
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   └── validators.py               # Input validation
│
├── config/                         # Configuration
│   └── service_account.json        # Google credentials (gitignored)
│
├── pilot_roster.csv                # Sample pilot data
├── drone_fleet.csv                 # Sample drone data
├── missions.csv                    # Sample missions data
│
├── README.md                       # This file
└── DECISION_LOG.md                 # Design decisions & assumptions
```

## 🔧 Troubleshooting

### "Failed to initialize Google Sheets"
- Verify service account JSON is in `config/service_account.json`
- Check that Google Sheets API is enabled in your GCP project
- Ensure sheet is shared with service account email

### "Groq API key not configured"
- Verify `.env` file has `GROQ_API_KEY=your_key`
- For Streamlit Cloud, check secrets are configured correctly

### "No pilots/drones/missions found"
- Verify Google Sheet has correct tab names:
  - "Pilot Roster"
  - "Drone Fleet"
  - "Missions"
- Check that data rows exist (not just headers)

### "Rate limit reached"
- Groq free tier has rate limits
- Wait a moment and try again
- Consider upgrading to Groq Pro (still free for most usage)

## 🤝 Contributing

This is a technical assignment prototype. For production use, consider:
- Adding authentication/authorization
- Implementing proper logging and monitoring
- Adding unit and integration tests
- Scaling database beyond Google Sheets
- Adding webhook notifications

## 📄 License

MIT License - See LICENSE file

## 🙋‍♂️ Support

For questions or issues:
1. Check DECISION_LOG.md for design rationale
2. Review example queries in app expander
3. Verify all prerequisites are met

---

**Built with ❤️ for Skylark Drones Assignment**