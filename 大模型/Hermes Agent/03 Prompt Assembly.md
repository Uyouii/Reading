[toc]

原文：https://hermes-agent.nousresearch.com/docs/developer-guide/prompt-assembly

## Prompt Assembly

Hermes deliberately separates:

- **cached system prompt state**
- **ephemeral API-call-time additions**

Hermes 刻意做了**分离设计**：

- **缓存的系统提示词状态**
- **临时的、API 调用时追加的内容**

This is one of the most important design choices in the project because it affects:

- token usage
- prompt caching effectiveness
- session continuity
- memory correctness

这是项目中**最重要的设计决策之一**，因为它会直接影响：

- Token 消耗量
- 提示词缓存的有效性
- 会话连续性
- 记忆准确性

### Cached system prompt layers

The cached system prompt is assembled in roughly this order:

1. agent identity — `SOUL.md` from `HERMES_HOME` when available, otherwise falls back to `DEFAULT_AGENT_IDENTITY` in `prompt_builder.py`
2. tool-aware behavior guidance
3. Honcho static block (when active)
4. optional system message
5. frozen MEMORY snapshot
6. frozen USER profile snapshot
7. skills index
8. context files (`AGENTS.md`, `.cursorrules`, `.cursor/rules/*.mdc`) — SOUL.md is **not** included here when it was already loaded as the identity in step 1
9. timestamp / optional session ID
10. platform hint

When `skip_context_files` is set (e.g., subagent delegation), SOUL.md is not loaded and the hardcoded `DEFAULT_AGENT_IDENTITY` is used instead.

缓存版系统提示词大致按以下顺序组装：

1. **agent身份**：优先加载 `HERMES_HOME` 下的 `SOUL.md`，若无则回退到 `prompt_builder.py` 中的 `DEFAULT_AGENT_IDENTITY`
2. **工具感知行为指引**
3. **Honcho 静态模块**（启用时）
4. **可选系统消息**
5. **冻结的记忆快照（MEMORY）**
6. **冻结的用户配置快照（USER）**
7. **技能索引**
8. **上下文文件**（`AGENTS.md`、`.cursorrules`、`.cursor/rules/*.mdc`）—— 若第 1 步已加载 `SOUL.md` 作为身份，则此处**不再**重复包含
9. **时间戳 / 可选会话 ID**
10. **平台提示**

当设置 `skip_context_files` 时（如子代理委派场景），**不加载 `SOUL.md`**，直接使用硬编码的 `DEFAULT_AGENT_IDENTITY`。

#### Concrete example: assembled system prompt

Here is a simplified view of what the final system prompt looks like when all layers are present (comments show the source of each section):

```markdown
# Layer 1: Agent Identity (from ~/.hermes/SOUL.md)
You are Hermes, an AI assistant created by Nous Research.
You are an expert software engineer and researcher.
You value correctness, clarity, and efficiency.
...

# Layer 2: Tool-aware behavior guidance
You have persistent memory across sessions. Save durable facts using
the memory tool: user preferences, environment details, tool quirks,
and stable conventions. Memory is injected into every turn, so keep
it compact and focused on facts that will still matter later.
...
When the user references something from a past conversation or you
suspect relevant cross-session context exists, use session_search
to recall it before asking them to repeat themselves.

# Tool-use enforcement (for GPT/Codex models only)
You MUST use your tools to take action — do not describe what you
would do or plan to do without actually doing it.
...

# Layer 3: Honcho static block (when active)
[Honcho personality/context data]

# Layer 4: Optional system message (from config or API)
[User-configured system message override]

# Layer 5: Frozen MEMORY snapshot
## Persistent Memory
- User prefers Python 3.12, uses pyproject.toml
- Default editor is nvim
- Working on project "atlas" in ~/code/atlas
- Timezone: US/Pacific

# Layer 6: Frozen USER profile snapshot
## User Profile
- Name: Alice
- GitHub: alice-dev

# Layer 7: Skills index
## Skills (mandatory)
Before replying, scan the skills below. If one clearly matches
your task, load it with skill_view(name) and follow its instructions.
...
<available_skills>
  software-development:
    - code-review: Structured code review workflow
    - test-driven-development: TDD methodology
  research:
    - arxiv: Search and summarize arXiv papers
</available_skills>

# Layer 8: Context files (from project directory)
# Project Context
The following project context files have been loaded and should be followed:

## AGENTS.md
This is the atlas project. Use pytest for testing. The main
entry point is src/atlas/main.py. Always run `make lint` before
committing.

# Layer 9: Timestamp + session
Current time: 2026-03-30T14:30:00-07:00
Session: abc123

# Layer 10: Platform hint
You are a CLI AI Agent. Try not to use markdown but simple text
renderable inside a terminal.
```

### How SOUL.md appears in the prompt

`SOUL.md` lives at `~/.hermes/SOUL.md` and serves as the agent's identity — the very first section of the system prompt. The loading logic in `prompt_builder.py` works as follows:

```python
# From agent/prompt_builder.py (simplified)
def load_soul_md() -> Optional[str]:
    soul_path = get_hermes_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")  # Security scan
    content = _truncate_content(content, "SOUL.md")       # Cap at 20k chars
    return content
```

When `load_soul_md()` returns content, it replaces the hardcoded `DEFAULT_AGENT_IDENTITY`. The `build_context_files_prompt()` function is then called with `skip_soul=True` to prevent SOUL.md from appearing twice (once as identity, once as a context file).

If `SOUL.md` doesn't exist, the system falls back to:

```sh
You are Hermes Agent, an intelligent AI assistant created by Nous Research.
You are helpful, knowledgeable, and direct. You assist users with a wide
range of tasks including answering questions, writing and editing code,
analyzing information, creative work, and executing actions via your tools.
You communicate clearly, admit uncertainty when appropriate, and prioritize
being genuinely useful over being verbose unless otherwise directed below.
Be targeted and efficient in your exploration and investigations.
```

### How context files are injected

`build_context_files_prompt()` uses a **priority system** — only one project context type is loaded (first match wins):

```python
# From agent/prompt_builder.py (simplified)
def build_context_files_prompt(cwd=None, skip_soul=False):
    cwd_path = Path(cwd).resolve()

    # Priority: first match wins — only ONE project context loaded
    project_context = (
        _load_hermes_md(cwd_path)       # 1. .hermes.md / HERMES.md (walks to git root)
        or _load_agents_md(cwd_path)    # 2. AGENTS.md (cwd only)
        or _load_claude_md(cwd_path)    # 3. CLAUDE.md (cwd only)
        or _load_cursorrules(cwd_path)  # 4. .cursorrules / .cursor/rules/*.mdc
    )

    sections = []
    if project_context:
        sections.append(project_context)

    # SOUL.md from HERMES_HOME (independent of project context)
    if not skip_soul:
        soul_content = load_soul_md()
        if soul_content:
            sections.append(soul_content)

    if not sections:
        return ""

    return (
        "# Project Context\n\n"
        "The following project context files have been loaded "
        "and should be followed:\n\n"
        + "\n".join(sections)
    )
```

#### Context file discovery details

| Priority | Files                                 | Search scope       | Notes                         |
| -------- | ------------------------------------- | ------------------ | ----------------------------- |
| 1        | `.hermes.md`, `HERMES.md`             | CWD up to git root | Hermes-native project config  |
| 2        | `AGENTS.md`                           | CWD only           | Common agent instruction file |
| 3        | `CLAUDE.md`                           | CWD only           | Claude Code compatibility     |
| 4        | `.cursorrules`, `.cursor/rules/*.mdc` | CWD only           | Cursor compatibility          |

All context files are:

- **Security scanned** — checked for prompt injection patterns (invisible unicode, "ignore previous instructions", credential exfiltration attempts)
- **Truncated** — capped at 20,000 characters using 70/20 head/tail ratio with a truncation marker
- **YAML frontmatter stripped** — `.hermes.md` frontmatter is removed (reserved for future config overrides)

所有上下文文件都会经过以下处理：

- **安全扫描**：检查是否存在提示注入特征（不可见 Unicode 字符、“忽略之前指令”、凭证窃取尝试等）
- **截断处理**：按 **70/20 头尾比例** 限制最长 **20,000 字符**，并添加截断标记
- **移除 YAML 前置元信息**：剥离 `.hermes.md` 的前置配置区（预留用于后续配置覆盖）

### API-call-time-only layers

These are intentionally *not* persisted as part of the cached system prompt:

- `ephemeral_system_prompt`
- prefill messages
- gateway-derived session context overlays
- later-turn Honcho recall injected into the current-turn user message

This separation keeps the stable prefix stable for caching.

以下内容**刻意不被持久化**到缓存的系统提示词中：

- 临时系统提示词（`ephemeral_system_prompt`）
- 预填充消息
- 网关派生的会话上下文叠加层
- 在当前轮用户消息中注入的后期 Honcho 召回内容

这种分离设计能让**稳定前缀保持不变**，从而提升缓存效率。

### Memory snapshots

Local memory and user profile data are injected as frozen snapshots at session start. Mid-session writes update disk state but do not mutate the already-built system prompt until a new session or forced rebuild occurs.

本地记忆与用户资料数据会在会话开始时，以**冻结快照**形式注入。

会话中途的写入操作只会更新磁盘数据，**不会改动已构建好的系统提示词**，直到新建会话或强制重建才会刷新。

### Context files

`agent/prompt_builder.py` scans and sanitizes project context files using a **priority system** — only one type is loaded (first match wins):

1. `.hermes.md` / `HERMES.md` (walks to git root)
2. `AGENTS.md` (CWD at startup; subdirectories discovered progressively during the session via `agent/subdirectory_hints.py`)
3. `CLAUDE.md` (CWD only)
4. `.cursorrules` / `.cursor/rules/*.mdc` (CWD only)

`agent/prompt_builder.py` 使用一套**优先级系统**扫描并清理项目上下文文件 ——**仅加载优先级最高的一类（先匹配即加载，后续不再加载）**：

1. `.hermes.md` / `HERMES.md`（向上遍历至 Git 根目录查找）
2. `AGENTS.md`（启动时的当前工作目录；会话期间通过 `agent/subdirectory_hints.py` 逐步发现子目录中的文件）
3. `CLAUDE.md`（仅限当前工作目录）
4. `.cursorrules` / `.cursor/rules/*.mdc`（仅限当前工作目录）

`SOUL.md` is loaded separately via `load_soul_md()` for the identity slot. When it loads successfully, `build_context_files_prompt(skip_soul=True)` prevents it from appearing twice.

`SOUL.md` 通过 `load_soul_md()` 单独加载，用于填充智能体身份字段。若成功加载，`build_context_files_prompt(skip_soul=True)` 会避免其重复出现。

Long files are truncated before injection.

长文件在注入前会被截断处理。

### Skills index

The skills system contributes a compact skills index to the prompt when skills tooling is available.

### Supported prompt customization surfaces

Most users should treat `agent/prompt_builder.py` as implementation code, not a configuration surface. The supported customization path is to change the prompt inputs Hermes already loads, rather than editing Python templates in place.

大多数开发者应将 `agent/prompt_builder.py` 视为**底层实现代码**，而非配置入口。

Hermes 推荐的自定义方式是**修改框架已加载的提示词资源文件**，而不是直接改动 Python 模板源码。

#### Use these surfaces first

- `~/.hermes/SOUL.md` — replace the built-in default identity block with your own agent personal and standing behavior.
- `~/.hermes/MEMORY.md` and `~/.hermes/USER.md` — provide durable cross-session facts and user profile data that should be snapshotted into new sessions.
- Project context files such as `.hermes.md`, `HERMES.md`, `AGENTS.md`, `CLAUDE.md`, or `.cursorrules` — inject repo-specific working rules.
- Skills — package reusable workflows and references without editing core prompt code.
- Optional system prompt config / API overrides — add deployment-specific instruction text without forking Hermes.
- Ephemeral overlays such as `HERMES_EPHEMERAL_SYSTEM_PROMPT` or prefill messages — add turn-scoped guidance that should not become part of the cached prompt prefix.

- `~/.hermes/SOUL.md` — 用自定义的智能体人设与常驻行为规范，替换内置默认身份模块。

- `~/.hermes/MEMORY.md` 与 `~/.hermes/USER.md` — 提供跨会话持久化的事实信息和用户资料，新建会话时会以快照形式载入。

- 项目上下文文件（`.hermes.md`、`HERMES.md`、`AGENTS.md`、`CLAUDE.md`、`.cursorrules` 等）—— 注入代码仓库专属的工作规则。

- 技能（Skills）—— 封装可复用的工作流程与参考信息，**无需修改核心提示词代码**。

- 可选系统提示词配置 / API 覆盖配置 — 增加部署环境专属指令文本，无需 Fork Hermes 源码。

- 临时覆盖层（如 `HERMES_EPHEMERAL_SYSTEM_PROMPT`、预填充消息）—— 添加**仅单轮生效**的引导规则，不纳入缓存提示词前缀。

#### When to edit code instead

Edit `agent/prompt_builder.py` only if you are intentionally maintaining a fork or contributing upstream behavior changes. That file assembles the prompt plumbing, cache boundaries, and injection order for every session. Direct edits there are global product changes, not per-user prompt customization.

In other words:

- if you want a different assistant identity, edit `SOUL.md`
- if you want different repo rules, edit project context files
- if you want reusable operating procedures, add or modify skills
- if you want to change how Hermes assembles prompts for everyone, change Python and treat it as a code contribution

仅当你**主动维护源码分支**或**向官方贡献功能变更**时，才可编辑 `agent/prompt_builder.py`。

该文件负责为每一次会话组装提示词底层逻辑、缓存边界以及内容注入顺序。直接修改此文件属于**全局性产品级改动**，而非个人提示词自定义配置。

换而言之：

- 想要更换智能体人设，修改 `SOUL.md`
- 想要自定义仓库规则，编辑项目上下文文件
- 想要新增可复用工作流程，添加或修改技能模块
- 想要全局改动 Hermes 提示词组装逻辑，再去修改 Python 源码，并按代码贡献的方式对待

### Why prompt assembly is split this way

The architecture is intentionally optimized to:

- preserve provider-side prompt caching
- avoid mutating history unnecessarily
- keep memory semantics understandable
- let gateway/ACP/CLI add context without poisoning persistent prompt state

该架构经过精心设计，专门针对以下目标做了优化：

- 保留模型服务端的提示词缓存能力
- 避免对会话历史进行不必要的变更
- 保持记忆逻辑语义清晰、易于理解
- 允许网关 / ACP/CLI 层追加上下文，同时**不污染持久化的提示词状态**