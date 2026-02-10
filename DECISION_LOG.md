# Decision Log - Drone Operations Coordinator AI Agent

**Author**: [Your Name]  
**Date**: February 10, 2026  
**Assignment Duration**: 6 hours

---

## Executive Summary

This document outlines the key architectural decisions, assumptions, and trade-offs made during the development of the Drone Operations Coordinator AI Agent for Skylark Drones.

---

## 1. Key Assumptions

### Data Structure Assumptions
- **Pilot IDs follow pattern P001, P002...** to enable regex validation
- **Drone IDs follow pattern D001, D002...** for consistent identification
- **Project IDs use PRJ001, PRJ002...** format for clarity
- **Date format is YYYY-MM-DD** across all data sources
- **Skills and certifications are comma-separated** strings in CSV/Sheets
- **Status values are standardized**: Available/On Leave/Assigned for pilots, Available/Maintenance/Assigned for drones

### Google Sheets Assumptions
- User uploads CSVs to Google Sheets with exact tab names: "Pilot Roster", "Drone Fleet", "Missions"
- Sheet structure matches CSV column headers exactly
- Service account has Editor permissions on the sheet
- Updates to status fields sync within seconds

### Operational Assumptions
- **Current date is February 10, 2026** for conflict detection
- Pilots and drones can only be assigned to one project at a time
- Location matching is exact string match (no fuzzy matching)
- Maintenance overrides any assignment attempts
- Skills must include all required skills (not just partial match for conflict detection)

---

## 2. Technology Stack Decisions

### Why LangChain + ReAct Agent?
**Decision**: Use LangChain's ReAct (Reasoning + Acting) agent pattern

**Rationale**:
- **Tool orchestration**: ReAct agent can reason about which tools to use and in what sequence
- **Multi-step reasoning**: Complex queries like "find best pilot for urgent project" require chaining multiple tools
- **Flexibility**: Easy to add new tools without rewriting core logic
- **Conversation memory**: Built-in memory management for context-aware responses

**Alternative Considered**: 
- Custom rule-based system → Rejected: Too rigid, hard to extend
- LangGraph → Rejected: Overkill for this scope, steeper learning curve

### Why Groq for LLM?
**Decision**: Use Groq API with Llama 3.1 70B model

**Rationale**:
- **100% free** with generous rate limits (15 req/min, 6000 req/day)
- **Fastest inference** in the market (~100 tokens/sec)
- **No credit card required** for signup
- **Good tool calling capability** with Llama 3.1
- **Cloud-based** so works on Streamlit Cloud deployment

**Alternatives Considered**:
- Ollama (local) → Rejected: Can't run on Streamlit Cloud
- OpenAI → Rejected: Costs money
- Google Gemini → Considered: Good free option but Groq is faster

### Why Streamlit?
**Decision**: Use Streamlit for UI

**Rationale**:
- **Free hosting** on Streamlit Community Cloud
- **Chat interface** built-in with `st.chat_message` and `st.chat_input`
- **Fast development**: Pure Python, no frontend code needed
- **Data visualization**: Built-in dataframe display for dashboards
- **Secrets management**: Native support for API keys and credentials

**Alternatives Considered**:
- Gradio → Similar but less mature ecosystem
- Flask + React → Too much overhead for 6-hour timeline

### Why Google Sheets for Data Storage?
**Decision**: Use Google Sheets as database with 2-way sync

**Rationale**:
- **Assignment requirement**: Must demonstrate 2-way sync
- **Free and simple**: No database hosting needed
- **Familiar interface**: Stakeholders can view/edit data directly
- **Real-time collaboration**: Multiple users can view updates
- **API maturity**: gspread library is stable and well-documented

**Alternatives Considered**:
- Airtable → Similar but requires different API
- PostgreSQL → Overkill for assignment, requires hosting
- Firebase → Good option but Sheets is simpler

---

## 3. Architecture Decisions

### Layered Architecture
**Decision**: Separate concerns into Agent → Services → Data layers

**Rationale**:
- **Maintainability**: Each layer has single responsibility
- **Testability**: Can mock services for agent testing
- **Extensibility**: Easy to swap Google Sheets for different backend
- **Clarity**: Clear flow from user query → agent → tools → services → data

### Custom LangChain Tools
**Decision**: Build 7 custom tools (query_pilots, update_pilot_status, etc.)

**Rationale**:
- **Granular control**: Each tool does one thing well
- **Composability**: Agent can chain tools for complex queries
- **Error handling**: Tool-level error messages for debugging
- **Type safety**: Pydantic schemas validate inputs

**Tool Design Philosophy**:
- Input via JSON strings for flexibility
- Return human-readable strings (agent formats for user)
- All updates return success/failure confirmations
- Conflicts return detailed lists, not just boolean

### Conflict Detection Strategy
**Decision**: Comprehensive conflict checking with 10+ rules

**Rules Implemented**:
1. Pilot already assigned
2. Pilot on leave
3. Skill mismatch
4. Certification mismatch
5. Pilot-drone location mismatch
6. Pilot-project location mismatch
7. Drone in maintenance
8. Drone already assigned
9. Date overlap detection
10. Capability mismatch (e.g., thermal requirement)

**Rationale**:
- **Safety first**: Better to over-check than miss conflicts
- **Detailed feedback**: Users understand why assignment fails
- **Edge case coverage**: Handles all scenarios in requirements

---

## 4. Urgent Reassignments Interpretation

### Interpretation
**"Urgent reassignments" means**:
1. When a pilot becomes unavailable (sick, emergency), quickly find replacement
2. When urgent priority project arrives, reallocate resources from lower priority
3. Automated candidate scoring based on:
   - Skill match (weighted 2x)
   - Location match (weighted 5 points)
   - Availability status
   - Drone availability in same location

### Implementation Approach
**Decision**: Build `find_urgent_reassignment_candidates` function in ConflictDetector

**Features**:
- Queries all available pilots
- Scores based on skill/location match
- Returns top 5 candidates with drones
- Agent can present options for human decision

**Why This Approach**:
- **Human-in-the-loop**: Agent suggests, human confirms
- **Transparent scoring**: Users see why candidates are ranked
- **Conflict-aware**: Still runs conflict detection before final assignment

**Alternatives Considered**:
- Fully automated reassignment → Rejected: Too risky without approval
- Manual search only → Rejected: Doesn't leverage AI capabilities

---

## 5. Trade-offs & Compromises

### What I Sacrificed for Speed

| **Feature** | **Current State** | **Production Would Need** |
|------------|------------------|---------------------------|
| **Authentication** | None | Role-based access control |
| **Logging** | Print statements | Structured logging (ELK stack) |
| **Testing** | Manual testing | Unit + integration tests |
| **Database** | Google Sheets | PostgreSQL/MongoDB |
| **Caching** | Simple in-memory | Redis |
| **Error recovery** | Basic try-catch | Retry logic, circuit breakers |
| **Monitoring** | None | APM (DataDog, New Relic) |
| **Rate limiting** | Groq's limits | Custom rate limiter |
| **Audit trail** | None | Full change history |

### Known Limitations

1. **Google Sheets Scale**: Won't scale beyond ~10,000 rows
   - **Solution for production**: Migrate to real database

2. **Concurrent Updates**: Race conditions possible with multiple users
   - **Solution**: Implement optimistic locking or use database transactions

3. **LLM Reliability**: Agent might hallucinate or fail to use tools correctly
   - **Solution**: Add validation layer, human confirmation for critical actions

4. **No Offline Mode**: Requires internet for LLM and Sheets
   - **Solution**: Local LLM + local DB cache with sync

5. **Simple Skill Matching**: Exact string match only
   - **Solution**: NLP-based skill similarity, ontology mapping

---

## 6. What I'd Do Differently With More Time

### Week 1: Testing & Reliability
- **Unit tests** for all tools and services (pytest)
- **Integration tests** for end-to-end flows
- **Load testing** to understand breaking points
- **Error simulation** to improve handling

### Week 2: Features
- **Natural date parsing**: "next Monday" instead of "2026-02-17"
- **Fuzzy skill matching**: "mapping" matches "aerial mapping"
- **Notification system**: Email/Slack alerts for urgent assignments
- **Audit log**: Track all changes with timestamps and reasons
- **Undo functionality**: Rollback recent changes

### Week 3: UX Improvements
- **Voice interface**: Enable voice queries (Whisper API)
- **Visualizations**: Gantt charts for project timelines, map view for locations
- **Bulk operations**: Assign multiple pilots at once
- **What-if analysis**: "What if I assign P001 to PRJ003?"
- **Mobile optimization**: Responsive design for tablets

### Week 4: Infrastructure
- **Migrate to PostgreSQL** for data storage
- **Add Redis** for caching and rate limiting
- **Implement proper auth** with OAuth2
- **Set up CI/CD** pipeline (GitHub Actions)
- **Add monitoring** and alerting

---

## 7. Success Metrics

### Assignment Goals Met ✅
- ✅ Conversational interface working
- ✅ 2-way Google Sheets sync (read all, write status updates)
- ✅ All 4 core features implemented (roster, assignment, inventory, conflicts)
- ✅ Edge cases handled (overlaps, mismatches, maintenance, location)
- ✅ Urgent reassignments interpreted and implemented
- ✅ Deployable to free hosting (Streamlit Cloud)
- ✅ No costs for LLM or hosting
- ✅ Decision log documenting choices

### What Makes This AI Agent (Not Just CRUD App)
1. **Natural language understanding**: Parses ambiguous queries
2. **Tool orchestration**: Decides which tools to use and when
3. **Multi-step reasoning**: Chains operations for complex tasks
4. **Context awareness**: Remembers conversation history
5. **Adaptive responses**: Explains conflicts, suggests alternatives

---

## 8. Lessons Learned

### Technical Insights
- **LangChain agents are powerful but debugging is hard** → Added verbose logging
- **Google Sheets API has rate limits** → Implemented caching
- **Groq is surprisingly fast** → No noticeable latency even on free tier
- **Streamlit caching is critical** → Used `@st.cache_resource` for agent initialization

### Process Insights
- **Start with data modeling** → Clear data structures prevented rework
- **Tool design matters** → Granular tools are easier to compose
- **Test early with real queries** → Caught prompt engineering issues
- **Documentation while coding** → This decision log was written alongside code

---

## 9. Conclusion

This implementation demonstrates a production-viable prototype of an AI agent for drone operations coordination. The core functionality is solid, the architecture is extensible, and the system meets all assignment requirements while maintaining zero cost for deployment and operation.

The trade-offs made prioritize **speed of development** and **assignment requirements** over enterprise features, which is appropriate for a 6-hour technical assessment. The architecture provides a clear path to scale and productionize if needed.

**Total Development Time**: ~6 hours  
**Lines of Code**: ~1,500  
**External Dependencies**: 9 Python packages, all free  
**Monthly Operating Cost**: $0.00  

---

**Submitted with confidence that this solution effectively demonstrates the value of AI agents in operational coordination roles.**
