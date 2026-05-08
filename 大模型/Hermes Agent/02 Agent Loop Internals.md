[toc]

原文: https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop

## Agent Loop Internals

The core orchestration engine is `run_agent.py`'s `AIAgent` class — roughly 13,700 lines that handle everything from prompt assembly to tool dispatch to provider failover.

核心编排引擎是 **run_agent.py** 中的 **AIAgent 类** —— 约 **13,700 行代码**，涵盖从提示词组装、工具分发到服务提供商故障转移的全部逻辑。

### Core Responsibilities

`AIAgent` is responsible for:

- Assembling the effective system prompt and tool schemas via `prompt_builder.py`
- Selecting the correct provider/API mode (chat_completions, codex_responses, anthropic_messages)
- Making interruptible model calls with cancellation support
- Executing tool calls (sequentially or concurrently via thread pool)
- Maintaining conversation history in OpenAI message format
- Handling compression, retries, and fallback model switching
- Tracking iteration budgets across parent and child agents
- Flushing persistent memory before context is lost

`AIAgent` 负责：

- 通过 `prompt_builder.py` 组装生效的系统提示词与工具 schema
- 选择正确的 provider/ API 模式（chat_completions、codex_responses、anthropic_messages）
- 发起**可中断**的模型调用，支持中途取消
- 执行工具调用（串行执行，或通过线程池并发执行）
- 以 OpenAI 消息格式维护对话历史
- 处理上下文压缩、重试与备用模型切换
- 跟踪parent agent 和child agent之间的迭代次数上限
- 在上下文丢失前**持久化写入记忆**

### Two Entry Points

```sh
# Simple interface — returns final response string
response = agent.chat("Fix the bug in main.py")

# Full interface — returns dict with messages, metadata, usage stats
result = agent.run_conversation(
    user_message="Fix the bug in main.py",
    system_message=None,           # auto-built if omitted
    conversation_history=None,      # auto-loaded from session if omitted
    task_id="task_abc123"
)
```

`chat()` is a thin wrapper around `run_conversation()` that extracts the `final_response` field from the result dict.

`chat()` 是对 `run_conversation()` 的**轻量封装**，它从结果字典中提取 `final_response` 字段。

### API Modes

Hermes supports three API execution modes, resolved from provider selection, explicit args, and base URL heuristics:

Hermes 支持三种 API 执行模式，这些模式通过**服务提供方选择、显式传入参数、基础 URL 启发式规则**共同确定：

| API mode             | Used for                                                     | Client type                           |
| -------------------- | ------------------------------------------------------------ | ------------------------------------- |
| `chat_completions`   | OpenAI-compatible endpoints (OpenRouter, custom, most providers) | `openai.OpenAI`                       |
| `codex_responses`    | OpenAI Codex / Responses API                                 | `openai.OpenAI` with Responses format |
| `anthropic_messages` | Native Anthropic Messages API                                | `anthropic.Anthropic` via adapter     |

The mode determines how messages are formatted, how tool calls are structured, how responses are parsed, and how caching/streaming works. All three converge on the same internal message format (OpenAI-style `role`/`content`/`tool_calls` dicts) before and after API calls.

模式决定了消息如何格式化、工具调用如何构造、响应如何解析，以及缓存与流式传输的实现方式。在 API 调用前后，三种模式最终都会统一为相同的**内部消息格式**（OpenAI 风格的 `role`/`content`/`tool_calls` 字典结构）。

**Mode resolution order:**

1. Explicit `api_mode` constructor arg (highest priority)
2. Provider-specific detection (e.g., `anthropic` provider → `anthropic_messages`)
3. Base URL heuristics (e.g., `api.anthropic.com` → `anthropic_messages`)
4. Default: `chat_completions`

**模式确定顺序：**

1. 显式传入的 `api_mode` 构造参数（最高优先级）
2. 服务提供方专属检测（例如：`anthropic` 提供方 → `anthropic_messages`）
3. 基础 URL 启发式判断（例如：`api.anthropic.com` → `anthropic_messages`）
4. 默认值：`chat_completions`

### Turn Lifecycle

Each iteration of the agent loop follows this sequence:

```sh
run_conversation()
  1. Generate task_id if not provided
  2. Append user message to conversation history
  3. Build or reuse cached system prompt (prompt_builder.py)
  4. Check if preflight compression is needed (>50% context)
  5. Build API messages from conversation history
     - chat_completions: OpenAI format as-is
     - codex_responses: convert to Responses API input items
     - anthropic_messages: convert via anthropic_adapter.py
  6. Inject ephemeral prompt layers (budget warnings, context pressure)
  7. Apply prompt caching markers if on Anthropic
  8. Make interruptible API call (_interruptible_api_call)
  9. Parse response:
     - If tool_calls: execute them, append results, loop back to step 5
     - If text response: persist session, flush memory if needed, return
```

#### Message Format

All messages use OpenAI-compatible format internally:

```sh
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "...", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

Reasoning content (from models that support extended thinking) is stored in `assistant_msg["reasoning"]` and optionally displayed via the `reasoning_callback`.

来自支持**扩展思考**的模型的推理内容，会被存储在 `assistant_msg["reasoning"]` 中，并可通过 `reasoning_callback` 选择性展示。

#### Message Alternation Rules

The agent loop enforces strict message role alternation:

- After the system message: `User → Assistant → User → Assistant → ...`
- During tool calling: `Assistant (with tool_calls) → Tool → Tool → ... → Assistant`
- **Never** two assistant messages in a row
- **Never** two user messages in a row
- **Only** `tool` role can have consecutive entries (parallel tool results)

Providers validate these sequences and will reject malformed histories.

智能体循环严格执行**消息角色交替规则**：

- 系统消息之后：`User → Assistant → User → Assistant → ...`
- 工具调用期间：`Assistant (with tool_calls) → Tool → Tool → ... → Assistant`
- **绝不**连续出现两条assistant消息
- **绝不**连续出现两条user消息
- **只有** `tool` role 允许连续出现（并行工具返回结果）

Providers会校验这些序列，并拒绝格式错误的对话历史。

### Interruptible API Calls

API requests are wrapped in `_interruptible_api_call()` which runs the actual HTTP call in a background thread while monitoring an interrupt event:

```sh
┌────────────────────────────────────────────────────┐
│  Main thread                  API thread           │
│                                                    │
│   wait on:                     HTTP POST           │
│    - response ready     ───▶   to provider         │
│    - interrupt event                               │
│    - timeout                                       │
└────────────────────────────────────────────────────┘
```

When interrupted (user sends new message, `/stop` command, or signal):

- The API thread is abandoned (response discarded)
- The agent can process the new input or shut down cleanly
- No partial response is injected into conversation history

### Tool Execution

#### Sequential vs Concurrent

When the model returns tool calls:

- **Single tool call** → executed directly in the main thread
- **Multiple tool calls** → executed concurrently via `ThreadPoolExecutor`
  - Exception: tools marked as interactive (e.g., `clarify`) force sequential execution
  - Results are reinserted in the original tool call order regardless of completion order

#### Execution Flow

```sh
for each tool_call in response.tool_calls:
    1. Resolve handler from tools/registry.py
    2. Fire pre_tool_call plugin hook
    3. Check if dangerous command (tools/approval.py)
       - If dangerous: invoke approval_callback, wait for user
    4. Execute handler with args + task_id
    5. Fire post_tool_call plugin hook
    6. Append {"role": "tool", "content": result} to history
```

#### Agent-Level Tools

Some tools are intercepted by `run_agent.py` *before* reaching `handle_function_call()`:

| Tool             | Why intercepted                                         |
| ---------------- | ------------------------------------------------------- |
| `todo`           | Reads/writes agent-local task state                     |
| `memory`         | Writes to persistent memory files with character limits |
| `session_search` | Queries session history via the agent's session DB      |
| `delegate_task`  | Spawns subagent(s) with isolated context                |

These tools modify agent state directly and return synthetic tool results without going through the registry.

这些工具会**直接修改智能体状态**，并直接返回构造的工具结果，**无需经过registry**。

### Callback Surfaces

`AIAgent` supports platform-specific callbacks that enable real-time progress in the CLI, gateway, and ACP integrations:

| Callback                 | When fired                                | Used by                                         |
| ------------------------ | ----------------------------------------- | ----------------------------------------------- |
| `tool_progress_callback` | Before/after each tool execution          | CLI spinner, gateway progress messages          |
| `thinking_callback`      | When model starts/stops thinking          | CLI "thinking..." indicator                     |
| `reasoning_callback`     | When model returns reasoning content      | CLI reasoning display, gateway reasoning blocks |
| `clarify_callback`       | When `clarify` tool is called             | CLI input prompt, gateway interactive message   |
| `step_callback`          | After each complete agent turn            | Gateway step tracking, ACP progress             |
| `stream_delta_callback`  | Each streaming token (when enabled)       | CLI streaming display                           |
| `tool_gen_callback`      | When tool call is parsed from stream      | CLI tool preview in spinner                     |
| `status_callback`        | State changes (thinking, executing, etc.) | ACP status updates                              |

### Budget and Fallback Behavior

#### Iteration Budget

The agent tracks iterations via `IterationBudget`:

- Default: 90 iterations (configurable via `agent.max_turns`)
- Each agent gets its own budget. Subagents get independent budgets capped at `delegation.max_iterations` (default 50) — total iterations across parent + subagents can exceed the parent's cap
- At 100%, the agent stops and returns a summary of work done

Agent通过 **IterationBudget** 跟踪迭代次数：

- 默认：**90 轮迭代**（可通过 `agent.max_turns` 配置）
- 每个agent拥有独立的迭代配额；Subagents配额独立，上限由 `delegation.max_iterations` 控制（默认 50）——**父 + 子总迭代次数可超过父智能体上限**
- 配额用尽时，agent停止运行并返回已完成工作的总结

#### Fallback Model

When the primary model fails (429 rate limit, 5xx server error, 401/403 auth error):

1. Check `fallback_providers` list in config
2. Try each fallback in order
3. On success, continue the conversation with the new provider
4. On 401/403, attempt credential refresh before failing over

The fallback system also covers auxiliary tasks independently — vision, compression, web extraction, and session search each have their own fallback chain configurable via the `auxiliary.*` config section.

当主模型调用失败时（429 请求限流、5xx 服务端错误、401/403 鉴权错误）：

1. 检查配置中的 `fallback_providers` 备用提供商列表
2. 按顺序依次尝试每个备用提供商
3. 若调用成功，切换到新提供商继续对话
4. 若遇到 401/403 错误，先尝试刷新凭证，再进行故障转移

该降级机制也**独立覆盖辅助任务**—— 视觉、上下文压缩、网页提取、会话检索，各自拥有独立的备用链路，可通过配置项 `auxiliary.*` 进行设置。

### Compression and Persistence

#### When Compression Triggers

- **Preflight** (before API call): If conversation exceeds 50% of model's context window
- **Gateway auto-compression**: If conversation exceeds 85% (more aggressive, runs between turns)

- **预检查**（API 调用前）：当对话内容超过模型上下文窗口的 **50%** 时触发

- **网关自动压缩**：当对话内容超过 **85%** 时触发（策略更激进，在对话轮次之间执行）

#### What Happens During Compression

1. Memory is flushed to disk first (preventing data loss)
2. Middle conversation turns are summarized into a compact summary
3. The last N messages are preserved intact (`compression.protect_last_n`, default: 20)
4. Tool call/result message pairs are kept together (never split)
5. A new session lineage ID is generated (compression creates a "child" session)



1. 先将记忆**写入磁盘**（防止数据丢失）

2. 把对话中间轮次**压缩为精简摘要**

3. 保留最后 N 条消息**完整不变**（`compression.protect_last_n`，默认：20）

4. 工具调用与结果消息**成对保留、不拆分**

5. 生成新的会话谱系 ID（压缩会创建一个 “子会话”）

#### Session Persistence

After each turn:

- Messages are saved to the session store (SQLite via `hermes_state.py`)
- Memory changes are flushed to `MEMORY.md` / `USER.md`
- The session can be resumed later via `/resume` or `hermes chat --resume`

每轮对话结束后：

- 消息会保存到会话存储（通过 `hermes_state.py` 存入 SQLite）
- 记忆变更会**持久化写入** `MEMORY.md` / `USER.md`
- 后续可通过 `/resume` 或 `hermes chat --resume` 恢复会话

### Key Source Files

| File                          | Purpose                                                      |
| ----------------------------- | ------------------------------------------------------------ |
| `run_agent.py`                | AIAgent class — the complete agent loop (~13,700 lines)      |
| `agent/prompt_builder.py`     | System prompt assembly from memory, skills, context files, personality |
| `agent/context_engine.py`     | ContextEngine ABC — pluggable context management             |
| `agent/context_compressor.py` | Default engine — lossy summarization algorithm               |
| `agent/prompt_caching.py`     | Anthropic prompt caching markers and cache metrics           |
| `agent/auxiliary_client.py`   | Auxiliary LLM client for side tasks (vision, summarization)  |
| `model_tools.py`              | Tool schema collection, `handle_function_call()` dispatch    |

## 