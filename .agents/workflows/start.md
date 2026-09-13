---
name: start
description: Instantly restore full repository context without burning discovery tokens
---

### Execution Protocol for AI Agent:
1. **Read Active State**: Read [`.agents/memory/ACTIVE_SESSION.md`](file:///d:/Autogram/.agents/memory/ACTIVE_SESSION.md) immediately.
2. **Review Codebase Structure**: If file paths or symbol locations are needed, read [`.agents/memory/ARCHITECTURE_MAP.md`](file:///d:/Autogram/.agents/memory/ARCHITECTURE_MAP.md).
3. **STRICT PROHIBITIONS**:
   - **DO NOT** run recursive directory listings (`ls -R`, `find .`, `Get-ChildItem -Recurse`).
   - **DO NOT** load multiple large source files into context unless specifically directed to edit them.
   - **DO NOT** ask the user to re-explain the project architecture.
4. **Confirmation Output**: Provide a 2-sentence confirmation acknowledging the current objective and the immediate next task, then await instructions.
