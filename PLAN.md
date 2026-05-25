# PLAN.md

> SCOPE LOCK: 创建一个精简 `v1/` 目录，只保留模型调用、Agent、多轮对话、Skills、核心开发工具、Plan/Todo、长任务委托与长上下文压缩核心能力。

## Research Summary

- `docs/2026-05-25-hermes-agent-source-analysis.md` — 已完成全局源码分析，确认当前项目是 Python AI Agent / CLI / 多平台消息网关 / 工具调用框架，核心能力最终汇聚到 `run_agent.AIAgent`、`agent/`、`model_tools.py`、`tools/`、skills 与 compression 模块。
- `pyproject.toml` — 项目 Python 版本为 3.11+，主入口包括 `hermes`、`hermes-agent`、`hermes-acp`；v1 不改现有入口，避免影响当前产品形态。
- `run_agent.py` — `AIAgent` 已变成兼容门面，初始化、对话循环、system prompt、模型客户端创建大量 forward 到 `agent/` 子模块。v1 应直接建立更小的 Agent，而不是继续继承完整门面复杂度。
- `agent/agent_init.py` — 当前初始化承担 provider/model/toolsets/session/callbacks/memory/compression 等大量职责。v1 只保留模型配置、消息历史、工具注册表、skills、todo store、compression 配置。
- `agent/conversation_loop.py` — 当前核心循环包含 system prompt 构建、模型调用、tool calls、持久化、fallback、compression、memory/plugin hook 等。v1 应保留“用户消息 → 模型 → 工具调用 → 模型继续 → 最终响应”的最小闭环，去掉 Gateway、DB session split、plugin hook、复杂 fallback。
- `agent/tool_executor.py` — 当前负责工具调用执行、并发/顺序调度、结果归一化与预算控制。v1 应吸收其核心思想：统一执行 tool calls、把结果作为 `tool` message 回填、限制单次结果长度；不实现复杂路径冲突调度。
- `agent/system_prompt.py` — 当前 system prompt 分 stable/context/volatile 三层。v1 可保留简化版：身份/行为规则、可用技能索引、todo/long-task/compression 状态。
- `agent/agent_runtime_helpers.py` — 当前集中模型客户端创建、provider 解析和运行时辅助逻辑。v1 只吸收 OpenAI-compatible client 创建与环境变量读取，不保留完整 provider matrix。
- `agent/messages.py` / message normalization 相关逻辑 — 当前项目存在大量 provider/message 兼容处理。v1 只保留标准 OpenAI chat messages：`system`、`user`、`assistant`、`tool`。
- `agent/file_safety.py`、`agent/tool_guardrails.py` — 当前用于完整工具安全边界。v1 在 `dev_tools.py` 中吸收最关键的 workspace path 限制、命令超时和结果截断，并新增简化版 tool-loop guardrail，防止重复失败、无进展读操作和工具死循环。
- `agent/transports/base.py` — 定义 provider transport 抽象：`convert_messages`、`convert_tools`、`build_kwargs`、`normalize_response`。v1 可保留这个抽象思想，但只实现 OpenAI-compatible Chat Completions。
- `agent/transports/types.py` — `ToolCall`、`Usage`、`NormalizedResponse` 是清晰的 provider-independent 数据结构，适合作为 v1 模型层基础。
- `agent/transports/chat_completions.py` — 现有 Chat Completions transport 处理 provider 字段清理、tool schema 转换、response normalize。v1 可以提取简化版，仅支持标准 OpenAI-compatible `client.chat.completions.create`。
- `agent/chat_completion_helpers.py` — 当前 `interruptible_api_call` 使用后台线程支持中断和 stale-call 检测。v1 初版保留同步/超时模型调用即可，长任务由委托层隔离，不复制复杂中断机制。
- `agent/error_classifier.py`、`agent/retry_utils.py`、`agent/rate_limit_tracker.py` — 当前提供 API 错误分类、jittered backoff 和 rate-limit header 解析。v1 应纳入轻量版：识别 context overflow/rate limit/server error，支持有限重试和触发 compression。
- `agent/credential_pool.py` — 当前提供多凭证池和 failover。v1 不实现完整池化，但配置层要为单个 API key/base_url/model 留清晰边界，credential pool 作为 deferred。
- `tools/registry.py` — 当前 `ToolRegistry` 支持自注册、availability check、async bridge、动态 schema、结果大小限制。v1 应保留 schema + handler + dispatch 的小注册表，避免 discovery/import side effects。
- `tools/approval.py` — 当前是危险命令审批的核心，包括 hardline blocklist、危险模式检测、session-scoped approval 和永久 allowlist。v1 若包含 bash，必须吸收最小 hardline blocklist 与危险命令检测；交互式审批可先用配置开关/抛错代替。
- `tools/environments/base.py`、`tools/environments/local.py` — 当前抽象 terminal 执行环境、CWD/env snapshot、activity callback、interrupt。v1 不实现多后端环境，但应把本地执行封装为 `ExecutionEnvironment`，避免 bash 逻辑散落在 tool handler 中。
- `tools/checkpoint_manager.py` — 当前在写文件、patch、危险 terminal 前做透明快照并支持回滚。v1 若包含 write/bash，应纳入简化 checkpoint：至少在 write_file 前保存 `.v1-checkpoints/` 快照；完整共享 git shadow store deferred。
- `tools/mcp_tool.py` — 当前接入 MCP 外部工具。v1 初版不实现 MCP，但工具注册表应保留外部工具扩展口；MCP 作为 deferred。
- `model_tools.py` — 当前是工具定义过滤与 tool call 派发兼容层，包含插件 hook、审批、安全通知等。v1 不复用整层，只保留 `get_tool_definitions()` 与 `dispatch_tool_call()` 的核心概念。
- `toolsets.py` — 当前工具集覆盖 web/file/terminal/browser/memory/delegation/cron/send_message 等。v1 默认内置核心开发工具集：`file read/write/search`、`bash`、`skills`、`todo`、`delegate`；web/browser/memory/cron/send_message 暂不纳入。
- `tools/todo_tool.py` — `TodoStore` 是 session-scoped in-memory plan/todo，支持 read/write/merge 和 compression 后注入 active items。v1 可直接借鉴这个设计，作为 plan 核心。
- `agent/skill_utils.py` — 当前提供 frontmatter 解析、技能目录发现、平台/禁用过滤、config vars 等。v1 只保留 `SKILL.md` 读取、frontmatter 解析、名称/描述/内容字段。
- `agent/skill_preprocessing.py` — 当前支持 `${HERMES_SKILL_DIR}`、`${HERMES_SESSION_ID}` 和可选 inline shell。v1 保留模板变量替换，不默认启用 inline shell，降低复杂度与安全风险。
- `agent/skill_commands.py` — 当前负责 slash skill 扫描、解析和 invocation prompt 构建。v1 保留 `/skill-name instruction` 的最小解析与加载消息构建。
- `agent/prompt_builder.py` — 当前构建 skills system prompt index 并带缓存/快照。v1 可每次从 configured skills dirs 读取轻量索引，不做 disk snapshot。
- `tools/skills_tool.py` — 当前包含 skill readiness、platform/setup、prompt-injection 检测等。v1 保留基本注入风险字符串检测和 “列出/加载技能” 能力，跳过复杂 setup/status。
- `tools/delegate_tool.py` — 当前长任务通过 child `AIAgent` 隔离上下文，父级只看到 summary，并阻止递归/危险工具。v1 保留这种架构：创建子 Agent、限制工具集、返回 summary；不保留 Gateway/TUI 控制、terminal session 管理。
- `agent/context_compressor.py` — 当前 compression 保护 head/tail、总结 middle、裁剪旧 tool output、剥离历史 media。v1 保留 head/tail + middle summary + tool result pruning 的核心算法。
- `agent/conversation_compression.py` — 当前负责 compression feasibility、session split、DB 持久化、plugin/memory 通知。v1 只实现纯 message-list compression，不做 DB/session rotation。
- `hermes_cli/config.py` — 当前负责配置文件、env/secrets、默认值和解析失败降级。v1 应提供最小配置加载：显式参数优先，其次环境变量；不读取完整 `~/.hermes/config.yaml`。
- `gateway/session.py`、`hermes_state.py` — 当前提供 session store、reset policy、SQLite messages/FTS/usage。v1 不引入数据库，先用进程内 message history；但 `Agent` 应暴露 `reset()` 与可注入 `session_id`，为后续持久化留边界。
- `gateway/`、`web/`、`ui-tui/`、`acp_adapter/`、`cron/` — 属于完整产品壳层或平台能力，不纳入 v1 核心目录。

---

## Implementation Plan

### Overview

在仓库根目录新增 `v1/`，实现一个可读、可运行、低依赖的核心 Agent 版本。它不替换现有 Hermes Agent，只作为源码整合版，展示并保留模型调用、多轮对话、skills、plan/todo、长任务委托和上下文压缩的最小闭环。

### Constraints (DO NOT VIOLATE)

- 现有 `run_agent.py`、`agent/`、`tools/`、`hermes_cli/`、`gateway/` 不做行为改造；v1 是新增目录，避免破坏当前功能和测试。
- 不创建新的 CLI 入口点到 `pyproject.toml`，除非后续用户明确要求；先让 v1 通过模块/API 使用。
- 不复制 Gateway、Web UI、TUI、ACP、Cron、SQLite state、插件系统、复杂 provider fallback。
- 不启用 skills inline shell expansion；v1 skills 只做静态文本加载和安全检查。
- 默认提供核心开发工具：受限文件读写/搜索与 bash 执行；实现时必须限制路径在项目目录内，并保留命令超时。v1 长任务委托只允许 v1 内置工具集。
- 不做向后兼容 shim；v1 目录是独立精简实现。

### Proposed `v1/` layout

```text
v1/
├── __init__.py              # 导出 Agent、AgentConfig、chat helper
├── agent.py                 # 精简 Agent：多轮历史、tool loop、compression hook
├── config.py                # AgentConfig / ModelConfig / CompressionConfig
├── models.py                # OpenAI-compatible Chat Completions 调用与响应归一化
├── types.py                 # Message、ToolCall、Usage、ModelResponse 等数据结构
├── prompts.py               # system prompt + skills index + plan state 注入
├── compression.py           # 长上下文压缩：head/tail 保护 + middle summary + tool 裁剪
├── long_tasks.py            # 子 Agent 委托执行与 summary 返回
├── skills.py                # SKILL.md 发现、frontmatter、加载、slash invocation
├── planning.py              # TodoStore / todo tool / plan 注入文本
├── tools.py                 # 小型 ToolRegistry 与内置工具注册/guardrail
├── dev_tools.py             # 文件读写/搜索与 bash 执行等核心开发工具
├── execution.py             # 本地执行环境、cwd/env、命令超时
├── safety.py                # path 限制、危险命令检测、结果截断、checkpoint
└── README.md                # v1 使用说明、范围、示例
```

### Steps

#### Step 1: Create v1 package skeleton
- **File**: `v1/__init__.py`
- **Change**: 导出 v1 公共 API。
- **Sketch**:
  ```python
  from .agent import Agent
  from .config import AgentConfig, ModelConfig
  ```
- [ ] done

- **File**: `v1/config.py`
- **Change**: 定义最小配置 dataclasses。
- **Sketch**:
  ```python
  @dataclass
  class ModelConfig:
      model: str
      base_url: str | None = None
      api_key: str | None = None
      timeout: float = 120.0

  @dataclass
  class AgentConfig:
      model: ModelConfig
      max_iterations: int = 20
      auto_compress_tokens: int = 80_000
      skills_dirs: list[Path] = field(default_factory=list)
  ```
- [ ] done

#### Step 2: Add shared types
- **File**: `v1/types.py`
- **Change**: 提取并简化 `agent/transports/types.py` 的数据结构。
- **Sketch**:
  ```python
  @dataclass
  class ToolCall:
      id: str | None
      name: str
      arguments: str

  @dataclass
  class ModelResponse:
      content: str | None
      tool_calls: list[ToolCall]
      finish_reason: str
      usage: Usage | None = None
  ```
- [ ] done

#### Step 3: Implement OpenAI-compatible model layer
- **File**: `v1/models.py`
- **Change**: 实现最小 Chat Completions client wrapper。
- **Sketch**:
  ```python
  class ChatModel:
      def complete(self, messages, tools=None) -> ModelResponse: ...
  ```
- **Reference**: `agent/transports/chat_completions.py`, `agent/chat_completion_helpers.py`。
- [ ] done

#### Step 4: Implement minimal tool registry
- **File**: `v1/tools.py`
- **Change**: 实现 `ToolRegistry.register()`、`definitions()`、`dispatch()`，注册 `todo`、`skill`、`delegate`、文件工具与 bash 工具。
- **Sketch**:
  ```python
  class ToolRegistry:
      def register(self, name: str, schema: dict, handler: Callable[..., str]) -> None: ...
      def definitions(self) -> list[dict]: ...
      def dispatch(self, name: str, args: dict, context: ToolContext) -> str: ...
  ```
- **Reference**: `tools/registry.py`, `model_tools.py`。
- [ ] done

#### Step 4.1: Implement core development tools
- **File**: `v1/dev_tools.py`
- **Change**: 实现项目目录内的文件读取、写入、文本搜索和带超时的 bash 执行。
- **Sketch**:
  ```python
  def read_file(path: str, context: ToolContext) -> str: ...
  def write_file(path: str, content: str, context: ToolContext) -> str: ...
  def search_text(query: str, path: str | None, context: ToolContext) -> str: ...
  def run_bash(command: str, timeout: float, context: ToolContext) -> str: ...
  ```
- **Safety**: 文件路径必须解析到 `workspace_root` 内；bash 通过 `ExecutionEnvironment.run()` 执行，不做后台常驻进程。
- [ ] done

#### Step 4.2: Implement safety and execution infrastructure
- **File**: `v1/safety.py`
- **Change**: 实现 workspace path validation、危险命令 hardline blocklist、结果截断、写入前 checkpoint。
- **Sketch**:
  ```python
  def ensure_workspace_path(path: str, root: Path) -> Path: ...
  def detect_dangerous_command(command: str) -> str | None: ...
  def create_checkpoint(path: Path, root: Path) -> str | None: ...
  def truncate_result(text: str, limit: int) -> str: ...
  ```
- **Reference**: `tools/approval.py`, `tools/checkpoint_manager.py`, `tools/path_security.py`, `tools/tool_output_limits.py`。
- [ ] done

- **File**: `v1/execution.py`
- **Change**: 实现本地命令执行环境，集中处理 cwd、env、timeout、stdout/stderr 合并。
- **Sketch**:
  ```python
  class ExecutionEnvironment:
      def run(self, command: str, timeout: float) -> CommandResult: ...
  ```
- **Reference**: `tools/environments/base.py`, `tools/environments/local.py`, `tools/terminal_tool.py`。
- [ ] done

#### Step 5: Implement planning/todo core
- **File**: `v1/planning.py`
- **Change**: 基于 `tools/todo_tool.py` 实现 `TodoStore`、schema、handler、active task injection。
- **Sketch**:
  ```python
  class TodoStore:
      def write(self, todos: list[dict], merge: bool = False) -> list[dict]: ...
      def format_for_injection(self) -> str | None: ...
  ```
- [ ] done

#### Step 6: Implement skills subsystem
- **File**: `v1/skills.py`
- **Change**: 实现 `SKILL.md` 扫描、frontmatter 解析、skills index、slash invocation prompt。
- **Sketch**:
  ```python
  class SkillManager:
      def list_skills(self) -> list[Skill]: ...
      def load(self, name: str, instruction: str = "") -> str: ...
      def build_index_prompt(self) -> str: ...
  ```
- **Reference**: `agent/skill_utils.py`, `agent/skill_commands.py`, `agent/skill_preprocessing.py`, `tools/skills_tool.py`。
- [ ] done

#### Step 7: Implement compression core
- **File**: `v1/compression.py`
- **Change**: 实现 token 近似、head/tail 保护、middle summary、旧 tool result 裁剪。
- **Sketch**:
  ```python
  class ContextCompressor:
      def maybe_compress(self, messages: list[dict], model: ChatModel, focus: str | None = None) -> list[dict]: ...
  ```
- **Reference**: `agent/context_compressor.py`, `agent/conversation_compression.py`。
- [ ] done

#### Step 8: Implement long-task delegation
- **File**: `v1/long_tasks.py`
- **Change**: 创建 child `Agent`，使用独立 history、受限 tools，返回 summary。
- **Sketch**:
  ```python
  class LongTaskRunner:
      def run(self, prompt: str, parent_config: AgentConfig) -> str: ...
  ```
- **Reference**: `tools/delegate_tool.py`。
- [ ] done

#### Step 9: Implement Agent loop
- **File**: `v1/agent.py`
- **Change**: 整合 model、registry、skills、todo、compression、tool guardrail，实现多轮对话和工具调用循环。
- **Sketch**:
  ```python
  class Agent:
      def chat(self, message: str) -> str: ...
      def run(self, message: str) -> AgentResult: ...
  ```
- **Core loop**:
  1. append user message
  2. build system prompt
  3. maybe compress history
  4. call model with tool definitions
  5. check tool-loop guardrail
  6. execute tool calls
  7. append tool results
  8. continue until final answer or max iterations
- **Reference**: `agent/conversation_loop.py`, `agent/tool_executor.py`, `agent/agent_init.py`, `agent/system_prompt.py`, `agent/agent_runtime_helpers.py`, `run_agent.py`。
- [ ] done

#### Step 10: Add v1 documentation and smoke validation
- **File**: `v1/README.md`
- **Change**: 写明 v1 范围、配置方式、最小使用示例、与完整 Hermes 的差异。
- **Validation**:
  ```bash
  python -m compileall v1
  python - <<'PY'
  from v1 import Agent, AgentConfig, ModelConfig
  print(AgentConfig(model=ModelConfig(model="test")))
  PY
  ```
- [ ] done

### Files to modify / create

| File | Change | Why |
|------|--------|-----|
| `PLAN.md` | create/update | 保存研究结论与审批前实现方案 |
| `v1/__init__.py` | create | v1 包入口 |
| `v1/config.py` | create | 最小运行配置 |
| `v1/types.py` | create | 模型和工具通用数据结构 |
| `v1/models.py` | create | OpenAI-compatible 模型调用 |
| `v1/tools.py` | create | 小型工具注册与派发 |
| `v1/dev_tools.py` | create | 核心开发工具：文件读写/搜索与 bash |
| `v1/execution.py` | create | 本地命令执行环境 |
| `v1/safety.py` | create | 路径/命令安全、结果截断、checkpoint |
| `v1/planning.py` | create | plan/todo 核心能力 |
| `v1/skills.py` | create | skills 发现与加载 |
| `v1/compression.py` | create | 长上下文压缩 |
| `v1/long_tasks.py` | create | 长任务委托 |
| `v1/agent.py` | create | 多轮 agent loop |
| `v1/README.md` | create | v1 范围与用法说明 |

### What will NOT change

- 不修改现有 Hermes CLI、Gateway、ACP、TUI/Web UI 入口。
- 不改 `pyproject.toml` entry points。
- 不迁移现有 tests 或重构原模块。
- 不引入 SQLite session persistence。
- 不实现 Telegram/Discord/Slack/WhatsApp gateway。
- 不实现 cron、memory、browser、computer-use、kanban、send_message。
- 不实现完整 provider abstraction/fallback/reasoning/prompt-cache 兼容层。
- 不实现完整 MCP 客户端、多执行后端、共享 git checkpoint store、credential pool；只保留扩展边界或轻量替代。

### Risks / trade-offs

- v1 会比完整 Hermes 少很多 guardrails 和平台能力；优点是核心流程清晰，缺点是不适合作为完整产品替代。
- 不复制 `hermes_state.py` 意味着多轮对话只在进程内存在；如果需要长期会话，后续应添加 JSON 或 SQLite persistence。
- 简化模型层只支持 OpenAI-compatible Chat Completions；如果要支持 Responses API 或 Claude 原生 API，需要后续扩展 transport。
- skills 不启用 inline shell expansion，会牺牲部分高级技能能力，但降低 v1 的安全和依赖复杂度。
- compression 的 token 估算如果不用 provider tokenizer，只能近似；适合 v1，但不保证精确 token budgeting。

---

## Deferred

- v1 CLI 命令和 `pyproject.toml` script。
- v1 tests 目录与完整 pytest 覆盖。
- SQLite / JSONL session persistence。
- 多 provider transport 和 fallback。
- 完整 MCP 客户端与 external tool protocol。
- 完整多后端执行环境：Docker、SSH、Modal、Daytona、Vercel Sandbox。
- 完整共享 git checkpoint store 与 rollback UI。
- 多凭证池、OAuth refresh、provider credential failover。
- LSP diagnostics / edit feedback loop。
- Gateway / platform adapters。
- Cron/scheduled tasks。
- Memory / session search。
- Web、browser、computer-use、kanban、send_message 等非核心工具集。
- ACP edit approval 与完整安全审批链。
