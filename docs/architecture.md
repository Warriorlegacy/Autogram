# Architecture

## Overview

`Warriorlegacy/Autogram` is an autonomous automation platform combining:
- **Agent System** — Autonomous agents with memory, tools, and guardrails
- **Workflow Engine** — Event-driven workflow orchestration with retries and human-in-the-loop
- **Dashboard** — Real-time monitoring and management
- **Billing** — Per-workflow usage metering

## Tech Stack

- **Runtime:** Python 3.11+
- **Backend:** Python (orchestrator + pipeline runner)
- **Frontend:** HTML/CSS/JS dashboard
- **Database:** PostgreSQL/SQLite (Docker)
- **AI:** OpenAI/Anthropic/Google (provider-agnostic gateway)
- **Testing:** pytest + GitHub Actions (9 workflows)
- **Deployment:** Docker + Render + Fly.io

## Directory Structure

```
orchestrator.py      Workflow orchestration (state machine)
pipeline_runner.py   Pipeline execution (async, retry, checkpoint)
dashboard_api.py     Dashboard API (monitoring, management)

agents/              Agent definitions, prompts, memory
workflows/           Workflow definitions (triggers, conditions, steps)
tools/               Tool definitions, MCP integration
memory/              Short/working/persistent memory
billing/             Usage metering, cost tracking
evaluation/          Eval datasets, benchmarks
observability/       Traces, logs, metrics
guardrails/          Input/output validation, safety
events/              Event bus, triggers, schedules
```

## AI-Native Pipeline

```
USER / EVENT / SCHEDULE
  → INTENT DETECTION
  → CONTEXT RETRIEVAL
  → PLANNING
  → AGENT / WORKFLOW EXECUTION
  → TOOL CALLS
  → VALIDATION
  → OPTIONAL HUMAN APPROVAL
  → ACTION
  → OBSERVABILITY
  → RESULT
  → FEEDBACK
  → OPTIMIZATION
```

## Security

See [SECURITY.md](SECURITY.md).

## Testing

- pytest test suite
- 9 GitHub Actions workflows
- Integration tests for workflows
- Contract tests for API

## License

None — consider adding MIT or Apache-2.0.
