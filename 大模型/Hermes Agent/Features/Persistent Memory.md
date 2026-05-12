[TOC]

原文：https://hermes-agent.nousresearch.com/docs/user-guide/features/memory

## Persistent Memory

Hermes Agent has bounded, curated memory that persists across sessions. This lets it remember your preferences, your projects, your environment, and things it has learned.

Hermes Agent 拥有**有边界、经精选**的跨会话持久记忆，能够记住你的个人偏好、项目信息、使用环境以及它自身习得的各类知识经验。

### How It Works

Two files make up the agent's memory:

| File          | Purpose                                                      | Char Limit                |
| ------------- | ------------------------------------------------------------ | ------------------------- |
| **MEMORY.md** | Agent's personal notes — environment facts, conventions, things learned<br />智能体个人笔记 —— 环境客观信息、项目规范约定、习得经验心得 | 2,200 chars (~800 tokens) |
| **USER.md**   | User profile — your preferences, communication style, expectations<br />用户画像 —— 个人使用偏好、沟通表达方式、交互预期要求 | 1,375 chars (~500 tokens) |

Both are stored in `~/.hermes/memories/` and are injected into the system prompt as a frozen snapshot at session start. The agent manages its own memory via the `memory` tool — it can add, replace, or remove entries.

> Character limits keep memory focused. When memory is full, the agent consolidates or replaces entries to make room for new information.

### How Memory Appears in the System Prompt

At the start of every session, memory entries are loaded from disk and rendered into the system prompt as a frozen block:

```sh
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

The format includes:

- A header showing which store (MEMORY or USER PROFILE)
- Usage percentage and character counts so the agent knows capacity
- Individual entries separated by `§` (section sign) delimiters
- Entries can be multiline

格式包含以下内容：

- 头部标识，标明所属存储区（**记忆区 / 用户画像区**）
- 使用率与字符统计，让智能体知晓容量占用情况
- 独立条目以**段落分隔符 §** 进行拆分
- 条目支持多行文本

**Frozen snapshot pattern:** The system prompt injection is captured once at session start and never changes mid-session. This is intentional — it preserves the LLM's prefix cache for performance. When the agent adds/removes memory entries during a session, the changes are persisted to disk immediately but won't appear in the system prompt until the next session starts. Tool responses always show the live state.

**冻结快照模式**：系统提示词仅在会话起始时一次性加载注入，**同一会话中途不再变更**。

这是刻意设计的机制 —— 保留大模型的**前缀缓存**，以此提升推理性能。

智能体在会话过程中新增 / 删除记忆条目时，改动会**立即持久化写入磁盘**，但要等到**下一次会话启动**，这些变更才会体现在系统提示词中；而工具返回的响应始终展示**最新实时状态**。

### Memory Tool Actions

The agent uses the `memory` tool with these actions:

- **add** — Add a new memory entry
- **replace** — Replace an existing entry with updated content (uses substring matching via `old_text`)
- **remove** — Remove an entry that's no longer relevant (uses substring matching via `old_text`)

智能体通过 **memory** 工具执行以下操作：

- **add（新增）**：添加一条新记忆条目
- **replace（替换）**：用更新后的内容替换已有条目（通过`old_text`做子串匹配）
- **remove（删除）**：移除已失效、不再相关的条目（通过`old_text`做子串匹配）

There is no `read` action — memory content is automatically injected into the system prompt at session start. The agent sees its memories as part of its conversation context.

该工具**没有读取（read）操作**—— 记忆内容会在会话开始时自动注入系统提示词。智能体可直接在对话上下文里看到自身的记忆内容。

#### Substring Matching

The `replace` and `remove` actions use short unique substring matching — you don't need the full entry text. The `old_text` parameter just needs to be a unique substring that identifies exactly one entry:

`replace`（替换）和 `remove`（删除）操作采用**简短唯一子串匹配**机制 —— 无需传入完整条目文本。`old_text` 参数只需是**能精准定位唯一条目**的一段唯一子串即可：

```python
# If memory contains "User prefers dark mode in all editors"
memory(action="replace", target="memory",
       old_text="dark mode",
       content="User prefers light mode in VS Code, dark mode in terminal")
```

If the substring matches multiple entries, an error is returned asking for a more specific match.

如果该子串匹配到**多个条目**，系统将返回错误，并要求提供**更具体的匹配内容**。

### Two Targets Explained

#### `memory` — Agent's Personal Notes

For information the agent needs to remember about the environment, workflows, and lessons learned:

- Environment facts (OS, tools, project structure)
- Project conventions and configuration
- Tool quirks and workarounds discovered
- Completed task diary entries
- Skills and techniques that worked

供智能体需要长期记忆的**环境信息、工作流程、经验总结**适用范围：

- 环境客观信息（操作系统、工具、项目目录结构）
- 项目规范约定与配置规则
- 工具特有问题及摸索出的临时规避方案
- 已完成任务的日志记录
- 切实有效的技能与实操方法

#### `user` — User Profile

For information about the user's identity, preferences, and communication style:

- Name, role, timezone
- Communication preferences (concise vs detailed, format preferences)
- Pet peeves and things to avoid
- Workflow habits
- Technical skill level

用于记录**用户身份、个人偏好、沟通风格**相关信息：

- 姓名、身份角色、时区
- 沟通偏好（简洁版 vs 详细版、输出格式偏好）
- 忌讳事项、需要规避的行为
- 工作习惯
- 技术水平层次

### What to Save vs Skip

#### Save These (Proactively)

The agent saves automatically — you don't need to ask. It saves when it learns:

- **User preferences:** "I prefer TypeScript over JavaScript" → save to `user`
- **Environment facts:** "This server runs Debian 12 with PostgreSQL 16" → save to `memory`
- **Corrections:** "Don't use `sudo` for Docker commands, user is in docker group" → save to `memory`
- **Conventions:** "Project uses tabs, 120-char line width, Google-style docstrings" → save to `memory`
- **Completed work:** "Migrated database from MySQL to PostgreSQL on 2026-01-15" → save to `memory`
- **Explicit requests:** "Remember that my API key rotation happens monthly" → save to `memory`

智能体**自动保存记忆**，无需你手动指令。只要学到新信息就会自动留存：

- 用户偏好：「相比 JavaScript，我更喜欢 TypeScript」→ 保存到用户画像

- 环境信息：「本服务器运行 Debian 12 + PostgreSQL 16」→ 保存到记忆区

- 纠错经验：「Docker 命令不要用 sudo，当前用户已加入 docker 用户组」→ 保存到记忆区

- 项目规范：「项目使用制表符缩进、行宽 120 字符、Google 风格文档注释」→ 保存到记忆区

- 已完成工作：「2026-01-15 完成数据库从 MySQL 迁移到 PostgreSQL」→ 保存到记忆区

- 主动要求记忆：「记住我的 API 密钥每月轮换一次」→ 保存到记忆区

#### Skip These

- **Trivial/obvious info:** "User asked about Python" — too vague to be useful
- **Easily re-discovered facts:** "Python 3.12 supports f-string nesting" — can web search this
- **Raw data dumps:** Large code blocks, log files, data tables — too big for memory
- **Session-specific ephemera:** Temporary file paths, one-off debugging context
- **Information already in context files:** SOUL.md and AGENTS.md content



- **琐碎 / 显而易见的信息**：如 “用户询问了 Python 相关问题”—— 描述过于笼统，没有实际用处

- **可随时重新查到的常识**：如 “Python 3.12 支持 f-string 嵌套”—— 这类内容可随时网页检索

- **原始数据堆砌**：大段代码块、日志文件、数据表 —— 体量过大，不适合放入记忆

- **仅当前会话的临时信息**：临时文件路径、一次性调试上下文

- **已存在上下文文件中的内容**：如 SOUL.md、AGENTS.md 里已有信息

### Capacity Management

Memory has strict character limits to keep system prompts bounded:

| Store  | Limit       | Typical entries |
| ------ | ----------- | --------------- |
| memory | 2,200 chars | 8-15 entries    |
| user   | 1,375 chars | 5-10 entries    |

#### What Happens When Memory is Full

When you try to add an entry that would exceed the limit, the tool returns an error:

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Replace or remove existing entries first.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

The agent should then:

1. Read the current entries (shown in the error response)
2. Identify entries that can be removed or consolidated
3. Use `replace` to merge related entries into shorter versions
4. Then `add` the new entry

**Best practice:** When memory is above 80% capacity (visible in the system prompt header), consolidate entries before adding new ones. For example, merge three separate "project uses X" entries into one comprehensive project description entry.

#### Practical Examples of Good Memory Entries

**Compact, information-dense entries work best:**

```sh
# Good: Packs multiple related facts
User runs macOS 14 Sonoma, uses Homebrew, has Docker Desktop and Podman. Shell: zsh with oh-my-zsh. Editor: VS Code with Vim keybindings.

# Good: Specific, actionable convention
Project ~/code/api uses Go 1.22, sqlc for DB queries, chi router. Run tests with 'make test'. CI via GitHub Actions.

# Good: Lesson learned with context
The staging server (10.0.1.50) needs SSH port 2222, not 22. Key is at ~/.ssh/staging_ed25519.

# Bad: Too vague
User has a project.

# Bad: Too verbose
On January 5th, 2026, the user asked me to look at their project which is
located at ~/code/api. I discovered it uses Go version 1.22 and...
```

### Duplicate Prevention

The memory system automatically rejects exact duplicate entries. If you try to add content that already exists, it returns success with a "no duplicate added" message.

### Security Scanning

Memory entries are scanned for injection and exfiltration patterns before being accepted, since they're injected into the system prompt. Content matching threat patterns (prompt injection, credential exfiltration, SSH backdoors) or containing invisible Unicode characters is blocked.

记忆条目在被采纳存入前，会先扫描**提示注入**与**信息窃取**特征，因为这些记忆最终会被注入到系统提示词中。

凡是匹配威胁特征（提示词注入、凭证信息窃取、SSH 后门）或包含**不可见 Unicode 字符**的内容，都会被拦截屏蔽。

### Session Search

Beyond MEMORY.md and USER.md, the agent can search its past conversations using the `session_search` tool:

- All CLI and messaging sessions are stored in SQLite (`~/.hermes/state.db`) with FTS5 full-text search
- Search queries return relevant past conversations with Gemini Flash summarization
- The agent can find things it discussed weeks ago, even if they're not in its active memory

除 **MEMORY.md** 和 **USER.md** 之外，智能体还可通过 `session_search` 工具检索历史对话记录：

- 所有命令行及聊天会话均持久化存储在 SQLite 数据库（路径：`~/.hermes/state.db`），内置 FTS5 全文检索能力
- 搜索查询会返回相关历史会话，并由 Gemini Flash 做内容摘要
- 即便不在常驻热记忆中，智能体也能找回数周前讨论过的内容

```sh
hermes sessions list    # Browse past sessions
```

#### session_search vs memory

| Feature        | Persistent Memory                 | Session Search                      |
| -------------- | --------------------------------- | ----------------------------------- |
| **Capacity**   | ~1,300 tokens total               | Unlimited (all sessions)            |
| **Speed**      | Instant (in system prompt)        | Requires search + LLM summarization |
| **Use case**   | Key facts always available        | Finding specific past conversations |
| **Management** | Manually curated by agent         | Automatic — all sessions stored     |
| **Token cost** | Fixed per session (~1,300 tokens) | On-demand (searched when needed)    |

**Memory** is for critical facts that should always be in context. **Session search** is for "did we discuss X last week?" queries where the agent needs to recall specifics from past conversations.

记忆用于存放**需要始终常驻上下文**的关键核心事实。

会话检索则适用于这类查询场景：「我们上周有没有聊过某件事？」，供智能体从历史对话中调取具体细节。

### Configuration

```yaml
# In ~/.hermes/config.yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
```

### External Memory Providers

For deeper, persistent memory that goes beyond MEMORY.md and USER.md, Hermes ships with 8 external memory provider plugins — including Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, and Supermemory.

若需要超越 **MEMORY.md** 与 **USER.md** 能力的**更深层、长效持久记忆**，Hermes 内置了 8 种外部记忆提供商插件，包括：Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover 以及 Supermemory。

External providers run **alongside** built-in memory (never replacing it) and add capabilities like knowledge graphs, semantic search, automatic fact extraction, and cross-session user modeling.

外部记忆组件与**内置记忆 并行运行**，并不会取而代之；同时额外增强了知识图谱、语义检索、自动事实抽取、跨会话用户画像建模等能力。

```sh
hermes memory setup      # pick a provider and configure it
hermes memory status     # check what's active
```

