# AI architecture

## Discovering AI components in an existing system
Detect LLM APIs, local models, agent frameworks, RAG, vector databases, embeddings, prompts, tool calling, MCP, AI workflows, evaluation frameworks. Apply the declared-versus-used distinction from `references/evidence-model.md`.
Record each component:
AI component | Purpose | Model | Input | Output | Tools | Knowledge | State | Evaluation | Risks.

## Reconstructing the flow
User -> application -> agent -> prompt -> model -> tools -> knowledge -> external systems. Fill each hop from evidence only; mark unseen hops Unknown.

## Designing AI parts
AI is added only when a requirement needs it. State the model strategy (hosted vs local, fallback), how knowledge is supplied, how tools are permissioned, how outputs are evaluated, and what happens when the model fails. Recommend an AI evaluation approach in the testing strategy.
