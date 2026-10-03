# Using this outside Claude

Nothing here is Claude-proprietary. `SKILL.md` and `references/*.md` are plain instructions written for an LLM to read and follow; `scripts/*.py` are ordinary, dependency-free Python. This doc covers using both outside Claude Code/claude.ai.

## 1. As a system prompt for any LLM agent

Claude Code loads `SKILL.md` and only pulls in a `references/*.md` file when it decides it's relevant (progressive disclosure). Most other frameworks (a custom GPT, a LangChain/LlamaIndex agent, an AutoGen agent, a raw API call to any model) don't have that lazy-loading mechanism — you generally hand them one system prompt up front. So for those, flatten everything into one file:

```bash
python3 tools/build_context_bundle.py
# writes dist/ai-requirements-analyst.full.md
```

Then paste that file's contents (or point your framework's system-prompt file at it) wherever your agent's system/developer prompt goes:

- **OpenAI Custom GPT / Assistants API**: paste into the GPT's "Instructions" field or the Assistant's `instructions` parameter. It's long, so if your platform has an instruction-length limit, trim `references/examples.md` first — it's illustrative, not load-bearing.
- **LangChain / LlamaIndex**: use it as the `SystemMessage` / system prompt template for your agent or chain.
- **AutoGen**: use it as the `system_message` for the relevant `ConversableAgent`.
- **Cursor / Windsurf / other IDE agents**: drop it in as a project rules file (e.g. `.cursor/rules/requirements-analyst.md` or your tool's equivalent) so it applies automatically in that repo.
- **Any raw API call** (OpenAI, Gemini, open-weight models via vLLM/Ollama, etc.): pass it as the system message on every request in the conversation.

The bundle is self-contained Markdown — no special syntax, no Claude-specific tool-calling assumptions. The "tool architecture" and "evidence model" sections describe *what a tool-using agent should do*, not a Claude-specific API, so they translate directly to whatever tool-calling mechanism your framework uses (OpenAI function calling, LangChain tools, etc.) — just make sure your agent's actual tools (file read, repo search, DB query) are described to it with names/purposes similar enough that it can map the guidance in `tool-architecture.md` onto them.

## 2. The validation/reporting scripts — pure CLI, no Claude dependency

`scripts/validate_ids.py`, `scripts/validate_requirements.py`, and `scripts/generate_report.py` are plain Python 3 (standard library only). Call them from any pipeline, regardless of which model produced the document:

```bash
python3 skills/ai-requirements-analyst/scripts/validate_ids.py path/to/doc.md
python3 skills/ai-requirements-analyst/scripts/validate_requirements.py path/to/doc.md
python3 skills/ai-requirements-analyst/scripts/generate_report.py path/to/data.json --format markdown
```

Exit codes are 0/1 (clean/errors found), so they drop straight into CI: run them as a post-processing step on whatever your agent produces, in a Node/Python/whatever pipeline, with no Claude API calls involved.

### Example: wiring into a non-Claude agent pipeline

```python
import subprocess

# after your agent (any model) produces requirements_doc.md
result = subprocess.run(
    ["python3", "skills/ai-requirements-analyst/scripts/validate_ids.py", "requirements_doc.md"],
    capture_output=True, text=True,
)
if result.returncode != 0:
    print("ID validation failed:\n", result.stdout)
```

## 3. MCP-style tool integration (any MCP-compatible client)

The instructions in `references/tool-architecture.md` describe tool *categories* (file, repository, database, API, project-management, CRM) and a permission model (read-only by default) rather than a fixed tool list — so they work whether the tools are wired up through Claude's connector system, a raw MCP server, or a hand-rolled function-calling setup in another framework. If you're building an MCP server to back this skill for a non-Claude MCP client, name your tools close to the ones listed in that file (`list_project_files`, `inspect_repository`, `inspect_database_schema`, etc.) so the instructions map onto them without edits.

## 4. What doesn't carry over

- **Claude Code's plugin mechanics** (`.claude-plugin/`, `claude plugin install`, `${CLAUDE_PLUGIN_ROOT}`) are Claude Code-specific and irrelevant outside it — ignore that folder entirely for non-Claude use.
- **Automatic skill triggering** (Claude deciding on its own when to consult `SKILL.md` based on its `description`) has no equivalent in a single-system-prompt setup — if your other agent handles multiple tasks, you'll need your own routing logic to decide when to hand it this system prompt versus another one, or you'll need to always include it and rely on the instructions' own "does this need tools at all?" step to keep it from over-triggering.
