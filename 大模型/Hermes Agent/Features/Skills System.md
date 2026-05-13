[TOC]

原文链接：https://hermes-agent.nousresearch.com/docs/user-guide/features/skills

## Skills System

Skills are on-demand knowledge documents the agent can load when needed. They follow a **progressive disclosure** pattern to minimize token usage and are compatible with the [agentskills.io](https://agentskills.io/specification) open standard.

技能（Skills）是智能体可按需加载的**知识文档**。

这类文档采用**渐进式展示**设计，最大限度减少令牌消耗，同时兼容 agentskills.io 开放标准。

All skills live in **`~/.hermes/skills/`** — the primary directory and source of truth. On fresh install, bundled skills are copied from the repo. Hub-installed and agent-created skills also go here. The agent can modify or delete any skill.

所有技能文件均存放于 **~/.hermes/skills/** 目录下，这是技能的主目录与权威数据源。

全新安装时，内置技能会从代码仓库自动复制至此目录；从技能市场安装的技能、以及智能体自行创建的技能，也都会保存到这里。智能体可对任意技能进行编辑或删除操作。

You can also point Hermes at **external skill directories** — additional folders scanned alongside the local one. See [External Skill Directories](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#external-skill-directories) below.

你也可以为 Hermes 指定**外部技能目录**，程序会在扫描本地技能目录的同时，一并扫描这些额外文件夹。详见下文「外部技能目录」章节。

### Using Skills

Every installed skill is automatically available as a slash command:

```sh
# In the CLI or any messaging platform:
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/plan design a rollout for migrating our auth provider

# Just the skill name loads it and lets the agent ask what you need:
/excalidraw
```

The bundled `plan` skill is a good example. Running `/plan [request]` loads the skill's instructions, telling Hermes to inspect context if needed, write a markdown implementation plan instead of executing the task, and save the result under `.hermes/plans/` relative to the active workspace/backend working directory.

内置的**plan（规划）** 技能就是一个很好的例子。

执行 `/plan [需求指令]` 时，会加载该技能的规则指引，告知 Hermes 在必要时梳理上下文，**仅生成 Markdown 格式的执行规划方案，而不直接执行任务**，并将结果保存到当前工作空间 / 后端工作目录下的 `.hermes/plans/` 文件夹中。

You can also interact with skills through natural conversation:

你也可以通过自然对话的方式与各类技能进行交互。

```sh
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

### Progressive Disclosure

Skills use a token-efficient loading pattern:

```sh
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)
Level 1: skill_view(name)        → Full content + metadata       (varies)
Level 2: skill_view(name, path)  → Specific reference file       (varies)
```

The agent only loads the full skill content when it actually needs it.

### SKILL.md Format

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]     # Optional — restrict to specific OS platforms
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # Optional — conditional activation (see below)
    requires_toolsets: [terminal]   # Optional — conditional activation (see below)
    config:                          # Optional — config.yaml settings
      - key: my.setting
        description: "What this controls"
        default: "value"
        prompt: "Prompt for setup"
---

# Skill Title

## When to Use
Trigger conditions for this skill.

## Procedure
1. Step one
2. Step two

## Pitfalls
- Known failure modes and fixes

## Verification
How to confirm it worked.
```

#### Platform-Specific Skills

Skills can restrict themselves to specific operating systems using the `platforms` field:

| Value     | Matches        |
| --------- | -------------- |
| `macos`   | macOS (Darwin) |
| `linux`   | Linux          |
| `windows` | Windows        |

```sh
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS and Linux
```

When set, the skill is automatically hidden from the system prompt, `skills_list()`, and slash commands on incompatible platforms. If omitted, the skill loads on all platforms.

#### Conditional Activation (Fallback Skills)

Skills can automatically show or hide themselves based on which tools are available in the current session. This is most useful for **fallback skills** — free or local alternatives that should only appear when a premium tool is unavailable.

技能可根据当前会话中可用的工具，自动显示或隐藏自身。这一特性对**备用技能**尤为实用 —— 这类免费或本地替代工具，仅在高级付费工具不可用时才会展示。

```sh
metadata:
  hermes:
    fallback_for_toolsets: [web]      # Show ONLY when these toolsets are unavailable
    requires_toolsets: [terminal]     # Show ONLY when these toolsets are available
    fallback_for_tools: [web_search]  # Show ONLY when these specific tools are unavailable
    requires_tools: [terminal]        # Show ONLY when these specific tools are available
```

| Field                   | Behavior                                                     |
| ----------------------- | ------------------------------------------------------------ |
| `fallback_for_toolsets` | Skill is **hidden** when the listed toolsets are available. Shown when they're missing. |
| `fallback_for_tools`    | Same, but checks individual tools instead of toolsets.       |
| `requires_toolsets`     | Skill is **hidden** when the listed toolsets are unavailable. Shown when they're present. |
| `requires_tools`        | Same, but checks individual tools.                           |

Skills without any conditional fields behave exactly as before — they're always shown.

### Secure Setup on Load

Skills can declare required environment variables without disappearing from discovery:

技能可以声明所需的环境变量，**同时仍能在检索列表中正常显示、不会被隐藏**：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

When a missing value is encountered, Hermes asks for it securely only when the skill is actually loaded in the local CLI. You can skip setup and keep using the skill. Messaging surfaces never ask for secrets in chat — they tell you to use `hermes setup` or `~/.hermes/.env` locally instead.

当检测到环境变量缺失时，Hermes **仅在本地命令行实际加载该技能时**，才会以安全方式向你索要配置。你也可以跳过配置，继续正常使用该技能的基础功能。

聊天交互界面**永远不会在对话中索要密钥等敏感信息**，只会提示你在本地执行 `hermes setup` 命令，或手动配置 `~/.hermes/.env` 文件。

Once set, declared env vars are **automatically passed through** to `execute_code` and `terminal` sandboxes — the skill's scripts can use `$TENOR_API_KEY` directly. For non-skill env vars, use the `terminal.env_passthrough` config option.

配置完成后，技能声明的环境变量会**自动透传**到代码执行沙箱和终端沙箱中，技能脚本可直接通过 `$TENOR_API_KEY` 取用。

如需透传非技能声明的普通环境变量，可配置 `terminal.env_passthrough` 选项。

#### Skill Config Settings

Skills can also declare non-secret config settings (paths, preferences) stored in `config.yaml`:

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
```

Settings are stored under `skills.config` in your config.yaml. `hermes config migrate` prompts for unconfigured settings, and `hermes config show` displays them. When a skill loads, its resolved config values are injected into the context so the agent knows the configured values automatically.

相关配置项存储在 `config.yaml` 文件的 **skills.config** 节点下。执行 `hermes config migrate` 会引导你补齐未配置的设置项；执行 `hermes config show` 可查看当前所有配置。当技能加载时，**已解析生效的配置值**会自动注入上下文，智能体可直接识别并使用这些已配置参数。

### Skill Directory Structure

```sh
~/.hermes/skills/                  # Single source of truth
├── mlops/                         # Category directory
│   ├── axolotl/
│   │   ├── SKILL.md               # Main instructions (required)
│   │   ├── references/            # Additional docs
│   │   ├── templates/             # Output formats
│   │   ├── scripts/               # Helper scripts callable from the skill
│   │   └── assets/                # Supplementary files
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent-created skill
│       ├── SKILL.md
│       └── references/
├── .hub/                          # Skills Hub state
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # Tracks seeded bundled skills
```

### External Skill Directories

If you maintain skills outside of Hermes — for example, a shared `~/.agents/skills/` directory used by multiple AI tools — you can tell Hermes to scan those directories too.

Add `external_dirs` under the `skills` section in `~/.hermes/config.yaml`:

```sh
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```

#### How it works

- **Read-only**: External dirs are only scanned for skill discovery. When the agent creates or edits a skill, it always writes to `~/.hermes/skills/`.
- **Local precedence**: If the same skill name exists in both the local dir and an external dir, the local version wins.
- **Full integration**: External skills appear in the system prompt index, `skills_list`, `skill_view`, and as `/skill-name` slash commands — no different from local skills.
- **Non-existent paths are silently skipped**: If a configured directory doesn't exist, Hermes ignores it without errors. Useful for optional shared directories that may not be present on every machine.



- **只读特性**：外部目录仅用于**扫描和发现技能**。当智能体新建或编辑技能时，只会写入 `~/.hermes/skills/` 本地主目录。
- **本地优先**：若本地目录和外部目录存在**同名技能**，**以本地版本为准**。
- **完全集成**：外部技能会纳入系统提示索引、`skills_list`、`skill_view` 中，也支持 `/技能名` 斜杠命令调用，与本地技能**使用体验完全一致**。
- **不存在路径静默跳过**：若配置的外部目录实际不存在，Hermes 会直接忽略且**不抛出报错**。适合配置非必需的共享目录，无需保证每台设备上都存在该路径。

#### Example

```sh
~/.hermes/skills/               # Local (primary, read-write)
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # External (read-only, shared)
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```

All four skills appear in your skill index. If you create a new skill called `my-custom-workflow` locally, it shadows the external version.

### Agent-Managed Skills (skill_manage tool)

The agent can create, update, and delete its own skills via the `skill_manage` tool. This is the agent's **procedural memory** — when it figures out a non-trivial workflow, it saves the approach as a skill for future reuse.

智能体可通过 `skill_manage` 工具**创建、更新和删除**自身的技能。这相当于智能体的**程序记忆**：当它梳理出一套复杂工作流程后，会把这套方法保存为技能，供后续重复使用。

#### When the Agent Creates Skills

- After completing a complex task (5+ tool calls) successfully
- When it hit errors or dead ends and found the working path
- When the user corrected its approach
- When it discovered a non-trivial workflow



- 成功完成**复杂任务**（调用工具次数达 5 次及以上）后

- 遭遇报错或陷入僵局、随后找到可行解决方案时

- 用户纠正其处理思路与方式时

- 摸索出一套**非简易、有复用价值**的工作流程时

#### Actions

| Action        | Use for                     | Key params                                             |
| ------------- | --------------------------- | ------------------------------------------------------ |
| `create`      | New skill from scratch      | `name`, `content` (full SKILL.md), optional `category` |
| `patch`       | Targeted fixes (preferred)  | `name`, `old_string`, `new_string`                     |
| `edit`        | Major structural rewrites   | `name`, `content` (full SKILL.md replacement)          |
| `delete`      | Remove a skill entirely     | `name`                                                 |
| `write_file`  | Add/update supporting files | `name`, `file_path`, `file_content`                    |
| `remove_file` | Remove a supporting file    | `name`, `file_path`                                    |

> The `patch` action is preferred for updates — it's more token-efficient than `edit` because only the changed text appears in the tool call.

### Skills Hub

Browse, search, install, and manage skills from online registries, `skills.sh`, direct well-known skill endpoints, and official optional skills.

#### Common commands

```sh
hermes skills browse                              # Browse all hub skills (official first)
hermes skills browse --source official            # Browse only official optional skills
hermes skills search kubernetes                   # Search all sources
hermes skills search react --source skills-sh     # Search the skills.sh directory
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect openai/skills/k8s           # Preview before installing
hermes skills install openai/skills/k8s           # Install with security scan
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install https://sharethis.chat/SKILL.md              # Direct URL (single-file SKILL.md)
hermes skills install https://example.com/SKILL.md --name my-skill # Override name when frontmatter has none
hermes skills list --source hub                   # List hub-installed skills
hermes skills check                               # Check installed hub skills for upstream updates
hermes skills update                              # Reinstall hub skills with upstream changes when needed
hermes skills audit                               # Re-scan all hub skills for security
hermes skills uninstall k8s                       # Remove a hub skill
hermes skills reset google-workspace              # Un-stick a bundled skill from "user-modified" (see below)
hermes skills reset google-workspace --restore    # Also restore the bundled version, deleting your local edits
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # Export skill config
hermes skills tap add myorg/skills-repo           # Add a custom GitHub source
```

#### Supported hub sources

| Source                                     | Example                                                      | Notes                                                        |
| ------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `official`                                 | `official/security/1password`                                | Optional skills shipped with Hermes.<br />Hermes 自带的**可选官方技能**。 |
| `skills-sh`                                | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | Searchable via `hermes skills search <query> --source skills-sh`. Hermes resolves alias-style skills when the skills.sh slug differs from the repo folder.<br />可通过命令 `hermes skills search <关键词> --source skills-sh` 检索。当 skills.sh 的标识别名与仓库文件夹名不一致时，Hermes 会自动解析别名形式的技能。 |
| `well-known`                               | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | Skills served directly from `/.well-known/skills/index.json` on a website. Search using the site or docs URL.<br />从网站 `/.well-known/skills/index.json` 路径直接提供的技能。可使用站点或文档网址进行检索。 |
| `url`                                      | `https://sharethis.chat/SKILL.md`                            | Direct HTTP(S) URL to a single-file `SKILL.md`. Name resolution: frontmatter → URL slug → interactive prompt → `--name` flag.<br />单个技能文件 `SKILL.md` 的标准 HTTP/HTTPS 直链。名称解析优先级：文件前置元数据 → 网址路径别名 → 交互式提示命名 → `--name` 指定参数。 |
| `github`                                   | `openai/skills/k8s`                                          | Direct GitHub repo/path installs and custom taps.<br />直接通过 GitHub 仓库 / 路径 安装，也支持自定义仓库源配置。 |
| `clawhub`, `lobehub`, `claude-marketplace` | Source-specific identifiers                                  | Community or marketplace integrations.<br />对应各类社区或技能市场的接入源。 |

#### Integrated hubs and registries

Hermes currently integrates with these skills ecosystems and discovery sources:

##### 1. Official optional skills (`official`)

These are maintained in the Hermes repository itself and install with builtin trust.

- Catalog: [Official Optional Skills Catalog](https://hermes-agent.nousresearch.com/docs/reference/optional-skills-catalog)
- Source in repo: `optional-skills/`
- Example:

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

##### 2. skills.sh (`skills-sh`)

This is Vercel's public skills directory. Hermes can search it directly, inspect skill detail pages, resolve alias-style slugs, and install from the underlying source repo.

- Directory: [skills.sh](https://skills.sh/)
- CLI/tooling repo: [vercel-labs/skills](https://github.com/vercel-labs/skills)
- Official Vercel skills repo: [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- Example:

```bash
hermes skills search react --source skills-sh
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

##### 3. Well-known skill endpoints (`well-known`)

This is URL-based discovery from sites that publish `/.well-known/skills/index.json`. It is not a single centralized hub — it is a web discovery convention.

- Example live endpoint: [Mintlify docs skills index](https://mintlify.com/docs/.well-known/skills/index.json)
- Reference server implementation: [vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- Example:

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

##### 4. Direct GitHub skills (`github`)

Hermes can install directly from GitHub repositories and GitHub-based taps. This is useful when you already know the repo/path or want to add your own custom source repo.

Default taps (browsable without any setup):

- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [garrytan/gstack](https://github.com/garrytan/gstack)
- Example:

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

##### 5. ClawHub (`clawhub`)

A third-party skills marketplace integrated as a community source.

- Site: [clawhub.ai](https://clawhub.ai/)
- Hermes source id: `clawhub`

##### 6. Claude marketplace-style repos (`claude-marketplace`)

Hermes supports marketplace repos that publish Claude-compatible plugin/marketplace manifests.

Known integrated sources include:

- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)

Hermes source id: `claude-marketplace`

##### 7. LobeHub (`lobehub`)

Hermes can search and convert agent entries from LobeHub's public catalog into installable Hermes skills.

- Site: [LobeHub](https://lobehub.com/)
- Public agents index: [chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- Backing repo: [lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes source id: `lobehub`

##### 8. Direct URL (`url`)

Install a single-file `SKILL.md` directly from any HTTP(S) URL — useful when an author hosts a skill on their own site (no hub listing, no GitHub path to type). Hermes fetches the URL, parses the YAML frontmatter, security-scans it, and installs.

- Hermes source id: `url`
- Identifier: the URL itself (no prefix needed)
- Scope: **single-file `SKILL.md`** only. Multi-file skills with `references/` or `scripts/` need a manifest and should be published via one of the other sources above.

```bash
hermes skills install https://sharethis.chat/SKILL.md
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```

Name resolution, in order:

1. `name:` field in the SKILL.md YAML frontmatter (recommended — every well-formed skill has one).
2. Parent directory name from the URL path (e.g. `.../my-skill/SKILL.md` → `my-skill`, or `.../my-skill.md` → `my-skill`), when it's a valid identifier (`^[a-z][a-z0-9_-]*$`).
3. Interactive prompt on a terminal with a TTY.
4. On non-interactive surfaces (the `/skills install` slash command inside the TUI, gateway platforms, scripts), a clean error pointing at the `--name` override.

技能名称解析优先级（按顺序）

1. **SKILL.md 的 YAML 前置元数据中的 name 字段**（推荐规范 —— 格式标准的技能都应配置该字段）。
2. 从 URL 路径中提取**父目录名**（例如：`.../my-skill/SKILL.md` 解析为 `my-skill`；`.../my-skill.md` 解析为 `my-skill`），且名称需符合合法标识符规则：仅小写字母开头，后跟小写字母、数字、下划线、连字符。
3. 在**TTY 交互式终端**中，弹出交互提示让用户手动输入名称。
4. 在**非交互式场景**（终端界面 TUI 内的 `/skills install` 斜杠命令、网关平台、脚本执行）下，直接返回清晰报错，并提示用 `--name` 参数手动指定名称。

```bash
# Frontmatter has no name and the URL slug is unhelpful — supply one:
hermes skills install https://example.com/SKILL.md --name sharethis-chat

# Or inside a chat session:
/skills install https://example.com/SKILL.md --name sharethis-chat
```

Trust level is always `community` — the same security scan runs as for every other source. The URL is stored as the install identifier, so `hermes skills update` re-fetches from the same URL automatically when you want to refresh.

此类来源的**信任等级固定为社区级**，会和其他所有技能来源执行完全一致的安全扫描。安装时会将原始 URL 保存为安装标识，后续执行 `hermes skills update` 刷新技能时，会自动从原 URL 重新拉取更新。

#### Security scanning and `--force`

All hub-installed skills go through a **security scanner** that checks for data exfiltration, prompt injection, destructive commands, supply-chain signals, and other threats.

所有从技能市场安装的技能都会经过**安全扫描器**检测，防范**数据外泄、提示注入、破坏性命令、供应链风险**及其他安全威胁。

`hermes skills inspect ...` now also surfaces upstream metadata when available:

- repo URL
- skills.sh detail page URL
- install command
- weekly installs
- upstream security audit statuses
- well-known index/endpoint URLs

执行 `hermes skills inspect ...` 命令时，若有相关信息，还会展示上游元数据：

- 代码仓库地址
- skills.sh 技能详情页地址
- 安装命令
- 周安装量
- 上游安全审计状态
- 知名索引 / 服务接口地址

Use `--force` when you have reviewed a third-party skill and want to override a non-dangerous policy block:

若你已自行审阅第三方技能，并希望**绕过非高危策略拦截**，可使用 `--force` 参数：

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

Important behavior:

- `--force` can override policy blocks for caution/warn-style findings.
- `--force` does **not** override a `dangerous` scan verdict.
- Official optional skills (`official/...`) are treated as builtin trust and do not show the third-party warning panel.

重要规则说明

1. `--force` 仅可覆盖**警示类、提醒类**的策略拦截。
2. 若安全扫描判定为**高危风险**，`--force` **无法强行绕过**。
3. 官方可选技能（`official/...`）享有**内置可信等级**，不会展示第三方技能的风险警告面板。

#### Trust levels

| Level       | Source                                                       | Policy                                                       |
| ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `builtin`   | Ships with Hermes                                            | Always trusted                                               |
| `official`  | `optional-skills/` in the repo                               | Builtin trust, no third-party warning                        |
| `trusted`   | Trusted registries/repos such as `openai/skills`, `anthropics/skills` | More permissive policy than community sources                |
| `community` | Everything else (`skills.sh`, well-known endpoints, custom GitHub repos, most marketplaces) | Non-dangerous findings can be overridden with `--force`; `dangerous` verdicts stay blocked |

#### Update lifecycle

The hub now tracks enough provenance to re-check upstream copies of installed skills:

```sh
hermes skills check          # Report which installed hub skills changed upstream
hermes skills update         # Reinstall only the skills with updates available
hermes skills update react   # Update one specific installed hub skill
```

This uses the stored source identifier plus the current upstream bundle content hash to detect drift.

该功能通过**已保存的源标识**，结合**当前上游捆绑内容哈希值**，来检测内容是否发生**变更**。

#### Publishing a custom skill tap

If you want to share a curated set of skills — for your team, your org, or publicly — you can publish them as a **tap**: a GitHub repository other Hermes users add with `hermes skills tap add <owner/repo>`. No server, no registry sign-up, no release pipeline. Just a directory of `SKILL.md` files.

如果你想向团队、公司内部或公开分享**一套精选技能合集**，可以将其发布为**技能源（tap）**：只需创建一个 GitHub 仓库，其他 Hermes 用户即可通过命令 `hermes skills tap add <用户名/仓库名>` 来添加使用。无需搭建服务器、无需注册镜像仓库、也不用发布流水线；**只要一个存放若干 SKILL.md 文件的目录即可**。

##### Repo layout

A tap is any GitHub repo (public or private — private needs `GITHUB_TOKEN`) laid out like this:

```text
owner/repo
├── skills/                       # default path; configurable per-tap
│   ├── my-workflow/
│   │   ├── SKILL.md              # required
│   │   ├── references/           # optional supporting files
│   │   ├── templates/
│   │   └── scripts/
│   ├── another-skill/
│   │   └── SKILL.md
│   └── third-skill/
│       └── SKILL.md
└── README.md                     # optional but helpful
```

Rules:

- Each skill lives in its own directory under the tap's root path (default `skills/`).
- The directory name becomes the skill's install slug.
- Each skill directory must contain a `SKILL.md` with standard [SKILL.md frontmatter](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#skillmd-format) (`name`, `description`, plus optional `metadata.hermes.tags`, `version`, `author`, `platforms`, `metadata.hermes.config`).
- Subdirectories like `references/`, `templates/`, `scripts/`, `assets/` are downloaded alongside `SKILL.md` at install time.
- Skills whose directory name starts with `.` or `_` are ignored.

规则说明：

- 每个技能独立存放于 **技能源（tap）** 根目录下的单独文件夹中，默认根目录为 `skills/`。

- 文件夹名称将作为该技能的**安装标识名（slug）**。

- 每个技能文件夹内必须包含一份 `SKILL.md` 文件，且需遵循标准前置元数据格式：需配置 `name`、`description`，还可可选配置 `metadata.hermes.tags`、`version`、`author`、`platforms`、`metadata.hermes.config` 等字段。

- `references/`、`templates/`、`scripts/`、`assets/` 这类子目录，会在安装技能时，与 `SKILL.md` 一并下载。

- 文件夹名以 **.** 或 **_** 开头的技能，会被自动忽略。

Hermes discovers skills by listing every subdirectory of the tap path and probing each for `SKILL.md`.

Hermes 的技能发现机制：遍历技能源路径下的所有子目录，逐一检测目录内是否存在 `SKILL.md` 文件。



##### Minimal tap example

```sh
my-org/hermes-skills
└── skills/
    └── deploy-runbook/
        └── SKILL.md
```

`skills/deploy-runbook/SKILL.md`:

```sh
---
name: deploy-runbook
description: Our deployment runbook — services, rollback, Slack channels
version: 1.0.0
author: My Org Platform Team
metadata:
  hermes:
    tags: [deployment, runbook, internal]
---

# Deploy Runbook

Step 1: ...
```

After pushing that to GitHub, any Hermes user can subscribe and install:

```sh
hermes skills tap add my-org/hermes-skills
hermes skills search deploy
hermes skills install my-org/hermes-skills/deploy-runbook
```

##### Non-default paths

If your skills don't live under `skills/` (common when you're adding a `skills/` subtree to an existing project), edit the tap entry in `~/.hermes/.hub/taps.json`:

```sh
{
  "taps": [
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}
  ]
}
```

The `hermes skills tap add` CLI defaults new taps to `path: "skills/"`; edit the file directly if you need a different path. `hermes skills tap list` shows the effective path per tap.

##### Installing individual skills directly (without adding a tap)

Users can also install a single skill from any public GitHub repo without adding the whole repo as a tap:

```sh
hermes skills install owner/repo/skills/my-workflow
```

Useful when you want to share one skill without asking the user to subscribe to your whole registry.

##### Trust levels for taps

New taps are assigned `community` trust by default. Skills installed from them run through the standard security scan and show the third-party warning panel on first install. If your org or a widely-trusted source should get higher trust, add its repo to `TRUSTED_REPOS` in `tools/skills_hub.py` (requires a Hermes core PR).

新增的自定义技能源（tap）默认被赋予**社区级信任等级**。从这类源安装的技能会经过标准安全扫描，且首次安装时会展示第三方技能风险警告面板。如果你的企业组织或高可信度技能源需要提升信任等级，可将其仓库加入 `tools/skills_hub.py` 文件中的 `TRUSTED_REPOS` 可信仓库列表（需向 Hermes 核心代码仓库提交合并 PR）。

##### Tap management

```sh
hermes skills tap list                                # show all configured taps
hermes skills tap add myorg/skills-repo               # add (default path: skills/)
hermes skills tap remove myorg/skills-repo            # remove
```

Inside a running session:

```sh
/skills tap list
/skills tap add myorg/skills-repo
/skills tap remove myorg/skills-repo
```

Taps are stored in `~/.hermes/.hub/taps.json` (created on demand).

### Bundled skill updates (`hermes skills reset`)

Hermes ships with a set of bundled skills in `skills/` inside the repo. On install and on every `hermes update`, a sync pass copies those into `~/.hermes/skills/` and records a manifest at `~/.hermes/skills/.bundled_manifest` mapping each skill name to the content hash at the time it was synced (the **origin hash**).

Hermes 在代码仓库的 `skills/` 目录中自带了一组**内置技能**。在安装时，以及每次执行 `hermes update` 更新时，系统会执行一次同步操作，将这些内置技能复制到 `~/.hermes/skills/` 目录下，并在 `~/.hermes/skills/.bundled_manifest` 生成一份清单文件。该清单会记录每个技能名称与其**同步时的内容哈希值**（即**原始哈希**）的对应关系。

On each sync, Hermes recomputes the hash of your local copy and compares it to the origin hash:

- **Unchanged** → safe to pull upstream changes, copy the new bundled version in, record the new origin hash.
- **Changed** → treated as **user-modified** and skipped forever, so your edits never get stomped.

每次同步时，Hermes 都会重新计算你本地副本的哈希值，并与原始哈希值进行比对：

- **未被修改** → 可以安全拉取上游更新，覆盖写入新的内置版本，并记录新的原始哈希。
- **已被修改** → 判定为**用户自定义修改**，永久跳过同步，确保你的编辑不会被覆盖。

The protection is good, but it has one sharp edge. If you edit a bundled skill and then later want to abandon your changes and go back to the bundled version by just copy-pasting from `~/.hermes/hermes-agent/skills/`, the manifest still holds the *old* origin hash from whenever the last successful sync ran. Your fresh copy-paste contents (current bundled hash) won't match that stale origin hash, so sync keeps flagging it as user-modified.

这项保护机制很实用，但存在一个**注意事项**。如果你编辑过某个内置技能，之后想放弃修改，直接从 `~/.hermes/hermes-agent/skills/` 复制粘贴官方原版内容恢复回去，清单文件中依然保留着**上一次成功同步时的旧原始哈希**。你新粘贴回去的官方原版内容（当前内置哈希）与这个过期的原始哈希不匹配，因此同步功能会一直将其标记为**用户已修改**。

`hermes skills reset` is the escape hatch:

```sh
# Safe: clears the manifest entry for this skill. Your current copy is preserved,
# but the next sync re-baselines against it so future updates work normally.
hermes skills reset google-workspace

# Full restore: also deletes your local copy and re-copies the current bundled
# version. Use this when you want the pristine upstream skill back.
hermes skills reset google-workspace --restore

# Non-interactive (e.g. in scripts or TUI mode) — skip the --restore confirmation.
hermes skills reset google-workspace --restore --yes
```

The same command works in chat as a slash command:

```sh
/skills reset google-workspace
/skills reset google-workspace --restore
```

#### Slash commands (inside chat)

All the same commands work with `/skills`:

```sh
/skills browse
/skills search react --source skills-sh
/skills search https://mintlify.com/docs --source well-known
/skills inspect skills-sh/vercel-labs/json-render/json-render-react
/skills install openai/skills/skill-creator --force
/skills check
/skills update
/skills reset google-workspace
/skills list
```

Official optional skills still use identifiers like `official/security/1password` and `official/migration/openclaw-migration`.



