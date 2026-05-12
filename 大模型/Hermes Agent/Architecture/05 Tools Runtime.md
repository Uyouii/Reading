[toc]

原文地址：https://hermes-agent.nousresearch.com/docs/developer-guide/tools-runtime

## Tools Runtime

Hermes tools are self-registering functions grouped into toolsets and executed through a central registry/dispatch system.

Primary files:

- `tools/registry.py`
- `model_tools.py`
- `toolsets.py`
- `tools/terminal_tool.py`
- `tools/environments/*`

### Tool registration model

Each tool module calls `registry.register(...)` at import time.

`model_tools.py` is responsible for importing/discovering tool modules and building the schema list used by the model.

#### How `registry.register()` works

Every tool file in `tools/` calls `registry.register()` at module level to declare itself. The function signature is:

```python
registry.register(
    name="terminal",               # Unique tool name (used in API schemas)
    toolset="terminal",            # Toolset this tool belongs to
    schema={...},                  # OpenAI function-calling schema (description, parameters)
    handler=handle_terminal,       # The function that executes when the tool is called
    check_fn=check_terminal,       # Optional: returns True/False for availability
    requires_env=["SOME_VAR"],     # Optional: env vars needed (for UI display)
    is_async=False,                # Whether the handler is an async coroutine
    description="Run commands",    # Human-readable description
    emoji="💻",                    # Emoji for spinner/progress display
)
```

Each call creates a `ToolEntry` stored in the singleton `ToolRegistry._tools` dict keyed by tool name. If a name collision occurs across toolsets, a warning is logged and the later registration wins.

#### Discovery: `discover_builtin_tools()`

When `model_tools.py` is imported, it calls `discover_builtin_tools()` from `tools/registry.py`. This function scans every `tools/*.py` file using AST parsing to find modules that contain top-level `registry.register()` calls, then imports them:

```python
# tools/registry.py (simplified)
def discover_builtin_tools(tools_dir=None):
    tools_path = Path(tools_dir) if tools_dir else Path(__file__).parent
    for path in sorted(tools_path.glob("*.py")):
        if path.name in {"__init__.py", "registry.py", "mcp_tool.py"}:
            continue
        if _module_registers_tools(path):  # AST check for top-level registry.register()
            importlib.import_module(f"tools.{path.stem}")
```

This auto-discovery means new tool files are picked up automatically — no manual list to maintain. The AST check only matches top-level `registry.register()` calls (not calls inside functions), so helper modules in `tools/` are not imported.

这种**自动发现机制**意味着新的工具文件可以被自动识别加载，无需手动维护工具清单。

AST 语法解析仅匹配**顶层**的 `registry.register()` 注册调用（不识别函数内部的注册调用），因此不会导入 `tools/` 目录下的辅助工具模块。

Each import triggers the module's `registry.register()` calls. Errors in optional tools (e.g., missing `fal_client` for image generation) are caught and logged — they don't prevent other tools from loading.

每一次模块导入都会触发该模块内的 `registry.register()` 注册逻辑。

可选工具若出现依赖错误（例如图像生成缺少 `fal_client` 依赖库），会被捕获并日志记录，**不会阻碍其他工具正常加载**。

After core tool discovery, MCP tools and plugin tools are also discovered:

1. **MCP tools** — `tools.mcp_tool.discover_mcp_tools()` reads MCP server config and registers tools from external servers.
2. **Plugin tools** — `hermes_cli.plugins.discover_plugins()` loads user/project/pip plugins that may register additional tools.

完成核心工具的自动发现后，还会继续发现并加载 **MCP 工具**与**插件工具**：

- **MCP 工具**：由 `tools.mcp_tool.discover_mcp_tools()` 读取 MCP 服务端配置，注册来自外部服务的工具。
- **插件工具**：由 `hermes_cli.plugins.discover_plugins()` 加载用户级、项目级以及 Pip 安装的插件，这类插件可注册额外的自定义工具。

### Tool availability checking (`check_fn`)

Each tool can optionally provide a `check_fn` — a callable that returns `True` when the tool is available and `False` otherwise. Typical checks include:

- **API key present** — e.g., `lambda: bool(os.environ.get("SERP_API_KEY"))` for web search
- **Service running** — e.g., checking if the Honcho server is configured
- **Binary installed** — e.g., verifying `playwright` is available for browser tools

When `registry.get_definitions()` builds the schema list for the model, it runs each tool's `check_fn()`:

```python
# Simplified from registry.py
if entry.check_fn:
    try:
        available = bool(entry.check_fn())
    except Exception:
        available = False   # Exceptions = unavailable
    if not available:
        continue            # Skip this tool entirely
```

Key behaviors:

- Check results are **cached per-call** — if multiple tools share the same `check_fn`, it only runs once.
- Exceptions in `check_fn()` are treated as "unavailable" (fail-safe).
- The `is_toolset_available()` method checks whether a toolset's `check_fn` passes, used for UI display and toolset resolution.

核心特性：

- 检查结果**按单次调用缓存**：如果多个工具共用同一个 `check_fn`，该函数只会执行一次。
- `check_fn()` 执行时若抛出异常，会被视作**工具不可用**（故障安全机制）。
- 方法 `is_toolset_available()` 用于校验某个工具集的 `check_fn` 是否校验通过，专供界面展示与工具集解析使用。

### Toolset resolution

Toolsets are named bundles of tools. Hermes resolves them through:

- explicit enabled/disabled toolset lists
- platform presets (`hermes-cli`, `hermes-telegram`, etc.)
- dynamic MCP toolsets
- curated special-purpose sets like `hermes-acp`

Toolsets are named bundles of tools。Hermes 通过以下途径解析加载工具集：

- 手动指定的启用 / 禁用工具集列表
- 平台预设方案（如 `hermes-cli`、`hermes-telegram` 等）
- 动态 MCP 工具集
- 精心定制的专用工具集，例如 `hermes-acp`

#### How `get_tool_definitions()` filters tools

The main entry point is `model_tools.get_tool_definitions(enabled_toolsets, disabled_toolsets, quiet_mode)`:

1. **If `enabled_toolsets` is provided** — only tools from those toolsets are included. Each toolset name is resolved via `resolve_toolset()` which expands composite toolsets into individual tool names.
2. **If `disabled_toolsets` is provided** — start with ALL toolsets, then subtract the disabled ones.
3. **If neither** — include all known toolsets.
4. **Registry filtering** — the resolved tool name set is passed to `registry.get_definitions()`, which applies `check_fn` filtering and returns OpenAI-format schemas.
5. **Dynamic schema patching** — after filtering, `execute_code` and `browser_navigate` schemas are dynamically adjusted to only reference tools that actually passed filtering (prevents model hallucination of unavailable tools).

### Dispatch

At runtime, tools are dispatched through the central registry, with agent-loop exceptions for some agent-level tools such as memory/todo/session-search handling.

#### Dispatch flow: model tool_call → handler execution

When the model returns a `tool_call`, the flow is:

```sh
Model response with tool_call
    ↓
run_agent.py agent loop
    ↓
model_tools.handle_function_call(name, args, task_id, user_task)
    ↓
[Agent-loop tools?] → handled directly by agent loop (todo, memory, session_search, delegate_task)
    ↓
[Plugin pre-hook] → invoke_hook("pre_tool_call", ...)
    ↓
registry.dispatch(name, args, **kwargs)
    ↓
Look up ToolEntry by name
    ↓
[Async handler?] → bridge via _run_async()
[Sync handler?]  → call directly
    ↓
Return result string (or JSON error)
    ↓
[Plugin post-hook] → invoke_hook("post_tool_call", ...)
```

#### Error wrapping

All tool execution is wrapped in error handling at two levels:

1. **`registry.dispatch()`** — catches any exception from the handler and returns `{"error": "Tool execution failed: ExceptionType: message"}` as JSON.
2. **`handle_function_call()`** — wraps the entire dispatch in a secondary try/except that returns `{"error": "Error executing tool_name: message"}`.

This ensures the model always receives a well-formed JSON string, never an unhandled exception.

#### Agent-loop tools

Four tools are intercepted(拦截) before registry dispatch because they need agent-level state (TodoStore, MemoryStore, etc.):

- `todo` — planning/task tracking
- `memory` — persistent memory writes
- `session_search` — cross-session recall
- `delegate_task` — spawns subagent sessions

These tools' schemas are still registered in the registry (for `get_tool_definitions`), but their handlers return a stub error if dispatch somehow reaches them directly.

有**四个工具**会在注册中心分发执行前被拦截，原因是它们需要依赖智能体层级的状态（如待办事项存储、持久化记忆存储等）：

- `todo` — 任务规划与跟踪
- `memory` — 持久化记忆写入
- `session_search` — 跨会话信息检索
- `delegate_task` — 创建子智能体会话

这些工具的模式定义仍会注册在注册中心中（供 `get_tool_definitions` 函数使用），但如果分发流程意外直接调用到它们的处理函数，函数会返回一个占位错误。

#### Async bridging

When a tool handler is async, `_run_async()` bridges it to the sync dispatch path:

- **CLI path (no running loop)** — uses a persistent event loop to keep cached async clients alive
- **Gateway path (running loop)** — spins up a disposable thread with `asyncio.run()`
- **Worker threads (parallel tools)** — uses per-thread persistent loops stored in thread-local storage

当工具处理函数为异步（async）时，`_run_async()` 会将其桥接到同步分发流程：

- **CLI 路径（无运行中的事件循环）** — 使用持久化事件循环，让缓存的异步客户端保持活跃
- **网关路径（存在运行中的事件循环）** — 通过 `asyncio.run()` 启动临时线程执行
- **工作线程（并行工具）** — 使用存储在线程本地存储中的、每个线程独立的持久化循环

### The DANGEROUS_PATTERNS approval flow

The terminal tool integrates a dangerous-command approval system defined in `tools/approval.py`:

1. **Pattern detection** — `DANGEROUS_PATTERNS` is a list of `(regex, description)` tuples covering destructive operations:
   - Recursive deletes (`rm -rf`)
   - Filesystem formatting (`mkfs`, `dd`)
   - SQL destructive operations (`DROP TABLE`, `DELETE FROM` without `WHERE`)
   - System config overwrites (`> /etc/`)
   - Service manipulation (`systemctl stop`)
   - Remote code execution (`curl | sh`)
   - Fork bombs, process kills, etc.
2. **Detection** — before executing any terminal command, `detect_dangerous_command(command)` checks against all patterns.
3. **Approval prompt** — if a match is found:
   - **CLI mode** — an interactive prompt asks the user to approve, deny, or allow permanently
   - **Gateway mode** — an async approval callback sends the request to the messaging platform
   - **Smart approval** — optionally, an auxiliary LLM can auto-approve low-risk commands that match patterns (e.g., `rm -rf node_modules/` is safe but matches "recursive delete")
4. **Session state** — approvals are tracked per-session. Once you approve "recursive delete" for a session, subsequent `rm -rf` commands don't re-prompt.
5. **Permanent allowlist** — the "allow permanently" option writes the pattern to `config.yaml`'s `command_allowlist`, persisting across sessions.

终端工具集成了一套定义在 `tools/approval.py` 中的**危险指令审批系统**：

1. **模式检测** — `DANGEROUS_PATTERNS` 是由 `(正则表达式, 描述)` 元组组成的列表，覆盖各类破坏性操作：
   - 递归删除（`rm -rf`）
   - 文件系统格式化（`mkfs`、`dd`）
   - SQL 破坏性操作（`DROP TABLE`、无 `WHERE` 条件的 `DELETE FROM`）
   - 系统配置覆盖写入（`> /etc/`）
   - 服务操作（`systemctl stop`）
   - 远程代码执行（`curl | sh`）
   - 进程炸弹、进程强制终止等
2. **检测机制** — 在执行任何终端指令前，`detect_dangerous_command(command)` 会将指令与所有危险模式进行匹配校验。
3. **审批提示** — 若匹配到危险指令：
   - **CLI 模式** — 弹出交互式提示，请求用户**批准、拒绝**或**永久允许**该指令
   - **网关模式** — 通过异步审批回调将请求发送至消息平台
   - **智能审批** — 可选用辅助大语言模型自动批准低风险指令（例如 `rm -rf node_modules/` 虽匹配 “递归删除” 模式，但属于安全操作）
4. **会话状态** — 审批记录按会话跟踪。若在某个会话中批准了 “递归删除”，后续执行的 `rm -rf` 指令将不再重复提示。
5. **永久白名单** — 选择 “永久允许” 后，会将对应模式写入 `config.yaml` 的 `command_allowlist` 配置项，跨会话永久生效。



