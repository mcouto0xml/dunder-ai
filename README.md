# Dunder Mifflin AI Agent System

Multi-agent system for expense management, fraud detection, and compliance checking.

## Architecture

### Orchestrator (Root Agent)
- **Location:** `src/orchestrator/`
- **Name:** `expense_orchestrator`
- **Role:** Main entry point that coordinates between specialized agents
- **Run with:** `adk run orchestrator`

The orchestrator routes user requests to the appropriate specialized agent:
- Fraud detection queries → AgentPandas
- Policy/compliance questions → agentCompliance
- Can coordinate both agents for complex requests

### AgentPandas (Fraud Detection)
- **Location:** `src/AgentPandas/`
- **Name:** `fraud_detector`
- **Role:** Analyzes CSV files from Google Cloud Storage for fraudulent transaction patterns
- **Exports:** `agent_pandas`, `root_agent` (points to agent_pandas)
- **Can run standalone:** Yes with `adk run AgentPandas`
- **Key Features:**
  - Downloads CSVs from GCS
  - Statistical analysis and baseline detection
  - Pattern detection (duplicates, threshold splitting, outliers)
  - Custom pandas code execution
  - Comprehensive fraud reports with severity levels

### agentCompliance (Policy Checker)
- **Location:** `src/agentCompliance/`
- **Name:** `agent_compliance`
- **Role:** Answers compliance policy questions using RAG over policy documents
- **Exports:** `agent_compliance`, `root_agent` (points to agent_compliance)
- **Can run standalone:** Yes with `adk run agentCompliance` (requires GCP auth for RAG)
- **Key Features:**
  - RAG-based policy retrieval
  - Grounded answers with evidence
  - Interprets spending limits, categories, and rules

## Running the System

### Option 1: Main Orchestrator (Recommended for complex workflows)
```bash
cd src
adk run orchestrator
```

Then interact with queries like:
- "Analyze gs://dunderai-transactions/expenses/jan-2024.csv for fraud"
- "Does the policy allow splitting a $1000 purchase?"
- "Check the CSV for fraud and tell me which violations break policy"

### Option 2: Individual Agents (Direct access to specialists)

**Fraud Detection Agent:**
```bash
cd src
adk run AgentPandas
```
Use for CSV fraud analysis queries directly.

**Compliance Agent:**
```bash
cd src
adk run agentCompliance
```
Use for policy questions directly.

All three agents can be run standalone with `adk run`!

## Project Structure

```
src/
├── orchestrator/          # Root agent - coordinates other agents
│   ├── __init__.py       # Exports: root_agent, run_orchestrator
│   ├── agent.py          # Main orchestrator logic
│   └── a.md              # Documentation
│
├── AgentPandas/          # Fraud detection specialist
│   ├── __init__.py       # Exports: agent_pandas, root_agent, analyze_csv_for_fraud
│   ├── agent.py          # Fraud detection agent (root_agent = agent_pandas)
│   ├── tools.py          # CSV analysis tools
│   └── a.md              # Documentation
│
├── agentCompliance/      # Policy compliance specialist
│   ├── __init__.py       # Exports: agent_compliance, root_agent, run_agent
│   ├── agent.py          # Compliance agent with RAG (root_agent = agent_compliance)
│   └── a.md              # Documentation
│
├── agentEmail/           # Email agent (future)
│   └── a.md
│
└── rag/                  # RAG infrastructure
    ├── config.py         # RAG corpus configuration
    ├── embedding.py      # Embedding utilities
    └── ingest.py         # Document ingestion

cache/                    # Downloaded CSV cache
example_usage.py          # Example scripts
```

## Configuration

All agents use:
- **Project:** `dunderai`
- **Location:** `us-west1`
- **Model (orchestrator):** `gemini-2.0-flash-exp`
- **Model (AgentPandas):** `gemini-2.0-flash-exp`
- **Model (agentCompliance):** `gemini-2.5-flash`

## Authentication

The system requires Google Cloud authentication:

```bash
# Set up Application Default Credentials
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

## Example Workflows

### 1. Fraud Detection
```
User: "Analyze january-2024.csv in dunderai-transactions for fraud"

Orchestrator → AgentPandas:
  1. Downloads CSV from GCS
  2. Previews data structure
  3. Calculates statistical baselines
  4. Runs fraud pattern detection
  5. Returns detailed report with severity levels
```

### 2. Policy Question
```
User: "Can I expense $400 in the 'Other' category?"

Orchestrator → agentCompliance:
  1. Uses RAG to retrieve relevant policy excerpts
  2. Grounds answer in compliance documents
  3. Returns answer with evidence and citations
```

### 3. Combined Analysis
```
User: "Check CSV for fraud and verify which findings violate policy"

Orchestrator:
  1. Calls AgentPandas for fraud detection
  2. Reviews fraud findings
  3. Calls agentCompliance for each major finding
  4. Synthesizes combined report
```

## Development

### Adding a New Agent

1. Create directory: `src/newAgent/`
2. Create `agent.py` with agent definition
3. Export in `__init__.py`:
   ```python
   from .agent import root_agent  # If standalone
   __all__ = ["root_agent"]
   ```
4. Update orchestrator to integrate (if needed)

### Testing

```bash
# Test imports
cd src
python -c "from orchestrator import root_agent; print(root_agent.name)"

# Test with ADK
adk run orchestrator
```

## Troubleshooting

**Error: "No root_agent found"**
- Ensure `agent.py` exports `root_agent`
- Check `__init__.py` imports it correctly

**Error: "DefaultCredentialsError"**
- Run `gcloud auth application-default login`
- Or set `GOOGLE_APPLICATION_CREDENTIALS`

**Error: RAG initialization fails**
- agentCompliance requires GCP auth
- orchestrator uses lazy imports to avoid this on startup
- Auth only needed when compliance tool is actually called

## Next Steps

- [ ] Implement agentEmail for email notifications
- [ ] Add session persistence
- [ ] Create web UI with `adk web`
- [ ] Add unit tests
- [ ] Deploy to Agent Engine
