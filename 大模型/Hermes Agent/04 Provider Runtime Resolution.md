[toc]

原文：https://hermes-agent.nousresearch.com/docs/developer-guide/provider-runtime

## Provider Runtime Resolution

Hermes has a shared provider runtime resolver used across:

- CLI
- gateway
- cron jobs
- ACP
- auxiliary model calls

Primary implementation:

- `hermes_cli/runtime_provider.py` — credential resolution, `_resolve_custom_runtime()`
- `hermes_cli/auth.py` — provider registry, `resolve_provider()`
- `hermes_cli/model_switch.py` — shared `/model` switch pipeline (CLI + gateway)
- `agent/auxiliary_client.py` — auxiliary model routing
- `providers/` — ABC + registry entry points (`ProviderProfile`, `register_provider`, `get_provider_profile`, `list_providers`)
- `plugins/model-providers/<name>/` — per-provider plugins (bundled) that declare `api_mode`, `base_url`, `env_vars`, `fallback_models` and register themselves into the registry on first access. User plugins at `$HERMES_HOME/plugins/model-providers/<name>/` override bundled ones of the same name.

`get_provider_profile()` in `providers/` returns a `ProviderProfile` for a given provider id. `runtime_provider.py` calls this at resolution time to get the canonical `base_url`, `env_vars` priority list, `api_mode`, and `fallback_models` without needing to duplicate that data in multiple files. Adding a new plugin under `plugins/model-providers/<your-provider>/` (or `$HERMES_HOME/plugins/model-providers/<your-provider>/`) that calls `register_provider()` is enough for `runtime_provider.py` to pick it up — no branch needed in the resolver itself.

`providers/` 中的 `get_provider_profile()` 会根据指定的服务商 ID 返回一个 `ProviderProfile` 对象。`runtime_provider.py` 在解析时调用该方法，以获取标准的 `base_url`、`env_vars` 优先级列表、`api_mode` 和 `fallback_models`，**无需在多个文件中重复定义这些数据**。只需在 `plugins/model-providers/<your-provider>/`（或 `$HERMES_HOME/plugins/model-providers/<your-provider>/`）下添加一个调用了 `register_provider()` 的新插件，`runtime_provider.py` 就能自动识别并加载 —— **无需在解析器内部添加分支判断逻辑**。

### Resolution precedence

At a high level, provider resolution uses:

1. explicit CLI/runtime request
2. `config.yaml` model/provider config
3. environment variables
4. provider-specific defaults or auto resolution

That ordering matters because Hermes treats the saved model/provider choice as the source of truth for normal runs. This prevents a stale shell export from silently overriding the endpoint a user last selected in `hermes model`.

从高层逻辑来看，模型服务商解析按以下优先级生效：

1. 命令行 / 运行时**显式指定**
2. `config.yaml` 模型与服务商配置
3. 环境变量
4. 服务商专属默认值或自动解析

该优先级顺序至关重要，因为 Hermes 在常规运行中**以已保存的模型 / 服务商选择作为唯一可信来源**。

这能避免旧的终端环境变量配置，悄悄覆盖用户通过 `hermes model` 最近选定的接口地址。



>  PS: 这里的 provider 就是指openapi, claude code, deepseek 等这些 LLM API 的能力提供方。

### Output of runtime resolution

The runtime resolver returns data such as:

- `provider`
- `api_mode`
- `base_url`
- `api_key`
- `source`
- provider-specific metadata like expiry/refresh info

### Why this matters

This resolver is the main reason Hermes can share auth/runtime logic between:

- `hermes chat`
- gateway message handling
- cron jobs running in fresh sessions
- ACP editor sessions
- auxiliary model tasks

这套解析器是 Hermes 能够在以下场景**复用鉴权与运行时逻辑**的核心原因：

- `hermes chat` 命令行对话
- 网关消息处理
- 全新会话中运行的定时任务
- ACP 编辑器会话
- 辅助模型任务

### AI Gateway

Set `AI_GATEWAY_API_KEY` in `~/.hermes/.env` and run with `--provider ai-gateway`. Hermes fetches available models from the gateway's `/models` endpoint, filtering to language models with tool-use support.

### OpenRouter, AI Gateway, and custom OpenAI-compatible base URLs

Hermes contains logic to avoid leaking the wrong API key to a custom endpoint when multiple provider keys exist (e.g. `OPENROUTER_API_KEY`, `AI_GATEWAY_API_KEY`, and `OPENAI_API_KEY`).

Hermes 内置了防护逻辑：当系统存在多个服务商密钥（例如 `OPENROUTER_API_KEY`、`AI_GATEWAY_API_KEY`、`OPENAI_API_KEY`）时，可**避免向自定义接口错误泄露无关的 API 密钥**。

Each provider's API key is scoped to its own base URL:

- `OPENROUTER_API_KEY` is only sent to `openrouter.ai` endpoints
- `AI_GATEWAY_API_KEY` is only sent to `ai-gateway.vercel.sh` endpoints
- `OPENAI_API_KEY` is used for custom endpoints and as a fallback

每个服务商的 API 密钥都**限定专属基础地址生效**：

- `OPENROUTER_API_KEY` 仅发送至 `openrouter.ai` 接口地址
- `AI_GATEWAY_API_KEY` 仅发送至 `ai-gateway.vercel.sh` 接口地址
- `OPENAI_API_KEY` 用于自定义接口，并作为兜底备用密钥

Hermes also distinguishes between:

- a real custom endpoint selected by the user
- the OpenRouter fallback path used when no custom endpoint is configured

Hermes 还会严格区分两种场景：

- 用户手动选定的**真实自定义接口**
- 未配置自定义接口时，自动走的 **OpenRouter 兜底链路**

That distinction is especially important for:

- local model servers
- non-OpenRouter/non-AI Gateway OpenAI-compatible APIs
- switching providers without re-running setup
- config-saved custom endpoints that should keep working even when `OPENAI_BASE_URL` is not exported in the current shell

这种区分机制在以下场景中尤为重要：

- 本地模型服务
- 非 OpenRouter、非 AI Gateway，但兼容 OpenAI 协议的第三方接口
- 切换模型服务商时无需重新初始化配置
- 已保存在配置文件中的自定义接口，**即便当前终端未导出 `OPENAI_BASE_URL` 环境变量，也能正常使用**

### Native Anthropic path

Anthropic is not just "via OpenRouter" anymore.

Anthropic 不再只能**经由 OpenRouter 中转**使用。

When provider resolution selects `anthropic`, Hermes uses:

- `api_mode = anthropic_messages`
- the native Anthropic Messages API
- `agent/anthropic_adapter.py` for translation

当服务商解析选中 `anthropic` 时，Hermes 会启用：

- `api_mode = anthropic_messages`
- 原生 Anthropic Messages 接口
- 由 `agent/anthropic_adapter.py` 做协议适配转换

Credential resolution for native Anthropic now prefers refreshable Claude Code credentials over copied env tokens when both are present. In practice that means:

- Claude Code credential files are treated as the preferred source when they include refreshable auth
- manual `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` values still work as explicit overrides
- Hermes preflights Anthropic credential refresh before native Messages API calls
- Hermes still retries once on a 401 after rebuilding the Anthropic client, as a fallback path

原生 Anthropic 的凭证解析逻辑做了优先级调整：

当**同时存在可刷新的 Claude Code 凭证**和手动配置的环境变量令牌时，**优先采用可自动刷新的 Claude Code 凭证**。

实际效果：

1. 若 Claude Code 凭证文件包含可刷新鉴权信息，会被作为**首选凭证来源**；
2. 手动填写的 `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` 仍可作为**显式强制覆盖**生效；
3. 调用原生 Messages 接口前，Hermes 会**预先检查并刷新 Anthropic 凭证**；
4. 遇到 401 鉴权失败时，Hermes 会重建 Anthropic 客户端并**自动重试一次**作为兜底方案。

### OpenAI Codex path

Codex uses a separate Responses API path:

- `api_mode = codex_responses`
- dedicated credential resolution and auth store support

### Auxiliary model routing

Auxiliary tasks such as:

- vision
- web extraction summarization
- context compression summaries
- session search summarization
- skills hub operations
- MCP helper operations
- memory flushes

can use their own provider/model routing rather than the main conversational model.

以下这类**辅助任务**：

- 视觉识图
- 网页提取与摘要
- 上下文压缩摘要
- 会话检索摘要
- 技能仓库操作
- MCP 助手操作
- 记忆落盘持久化

均可**独立配置服务商 / 模型路由**，不必和主对话模型共用一套。

When an auxiliary task is configured with provider `main`, Hermes resolves that through the same shared runtime path as normal chat. In practice that means:

- env-driven custom endpoints still work
- custom endpoints saved via `hermes model` / `config.yaml` also work
- auxiliary routing can tell the difference between a real saved custom endpoint and the OpenRouter fallback

若把辅助任务的服务商配置设为 `main`（沿用主配置），Hermes 会走和普通对话**完全相同的共享运行时解析链路**。

实际效果体现为：

- 环境变量配置的自定义接口依然生效
- 通过 `hermes model` 命令或 `config.yaml` 保存的自定义接口同样生效
- 辅助路由能精准区分：**用户真实保存的自定义接口** 和 **OpenRouter 兜底默认接口**

### Fallback models

Hermes supports a configured fallback model/provider pair, allowing runtime failover when the primary model encounters errors.

#### How it works internally

1. **Storage**: `AIAgent.__init__` stores the `fallback_model` dict and sets `_fallback_activated = False`.
2. **Trigger points**: `_try_activate_fallback()` is called from three places in the main retry loop in `run_agent.py`:
   - After max retries on invalid API responses (None choices, missing content)
   - On non-retryable client errors (HTTP 401, 403, 404)
   - After max retries on transient errors (HTTP 429, 500, 502, 503)
3. **Activation flow** (`_try_activate_fallback`):
   - Returns `False` immediately if already activated or not configured
   - Calls `resolve_provider_client()` from `auxiliary_client.py` to build a new client with proper auth
   - Determines `api_mode`: `codex_responses` for openai-codex, `anthropic_messages` for anthropic, `chat_completions` for everything else
   - Swaps in-place: `self.model`, `self.provider`, `self.base_url`, `self.api_mode`, `self.client`, `self._client_kwargs`
   - For anthropic fallback: builds a native Anthropic client instead of OpenAI-compatible
   - Re-evaluates prompt caching (enabled for Claude models on OpenRouter)
   - Sets `_fallback_activated = True` — prevents firing again
   - Resets retry count to 0 and continues the loop
4. **Config flow**:
   - CLI: `cli.py` reads `CLI_CONFIG["fallback_model"]` → passes to `AIAgent(fallback_model=...)`
   - Gateway: `gateway/run.py._load_fallback_model()` reads `config.yaml` → passes to `AIAgent`
   - Validation: both `provider` and `model` keys must be non-empty, or fallback is disabled

**存储**：`AIAgent.__init__` 会存储 `fallback_model` 字典，并设置 `_fallback_activated = False`（未启用降级）。

**触发点**：`_try_activate_fallback()` 在 `run_agent.py` 主重试循环中的**三处**被调用：

- API 响应无效达到最大重试次数后（无选项、缺失内容）
- 遇到不可重试的客户端错误时（HTTP 401、403、404）
- 瞬时错误达到最大重试次数后（HTTP 429、500、502、503）

**启用降级流程**（`_try_activate_fallback`）：

- 如果已启用降级或未配置降级，立即返回 `False`
- 调用 `auxiliary_client.py` 中的 `resolve_provider_client()`，用正确鉴权创建新客户端
- 确定 `api_mode`：`openai-codex` 用 `codex_responses`、`anthropic` 用 `anthropic_messages`、其他均用 `chat_completions`
- **原地替换**：`self.model`、`self.provider`、`self.base_url`、`self.api_mode`、`self.client`、`self._client_kwargs`
- 如果是 Anthropic 降级：创建**原生 Anthropic 客户端**，而非兼容 OpenAI 的客户端
- 重新评估提示词缓存（OpenRouter 上的 Claude 模型会启用）
- 设置 `_fallback_activated = True` —— 防止重复触发
- 重置重试次数为 0，并继续循环

**配置流程**：

- CLI：`cli.py` 读取 `CLI_CONFIG["fallback_model"]` → 传递给 `AIAgent(fallback_model=...)`
- 网关：`gateway/run.py._load_fallback_model()` 读取 `config.yaml` → 传递给 `AIAgent`
- 校验：`provider` 和 `model` 键必须都非空，否则降级功能禁用

#### What does NOT support fallback

- **Subagent delegation** (`tools/delegate_tool.py`): subagents inherit the parent's provider but not the fallback config
- **Auxiliary tasks**: use their own independent provider auto-detection chain (see Auxiliary model routing above)

Cron jobs **do** support fallback: `run_job()` reads `fallback_providers` (or legacy `fallback_model`) from `config.yaml` and passes it to `AIAgent(fallback_model=...)`, matching the gateway's `_load_fallback_model()` pattern. See [Cron Internals](https://hermes-agent.nousresearch.com/docs/developer-guide/cron-internals).

- **子代理委派**（`tools/delegate_tool.py`）：子代理会继承父代理的模型服务商配置，但**不继承降级备用模型配置**。
- **辅助任务**：拥有**独立的服务商自动解析链路**（参见上文「辅助模型路由」部分）。

定时任务**支持模型降级兜底**：`run_job()` 会从 `config.yaml` 读取 `fallback_providers`（或旧版配置字段 `fallback_model`），并传入 `AIAgent(fallback_model=...)`，实现逻辑与网关的 `_load_fallback_model()` 保持一致。详见文档：[定时任务内部原理](https://hermes-agent.nousresearch.com/docs/developer-guide/cron-internals)。

