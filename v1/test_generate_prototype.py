from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from v1 import Agent, AgentConfig


V1_ROOT = Path(__file__).resolve().parent
REQUIREMENT_FILE = V1_ROOT / "需求结构化.md"
STAGE1_OUTPUTS = [
    Path("需求结构化.md"),
]
STAGE2_OUTPUTS = [
    Path("系统全局功能描述与设计.md"),
    Path("系统的功能点设计.md"),
    Path("页面详细设计"),
    Path("第二阶段设计检查报告.md"),
]
STAGE3_OUTPUTS = [
    Path("prototype") / "index.html",
    Path("prototype") / "README.md",
    Path("prototype") / "assets" / "css" / "styles.css",
    Path("prototype") / "assets" / "js" / "app.js",
    Path("prototype") / "assets" / "js" / "mock-data.js",
    Path("generation-report.md"),
    Path("validation-report.md"),
]
PLANNED_ROUTE_PATTERN = re.compile(r"^/[^\s|]*$")
GENERATED_ROUTE_FILE_PATTERN = re.compile(r"^(?:pages/)?[^\s|]+\.html$")


def main() -> int:
    args = parse_args()
    run_root = resolve_task_dir(args.stage, args.run_dir)
    log_step(f"starting {args.stage}")
    log_step(f"workspace: {V1_ROOT}")
    log_step(f"task dir: {run_root.relative_to(V1_ROOT)}")

    log_step("loading environment")
    load_dotenv()
    if args.env_path:
        env_path = Path(args.env_path)
        if env_path.is_file():
            load_dotenv(env_path, override=True)
            log_step(f"loaded env file: {env_path}")
        elif (env_path / ".env").is_file():
            load_dotenv(env_path / ".env", override=True)
            log_step(f"loaded env file: {env_path / '.env'}")
        else:
            log_step(f"env path not found, continuing without override: {env_path}")

    log_step(f"checking requirement file: {REQUIREMENT_FILE.relative_to(V1_ROOT)}")
    if not REQUIREMENT_FILE.exists():
        raise FileNotFoundError(REQUIREMENT_FILE)

    log_step("checking model credentials")
    has_api_key = any(os.getenv(name) for name in ("OPENAI_API_KEY", "HERMES_V1_API_KEY"))
    if not has_api_key:
        print("Missing model API key. Export OPENAI_API_KEY or HERMES_V1_API_KEY before running.", file=sys.stderr)
        return 2

    log_step("building agent config")
    config = AgentConfig.from_env(workspace_root=run_root)
    config.skills_dirs = [V1_ROOT / "skills"]
    config.max_iterations = int(os.getenv("HERMES_V1_MAX_ITERATIONS", "80"))
    log_step(f"model={config.model.model}, max_iterations={config.max_iterations}")

    if args.stage == "stage2":
        exit_code = run_stage2(config, run_root)
        log_step(f"finished {args.stage} with exit_code={exit_code}")
        return exit_code

    log_step("building stage prompt and checking prerequisites")
    prompt, required_outputs = build_stage_prompt(args.stage, run_root)
    result = run_agent_prompt(config, prompt, run_root)

    print("\n--- final response ---")
    print(result.final_response)
    log_step(f"checking generated outputs under {run_root.relative_to(V1_ROOT)}")
    exit_code = check_outputs(args.stage, required_outputs, result.iterations, result.compressed, run_root)
    log_step(f"finished {args.stage} with exit_code={exit_code}")
    return exit_code


def run_stage2(config: AgentConfig, run_root: Path) -> int:
    copy_inputs(STAGE1_OUTPUTS, run_root)
    ensure_inputs(STAGE1_OUTPUTS, "stage2", run_root)
    total_iterations = 0
    compressed = False
    final_response = ""

    while True:
        prompt, required_outputs = build_stage2_step_prompt(run_root)
        if prompt is None:
            break
        result = run_agent_prompt(config, prompt, run_root)
        total_iterations += result.iterations
        compressed = compressed or result.compressed
        final_response = result.final_response
        print("\n--- stage2 step response ---")
        print(result.final_response)
        missing = [path.as_posix() for path in required_outputs if not (run_root / path).exists()]
        if missing:
            print("stage2 step missing outputs:")
            for path in missing:
                print(f"- {path}")
            return 1

    log_step(f"checking generated outputs under {run_root.relative_to(V1_ROOT)}")
    if final_response:
        print("\n--- final response ---")
        print(final_response)
    return check_outputs("stage2", STAGE2_OUTPUTS, total_iterations, compressed, run_root)


def run_agent_prompt(config: AgentConfig, prompt: str, output_root: Path):
    log_step(f"current output root: {output_root.relative_to(V1_ROOT)}")
    log_step("running agent")
    stop_monitor = threading.Event()
    monitor_thread = threading.Thread(target=monitor_outputs, args=(output_root, stop_monitor), daemon=True)
    monitor_thread.start()
    agent = Agent(config)
    install_agent_logging(agent)
    try:
        result = agent.run(prompt)
    finally:
        stop_monitor.set()
        monitor_thread.join(timeout=1)
    log_step(f"agent finished: iterations={result.iterations}, compressed={result.compressed}")
    return result


def log_step(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def resolve_task_dir(stage: str, run_dir: str | None) -> Path:
    if run_dir:
        task_dir = Path(run_dir)
        if not task_dir.is_absolute():
            task_dir = V1_ROOT / task_dir
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir.resolve()
    if stage == "stage1":
        return create_task_dir("full")
    return latest_run_with_prerequisites(stage)


def create_task_dir(label: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    runs_dir = V1_ROOT / "runs"
    for suffix in [""] + [f"-{index}" for index in range(1, 100)]:
        task_dir = runs_dir / f"{timestamp}-{label}{suffix}"
        try:
            task_dir.mkdir(parents=True, exist_ok=False)
            return task_dir
        except FileExistsError:
            continue
    raise FileExistsError(f"unable to create unique task dir under {runs_dir}")


def latest_run_with_prerequisites(stage: str) -> Path:
    required = STAGE1_OUTPUTS if stage == "stage2" else STAGE2_OUTPUTS
    runs_dir = V1_ROOT / "runs"
    candidates = sorted([path for path in runs_dir.glob("*") if path.is_dir()], reverse=True)
    for candidate in candidates:
        if all((candidate / path).exists() for path in required):
            log_step(f"reusing latest task dir with prerequisites: {candidate.relative_to(V1_ROOT)}")
            return candidate
    if all((V1_ROOT / path).exists() for path in required):
        task_dir = create_task_dir("full")
        log_step(f"no existing task dir has {stage} prerequisites; created {task_dir.relative_to(V1_ROOT)} from root outputs")
        copy_inputs(required, task_dir)
        return task_dir
    missing = [path.as_posix() for path in required if not (V1_ROOT / path).exists()]
    raise FileNotFoundError(f"no task dir or root outputs contain {stage} prerequisites: {', '.join(missing)}")


def install_agent_logging(agent: Agent) -> None:
    original_complete = agent.model.complete
    original_dispatch = agent.registry.dispatch
    state = {"iteration": 0}

    def complete_with_log(messages, tools):
        state["iteration"] += 1
        request_no = state["iteration"]
        log_step(f"model request #{request_no} started: messages={len(messages)}, tools={len(tools)}")
        print(f"\n--- model stream #{request_no} ---", flush=True)

        last_delta = {"time": time.monotonic()}

        def on_delta(text: str) -> None:
            last_delta["time"] = time.monotonic()
            print(text, end="", flush=True)

        heartbeat_stop = threading.Event()
        heartbeat = threading.Thread(target=model_request_heartbeat, args=(request_no, last_delta, heartbeat_stop), daemon=True)
        heartbeat.start()

        try:
            response = original_complete(messages, tools, on_delta=on_delta)
        finally:
            heartbeat_stop.set()
            heartbeat.join(timeout=1)
        print(f"\n--- end model stream #{request_no} ---", flush=True)
        log_step(f"model request #{request_no} finished: tool_calls={len(response.tool_calls)}")
        return response

    def dispatch_with_log(name, args, context):
        if name == "write_file":
            path = args.get("path", "")
            content = str(args.get("content", ""))
            log_step(f"tool write_file started: {path} ({len(content)} chars)")
            result = original_dispatch(name, args, context)
            log_step(f"tool write_file finished: {path}")
            return result
        if name in {"read_file", "search_text", "skills", "bash", "todo", "delegate"}:
            log_step(f"tool {name} started")
            result = original_dispatch(name, args, context)
            log_step(f"tool {name} finished")
            return result
        return original_dispatch(name, args, context)

    agent.model.complete = complete_with_log
    agent.registry.dispatch = dispatch_with_log


def model_request_heartbeat(request_no: int, last_delta: dict[str, float], stop_event: threading.Event) -> None:
    while not stop_event.wait(10):
        idle_seconds = int(time.monotonic() - last_delta["time"])
        log_step(f"model request #{request_no} still running; no stream delta for {idle_seconds}s")


def monitor_outputs(root: Path, stop_event: threading.Event) -> None:
    previous = output_snapshot(root)
    for path, size in sorted(previous.items()):
        log_step(f"output existing: {path} ({size} bytes)")
    while not stop_event.wait(5):
        current = output_snapshot(root)
        for path, size in sorted(current.items()):
            old_size = previous.get(path)
            if old_size is None:
                log_step(f"output created: {path} ({size} bytes)")
            elif old_size != size:
                log_step(f"output updated: {path} ({old_size} -> {size} bytes)")
        previous = current


def output_snapshot(root: Path) -> dict[str, int]:
    snapshot: dict[str, int] = {}
    for path in root.rglob("*"):
        if path.is_file() and ".v1-checkpoints" not in path.parts:
            snapshot[path.relative_to(root).as_posix()] = path.stat().st_size
    return snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Hermes v1 prototype generation one stage at a time.")
    parser.add_argument("stage", choices=("stage1", "stage2", "stage3"), help="Stage to run in this invocation.")
    parser.add_argument("env_path", nargs="?", help="Optional .env file or directory containing .env.")
    parser.add_argument("--run-dir", help="Existing or new task directory to use for this stage.")
    return parser.parse_args()


def build_stage_prompt(stage: str, run_root: Path) -> tuple[str, list[Path]]:
    log_step("reading requirement input")
    requirement = REQUIREMENT_FILE.read_text(encoding="utf-8")
    log_step(f"requirement input loaded: {len(requirement)} chars")
    if stage == "stage1":
        log_step("prepared stage1 prompt")
        return (
            "请使用 skills 工具加载 requirement-intake-structuring。\n"
            "本次只运行第一阶段：需求录入与结构化，不要进入系统设计或原型生成。\n"
            "输入需求内容已包含在本提示中，请检查、整理并将结构化结果写入当前任务目录根部的 需求结构化.md。\n"
            "输出必须覆盖输入理解摘要、项目基础信息、场景与诉求分析、功能需求、风险点与待确认需求。\n"
            "所有产物只能写在当前 v1 工作目录内。\n\n"
            f"需求内容：\n{requirement}",
            STAGE1_OUTPUTS,
        )
    if stage == "stage2":
        log_step("copying stage1 prerequisites into task dir")
        copy_inputs(STAGE1_OUTPUTS, run_root)
        log_step("checking stage2 prerequisites")
        ensure_inputs(STAGE1_OUTPUTS, "stage2", run_root)
        prompt, required_outputs = build_stage2_step_prompt(run_root)
        if prompt is None:
            log_step("stage2 outputs already complete")
            return ("第二阶段产物已完整，无需重新生成。", STAGE2_OUTPUTS)
        return prompt, required_outputs
    log_step("copying stage2 prerequisites into task dir")
    copy_inputs(STAGE2_OUTPUTS, run_root)
    log_step("checking stage3 prerequisites")
    ensure_inputs(STAGE2_OUTPUTS, "stage3", run_root)
    log_step("prepared stage3 prompt")
    return (
        "请使用 skills 工具加载 prototype-generator。\n"
        "本次只运行第三阶段：原型生成，不要重做第一阶段或第二阶段。\n"
        "输入是 系统全局功能描述与设计.md、系统的功能点设计.md、页面详细设计/、第二阶段设计检查报告.md。\n"
        "如果存在 skills/prototype-generator/prototype-guide.md，请读取并继承其规则。\n"
        "必须生成项目级多页面静态原型：prototype/index.html、prototype/pages/*.html、公共 CSS、公共 JS、mock 数据、generation-report.md、validation-report.md。\n"
        "必须按 系统的功能点设计.md 的页面任务拆分清单逐页生成独立 HTML；不得用核心页面覆盖、Toast、按钮或合并卡片替代编辑页、确认页、处理页和子流程页。\n"
        "generation-report.md 和 validation-report.md 必须基于第二阶段规划页数统计页面覆盖率，列出规划页数、生成页数、缺失页清单；如果存在缺失页面，验收结论必须是不通过。\n"
        "不允许只生成单个大 HTML，静态链接必须可用。\n"
        "所有产物只能写在当前 v1 工作目录内。",
        STAGE3_OUTPUTS,
    )


def build_stage2_step_prompt(run_root: Path) -> tuple[str, list[Path]] | tuple[None, list[Path]]:
    if not (run_root / "系统全局功能描述与设计.md").exists():
        log_step("prepared stage2 step prompt for 系统全局功能描述与设计.md")
        return (
            "请使用 skills 工具加载 system-function-design-planning。\n"
            "本次是第二阶段分步执行的第 1 步：只生成 系统全局功能描述与设计.md。\n"
            "请读取当前任务目录根部的 需求结构化.md，输出系统全局功能描述、角色权限、全局业务流程、信息架构、核心数据对象和业务规则。\n"
            "本轮不要生成 系统的功能点设计.md、页面详细设计/、第二阶段设计检查报告.md，也不要生成 prototype 目录或 HTML 原型。\n"
            "所有产物只能写在当前任务目录内。",
            [Path("系统全局功能描述与设计.md")],
        )
    if not (run_root / "系统的功能点设计.md").exists():
        log_step("prepared stage2 step prompt for 系统的功能点设计.md")
        return (
            "请使用 skills 工具加载 system-function-design-planning。\n"
            "本次是第二阶段分步执行的第 2 步：只生成 系统的功能点设计.md。\n"
            "请读取当前任务目录根部的 需求结构化.md 和 系统全局功能描述与设计.md。\n"
            "输出必须包含功能点清单、功能树/模块树、菜单与路由规划、页面任务拆分清单，并能支撑下一步生成页面详细设计。\n"
            "本轮不要生成 页面详细设计/、第二阶段设计检查报告.md，也不要重写 系统全局功能描述与设计.md。\n"
            "所有产物只能写在当前任务目录内。",
            [Path("系统的功能点设计.md")],
        )
    if not (run_root / "页面详细设计").exists():
        log_step("prepared stage2 step prompt for 页面详细设计/")
        return (
            "请使用 skills 工具加载 system-function-design-planning。\n"
            "本次是第二阶段分步执行的第 3 步：只生成 页面详细设计/ 目录。\n"
            "请读取当前任务目录根部的 需求结构化.md、系统全局功能描述与设计.md、系统的功能点设计.md。\n"
            "必须按照 系统的功能点设计.md 中的页面任务拆分清单，为每个页面任务生成独立的页面详细设计 Markdown 文件。\n"
            "本轮不要生成 第二阶段设计检查报告.md，不要重写已有全局设计和功能点设计，也不要生成 prototype 目录或 HTML 原型。\n"
            "所有产物只能写在当前任务目录内。",
            [Path("页面详细设计")],
        )
    if not (run_root / "第二阶段设计检查报告.md").exists():
        log_step("prepared stage2 step prompt for 第二阶段设计检查报告.md")
        return (
            "请使用 skills 工具加载 system-function-design-planning。\n"
            "本次是第二阶段分步执行的第 4 步：只生成 第二阶段设计检查报告.md。\n"
            "请读取当前任务目录根部的 需求结构化.md、系统全局功能描述与设计.md、系统的功能点设计.md 和 页面详细设计/。\n"
            "检查第二阶段产物完整性，重点核对页面任务拆分清单中的每个页面是否都有独立页面详细设计文件；列出规划页数、详细设计文件数和缺失清单。\n"
            "本轮不要重写已有设计产物，也不要生成 prototype 目录或 HTML 原型。\n"
            "所有产物只能写在当前任务目录内。",
            [Path("第二阶段设计检查报告.md")],
        )
    return None, STAGE2_OUTPUTS


def copy_inputs(paths: list[Path], run_root: Path) -> None:
    for relative_path in paths:
        source = V1_ROOT / relative_path
        destination = run_root / relative_path
        if destination.exists() or not source.exists():
            continue
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        log_step(f"copied prerequisite: {relative_path.as_posix()}")


def ensure_inputs(paths: list[Path], stage: str, root: Path) -> None:
    log_step(f"validating {stage} prerequisites: {len(paths)} paths")
    missing = [path.as_posix() for path in paths if not (root / path).exists()]
    if missing:
        log_step(f"{stage} prerequisite check failed: {len(missing)} missing")
        raise FileNotFoundError(f"{stage} missing prerequisite outputs: {', '.join(missing)}")
    log_step(f"{stage} prerequisites ready")


def check_outputs(stage: str, required_outputs: list[Path], iterations: int, compressed: bool, output_root: Path | None = None) -> int:
    output_root = output_root or V1_ROOT
    log_step(f"checking required output files under {output_root.relative_to(V1_ROOT)}")
    missing_outputs = [path.as_posix() for path in required_outputs if not (output_root / path).exists()]
    pages_dir = output_root / "prototype" / "pages"
    page_count = len(list(pages_dir.glob("*.html"))) if pages_dir.exists() else 0
    if stage == "stage3":
        log_step("parsing planned routes from stage2 design")
    planned_routes = parse_planned_routes(output_root) if stage == "stage3" else []
    if stage == "stage3":
        log_step("parsing generated route mappings from reports")
    generated_route_files = parse_generated_route_files(output_root) if stage == "stage3" else {}
    mapped_planned_files = [generated_route_files[route] for route in planned_routes if route in generated_route_files]
    duplicate_route_files = duplicate_paths(mapped_planned_files)
    missing_routes = [route for route in planned_routes if route not in generated_route_files]
    missing_route_files = [path for path in generated_route_files.values() if not path.exists()]

    print("\n--- generation check ---")
    print(f"stage: {stage}")
    print(f"iterations: {iterations}")
    print(f"compressed: {compressed}")
    if stage == "stage3":
        print(f"prototype pages: {page_count}")
        print(f"planned routes: {len(planned_routes)}")
        print(f"mapped routes: {len(generated_route_files)}")
    if missing_outputs:
        print("missing outputs:")
        for path in missing_outputs:
            print(f"- {path}")
        return 1
    if stage == "stage3" and missing_routes:
        print("missing planned route mappings:")
        for route in missing_routes:
            print(f"- {route}")
        return 1
    if stage == "stage3" and missing_route_files:
        print("missing mapped prototype files:")
        for path in missing_route_files:
            print(f"- {path.relative_to(output_root).as_posix()}")
        return 1
    if stage == "stage3" and duplicate_route_files:
        print("planned routes must map to standalone prototype files:")
        for path in duplicate_route_files:
            print(f"- {path.relative_to(output_root).as_posix()}")
        return 1
    print("all required outputs exist")
    return 0


def duplicate_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    duplicates: list[Path] = []
    for path in paths:
        if path in seen and path not in duplicates:
            duplicates.append(path)
        seen.add(path)
    return duplicates


def parse_planned_routes(output_root: Path) -> list[str]:
    design_file = V1_ROOT / "系统的功能点设计.md"
    if not design_file.exists():
        design_file = output_root / "系统的功能点设计.md"
    if not design_file.exists():
        design_file = output_root / "source" / "系统的功能点设计.md"
    if not design_file.exists():
        design_file = V1_ROOT / "source" / "系统的功能点设计.md"
    if not design_file.exists():
        log_step("planned route source not found")
        return []

    log_step(f"planned route source: {design_file.relative_to(V1_ROOT)}")
    content = design_file.read_text(encoding="utf-8")
    route_by_page = parse_route_table(content)
    task_page_names = parse_page_task_names(content)
    if not task_page_names:
        log_step(f"parsed planned routes without task filter: {len(route_by_page)}")
        return list(route_by_page.values())

    routes = [route_by_page[name] for name in task_page_names if name in route_by_page]
    log_step(f"parsed task pages: {len(task_page_names)}, planned routes: {len(routes)}")
    return routes


def parse_route_table(content: str) -> dict[str, str]:
    routes: dict[str, str] = {}
    in_route_table = False
    for line in content.splitlines():
        if line.startswith("## 6. 菜单与路由规划"):
            in_route_table = True
            continue
        if in_route_table and line.startswith("## "):
            break
        if not in_route_table or not line.startswith("|") or line.startswith("| :"):
            continue
        cells = split_markdown_row(line)
        if len(cells) < 4 or cells[2] == "页面名称":
            continue
        page_name = cells[2].strip()
        route = cells[3].strip()
        if page_name and PLANNED_ROUTE_PATTERN.match(route):
            routes[page_name] = route
    return routes


def parse_page_task_names(content: str) -> list[str]:
    names: list[str] = []
    in_task_table = False
    for line in content.splitlines():
        if line.startswith("## 7. 页面任务拆分清单"):
            in_task_table = True
            continue
        if in_task_table and line.startswith("## "):
            break
        if not in_task_table or not line.startswith("|") or line.startswith("| :"):
            continue
        cells = split_markdown_row(line)
        if len(cells) < 2 or cells[1] == "页面名称":
            continue
        if re.fullmatch(r"T\d+", cells[0]):
            names.append(cells[1].strip())
    return names


def parse_generated_route_files(output_root: Path) -> dict[str, Path]:
    reports = [output_root / "generation-report.md", output_root / "prototype" / "README.md"]
    route_files: dict[str, Path] = {}
    for report in reports:
        if not report.exists():
            log_step(f"route mapping report missing: {report.relative_to(V1_ROOT)}")
            continue
        before = len(route_files)
        for line in report.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|") or line.startswith("| :"):
                continue
            cells = split_markdown_row(line)
            for index, cell in enumerate(cells):
                route = cell.strip()
                if not PLANNED_ROUTE_PATTERN.match(route):
                    continue
                file_path = first_generated_file(cells[index + 1:], output_root)
                if file_path is not None:
                    route_files[route] = file_path
        log_step(f"parsed {len(route_files) - before} route mappings from {report.relative_to(V1_ROOT)}")
    return route_files


def first_generated_file(cells: list[str], output_root: Path) -> Path | None:
    for cell in cells:
        value = cell.strip().strip("`")
        if GENERATED_ROUTE_FILE_PATTERN.match(value):
            return output_root / "prototype" / value
    return None


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


if __name__ == "__main__":
    raise SystemExit(main())
