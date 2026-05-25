from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from v1 import Agent, AgentConfig


V1_ROOT = Path(__file__).resolve().parent
REQUIREMENT_FILE = V1_ROOT / "需求结构化.md"
STAGE1_OUTPUTS = [
    V1_ROOT / "需求结构化.md",
]
STAGE2_OUTPUTS = [
    V1_ROOT / "系统全局功能描述与设计.md",
    V1_ROOT / "系统的功能点设计.md",
    V1_ROOT / "页面详细设计",
    V1_ROOT / "第二阶段设计检查报告.md",
]
STAGE3_OUTPUTS = [
    V1_ROOT / "prototype" / "index.html",
    V1_ROOT / "prototype" / "README.md",
    V1_ROOT / "prototype" / "assets" / "css" / "styles.css",
    V1_ROOT / "prototype" / "assets" / "js" / "app.js",
    V1_ROOT / "prototype" / "assets" / "js" / "mock-data.js",
    V1_ROOT / "generation-report.md",
    V1_ROOT / "validation-report.md",
]
PLANNED_ROUTE_PATTERN = re.compile(r"^/[^\s|]*$")
GENERATED_ROUTE_FILE_PATTERN = re.compile(r"^(?:pages/)?[^\s|]+\.html$")


def main() -> int:
    args = parse_args()
    load_dotenv()
    if args.env_path:
        env_path = Path(args.env_path)
        if env_path.is_file():
            load_dotenv(env_path, override=True)
        elif (env_path / ".env").is_file():
            load_dotenv(env_path / ".env", override=True)

    if not REQUIREMENT_FILE.exists():
        raise FileNotFoundError(REQUIREMENT_FILE)

    has_api_key = any(os.getenv(name) for name in ("OPENAI_API_KEY", "HERMES_V1_API_KEY"))
    if not has_api_key:
        print("Missing model API key. Export OPENAI_API_KEY or HERMES_V1_API_KEY before running.", file=sys.stderr)
        return 2

    config = AgentConfig.from_env(workspace_root=V1_ROOT)
    config.skills_dirs = [V1_ROOT / "skills"]
    config.max_iterations = int(os.getenv("HERMES_V1_MAX_ITERATIONS", "80"))

    agent = Agent(config)
    prompt, required_outputs = build_stage_prompt(args.stage)
    result = agent.run(prompt)

    print(result.final_response)
    return check_outputs(args.stage, required_outputs, result.iterations, result.compressed)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Hermes v1 prototype generation one stage at a time.")
    parser.add_argument("stage", choices=("stage1", "stage2", "stage3"), help="Stage to run in this invocation.")
    parser.add_argument("env_path", nargs="?", help="Optional .env file or directory containing .env.")
    return parser.parse_args()


def build_stage_prompt(stage: str) -> tuple[str, list[Path]]:
    requirement = REQUIREMENT_FILE.read_text(encoding="utf-8")
    if stage == "stage1":
        return (
            "请使用 skills 工具加载 requirement-intake-structuring。\n"
            "本次只运行第一阶段：需求录入与结构化，不要进入系统设计或原型生成。\n"
            "输入需求文件是 source/需求结构化.md，请检查、整理并将结构化结果写入工作目录根部的 需求结构化.md。\n"
            "输出必须覆盖输入理解摘要、项目基础信息、场景与诉求分析、功能需求、风险点与待确认需求。\n"
            "所有产物只能写在当前 v1 工作目录内。\n\n"
            f"需求内容：\n{requirement}",
            STAGE1_OUTPUTS,
        )
    if stage == "stage2":
        ensure_inputs(STAGE1_OUTPUTS, "stage2")
        return (
            "请使用 skills 工具加载 system-function-design-planning。\n"
            "本次只运行第二阶段：系统功能设计与页面规划，不要生成 prototype 目录或 HTML 原型。\n"
            "输入是工作目录根部的 需求结构化.md，同时可参考 source/需求结构化.md。\n"
            "必须生成 系统全局功能描述与设计.md、系统的功能点设计.md、页面详细设计/、第二阶段设计检查报告.md。\n"
            "页面详细设计目录下必须有业务页面详细设计文件。\n"
            "所有产物只能写在当前 v1 工作目录内。",
            STAGE2_OUTPUTS,
        )
    ensure_inputs(STAGE2_OUTPUTS, "stage3")
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


def ensure_inputs(paths: list[Path], stage: str) -> None:
    missing = [path.relative_to(V1_ROOT).as_posix() for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"{stage} missing prerequisite outputs: {', '.join(missing)}")


def check_outputs(stage: str, required_outputs: list[Path], iterations: int, compressed: bool) -> int:
    missing_outputs = [path.relative_to(V1_ROOT).as_posix() for path in required_outputs if not path.exists()]
    pages_dir = V1_ROOT / "prototype" / "pages"
    page_count = len(list(pages_dir.glob("*.html"))) if pages_dir.exists() else 0
    planned_routes = parse_planned_routes() if stage == "stage3" else []
    generated_route_files = parse_generated_route_files() if stage == "stage3" else {}
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
            print(f"- {path.relative_to(V1_ROOT).as_posix()}")
        return 1
    if stage == "stage3" and duplicate_route_files:
        print("planned routes must map to standalone prototype files:")
        for path in duplicate_route_files:
            print(f"- {path.relative_to(V1_ROOT).as_posix()}")
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


def parse_planned_routes() -> list[str]:
    design_file = V1_ROOT / "系统的功能点设计.md"
    if not design_file.exists():
        design_file = V1_ROOT / "source" / "系统的功能点设计.md"
    if not design_file.exists():
        return []

    content = design_file.read_text(encoding="utf-8")
    route_by_page = parse_route_table(content)
    task_page_names = parse_page_task_names(content)
    if not task_page_names:
        return list(route_by_page.values())

    return [route_by_page[name] for name in task_page_names if name in route_by_page]


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


def parse_generated_route_files() -> dict[str, Path]:
    reports = [V1_ROOT / "generation-report.md", V1_ROOT / "prototype" / "README.md"]
    route_files: dict[str, Path] = {}
    for report in reports:
        if not report.exists():
            continue
        for line in report.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|") or line.startswith("| :"):
                continue
            cells = split_markdown_row(line)
            for index, cell in enumerate(cells):
                route = cell.strip()
                if not PLANNED_ROUTE_PATTERN.match(route):
                    continue
                file_path = first_generated_file(cells[index + 1:])
                if file_path is not None:
                    route_files[route] = file_path
    return route_files


def first_generated_file(cells: list[str]) -> Path | None:
    for cell in cells:
        value = cell.strip().strip("`")
        if GENERATED_ROUTE_FILE_PATTERN.match(value):
            return V1_ROOT / "prototype" / value
    return None


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


if __name__ == "__main__":
    raise SystemExit(main())
