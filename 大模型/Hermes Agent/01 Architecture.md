[toc]

原文:https://hermes-agent.nousresearch.com/docs/developer-guide/architecture

## Architecture

### System Overview

```sh
┌─────────────────────────────────────────────────────────────────────┐
│                        Entry Points                                  │
│                                                                      │
│  CLI (cli.py)    Gateway (gateway/run.py)    ACP (acp_adapter/)     │
│  Batch Runner    API Server                  Python Library          │
└──────────┬──────────────┬───────────────────────┬───────────────────┘
           │              │                       │
           ▼              ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AIAgent (run_agent.py)                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Prompt       │  │ Provider     │  │ Tool         │               │
│  │ Builder      │  │ Resolution   │  │ Dispatch     │               │
│  │ (prompt_     │  │ (runtime_    │  │ (model_      │               │
│  │  builder.py) │  │  provider.py)│  │  tools.py)   │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                       │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐               │
│  │ Compression  │  │ 3 API Modes  │  │ Tool Registry│               │
│  │ & Caching    │  │ chat_compl.  │  │ (registry.py)│               │
│  │              │  │ codex_resp.  │  │ 61 tools     │               │
│  │              │  │ anthropic    │  │ 52 toolsets  │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────┴─────────────────┴─────────────────┴───────────────────────┘
           │                                    │
           ▼                                    ▼
┌───────────────────┐              ┌──────────────────────┐
│ Session Storage   │              │ Tool Backends         │
│ (SQLite + FTS5)   │              │ Terminal (7 backends) │
│ hermes_state.py   │              │ Browser (5 backends)  │
│ gateway/session.py│              │ Web (4 backends)      │
└───────────────────┘              │ MCP (dynamic)         │
                                   │ File, Vision, etc.    │
                                   └──────────────────────┘
```

### Data Flow

#### CLI Session

```sh
User input → HermesCLI.process_input()
  → AIAgent.run_conversation()
    → prompt_builder.build_system_prompt()
    → runtime_provider.resolve_runtime_provider()
    → API call (chat_completions / codex_responses / anthropic_messages)
    → tool_calls? → model_tools.handle_function_call() → loop
    → final response → display → save to SessionDB
```

### Gateway Message

```sh
Platform event → Adapter.on_message() → MessageEvent
  → GatewayRunner._handle_message()
    → authorize user
    → resolve session key
    → create AIAgent with session history
    → AIAgent.run_conversation()
    → deliver response back through adapter
```

### Cron Job

```sh
Scheduler tick → load due jobs from jobs.json
  → create fresh AIAgent (no history)
  → inject attached skills as context
  → run job prompt
  → deliver response to target platform
  → update job state and next_run
```

### Design Principles

| Principle                  | What it means in practice                                    |
| -------------------------- | ------------------------------------------------------------ |
| **Prompt stability**       | System prompt doesn't change mid-conversation. No cache-breaking mutations except explicit user actions (`/model`).<br />System prompt在对话过程中不会改变。除非用户执行显式操作（`/model`），否则不会发生破坏缓存的变更。 |
| **Observable execution**   | Every tool call is visible to the user via callbacks. Progress updates in CLI (spinner) and gateway (chat messages).<br />所有工具调用都会通过回调对用户可见。进度更新会显示在 CLI（spinner）和gateway（chat messages）中。 |
| **Interruptible**          | API calls and tool execution can be cancelled mid-flight by user input or signals.<br />API 调用与工具执行可在运行中通过用户输入或信号取消。 |
| **Platform-agnostic core** | One AIAgent class serves CLI, gateway, ACP, batch, and API server. Platform differences live in the entry point, not the agent.<br />同一个 **AIAgent 类**同时服务 CLI、网关、ACP、批处理与 API 服务器。平台差异只存在于入口点，而非agent。 |
| **Loose coupling**         | Optional subsystems (MCP, plugins, memory providers, RL environments) use registry patterns and check_fn gating, not hard dependencies.<br />可选子系统（MCP、插件、记忆提供器、强化学习环境）采用**注册模式**与 `check_fn` 门控，而非硬编码依赖。 |
| **Profile isolation**      | Each profile (`hermes -p <name>`) gets its own HERMES_HOME, config, memory, sessions, and gateway PID. Multiple profiles run concurrently.<br />每个profile（`hermes -p <名称>`）都拥有独立的 HERMES_HOME、配置、记忆、会话与网关进程号。多个profiles可**并发运行**。 |

## 