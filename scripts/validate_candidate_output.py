#!/usr/bin/env python3
"""Validate mechanically checkable rules for final Huabao travel candidates."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

CANDIDATE_RE = re.compile(
    r"^###\s*选题\s*(\d+)\s*[：:]\s*(.+?)（(\d+)字）\s*$", re.MULTILINE
)
SOURCE_RE = re.compile(
    r"^\[已验证\]\s+\[([^\]]+)·([^\]]+)\]\((https://[^)\s]+)\)$"
)
FIELDS = {
    "status": "- 状态：",
    "category": "- 品类：",
    "timeline": "- 素材范围 / 目标上线日 / 去重窗口：",
    "context": "- 当前关联：",
    "fact_certainty": "- 核心事实 / 确定性：",
    "visual": "- 首图证明 / 3种内页画面：",
    "hook_value": "- 主钩子 / 用户收益：",
    "style": "- 风格对标：",
    "subtitle": "- 副标题：",
    "landing": "- 落地页：",
    "source": "- 信息源：",
    "source_meta": "- 来源等级 / 日期：",
    "dedup": "- 去重回执：",
    "quality": "- 质量总分：",
    "scores": "- P 潜力：",
    "risk": "- 审核风险：",
}
ALLOWED_STATUS = {"主推", "可用"}
CERTAINTY_LEVELS = {"已确认", "研究推测", "理论假设", "个人解读"}
QUESTION_TOKENS = (
    "吗", "么", "呢", "为何", "如何", "是否", "谁", "哪里", "哪儿", "去哪",
    "怎么", "怎样", "多少", "几座", "几个", "几处", "几种", "何时", "何地",
)
PLACEHOLDER_BASE_HOSTS = {"example.com", "example.org", "example.net"}
SOURCE_LEVELS = {"官方", "权威媒体", "专业机构", "可靠二手"}
UNRESOLVED_RISK_TOKENS = {"未处理", "待处理", "待核", "不明", "存在风险"}
DATE_RE = r"\d{4}-\d{2}-\d{2}"


def count_chars(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def field_value(lines: list[str], prefix: str) -> str | None:
    matches = [line[len(prefix):].strip() for line in lines if line.startswith(prefix)]
    if len(matches) != 1:
        return None
    return matches[0]


def valid_source(value: str) -> bool:
    match = SOURCE_RE.fullmatch(value)
    if not match:
        return False
    source_name, article_title, url = match.groups()
    if not source_name.strip() or not article_title.strip() or "..." in url or "…" in url:
        return False
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host or "." not in host:
        return False
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith((".localhost", ".invalid", ".test")):
        return False
    if any(host == base or host.endswith(f".{base}") for base in PLACEHOLDER_BASE_HOSTS):
        return False
    return True


def parse_scores(block: str) -> tuple[int | None, int | None, int | None]:
    p_match = re.search(r"P\s*潜力：\s*(\d+)\s*/\s*10", block)
    month_match = re.search(r"月报潜力：\s*(\d+)\s*/\s*10", block)
    quality_match = re.search(r"质量总分：\s*(\d+)\s*/\s*100", block)
    return (
        int(p_match.group(1)) if p_match else None,
        int(month_match.group(1)) if month_match else None,
        int(quality_match.group(1)) if quality_match else None,
    )


def validate_block(number: int, title: str, declared: int, block: str) -> list[str]:
    errors: list[str] = []
    actual = count_chars(title)
    if actual != declared:
        errors.append(f"选题 {number}：标题声明 {declared} 字，实际 {actual} 字。")
    if actual > 7:
        errors.append(f"选题 {number}：旅行标题超过 7 字（实际 {actual} 字）。")
    if title.endswith("?"):
        errors.append(f"选题 {number}：疑问句必须使用中文问号，不可使用半角 ?。")
    elif any(token in title for token in QUESTION_TOKENS) and not title.endswith("？"):
        errors.append(f"选题 {number}：疑问式标题缺少中文问号。")

    lines = [line.strip() for line in block.splitlines() if line.strip()]
    values: dict[str, str] = {}
    for key, prefix in FIELDS.items():
        value = field_value(lines, prefix)
        label = prefix.removeprefix("- ").removesuffix("：")
        if value is None:
            errors.append(f"选题 {number}：字段“{label}”缺失或重复。")
        elif not value:
            errors.append(f"选题 {number}：字段“{label}”不能为空。")
        else:
            values[key] = value

    status = values.get("status")
    if status is not None and status not in ALLOWED_STATUS:
        errors.append(f"选题 {number}：正式候选状态只能是“主推”或“可用”。")

    category = values.get("category")
    if category is not None and category != "旅行风光":
        errors.append(f"选题 {number}：旅行专项正式候选的品类必须是“旅行风光”。")

    fact_certainty = values.get("fact_certainty")
    if fact_certainty is not None and not any(level in fact_certainty for level in CERTAINTY_LEVELS):
        errors.append(f"选题 {number}：核心事实必须标注允许的确定性等级。")

    visual = values.get("visual")
    if visual is not None:
        parts = re.split(r"[；;]", visual, maxsplit=1)
        body_views = re.split(r"[、，,]", parts[1]) if len(parts) == 2 else []
        if not parts[0].strip() or len([item for item in body_views if item.strip()]) < 3:
            errors.append(f"选题 {number}：必须写明首图证明与至少3种不同内页画面。")

    hook_value = values.get("hook_value")
    if hook_value is not None:
        parts = [item.strip() for item in re.split(r"[；;]", hook_value, maxsplit=1)]
        if len(parts) != 2 or not all(parts):
            errors.append(f"选题 {number}：主钩子与用户收益必须分别写明。")

    source_meta = values.get("source_meta")
    if source_meta is not None:
        source_level = re.split(r"[；;]", source_meta, maxsplit=1)[0].strip()
        if source_level not in SOURCE_LEVELS:
            errors.append(f"选题 {number}：来源等级必须是官方、权威媒体、专业机构或可靠二手。")
        if not re.search(DATE_RE, source_meta):
            errors.append(f"选题 {number}：来源等级与日期必须包含完整日期。")

    dedup = values.get("dedup")
    if dedup is not None:
        if not all(re.search(rf"(?:^|[；;])\s*{layer}\s*通过(?:\s|[；;]|$)", dedup) for layer in ("H", "R", "B")):
            errors.append(f"选题 {number}：正式候选的 H、R、B 必须全部明确为“通过”。")
        reported_window = re.search(rf"窗口[：:]?\s*({DATE_RE})\s*[–—~-]\s*({DATE_RE})", dedup)
        r_coverage = re.search(rf"R\s*数据覆盖[：:]?\s*({DATE_RE})\s*[–—~-]\s*({DATE_RE})", dedup)
        cutoff = re.search(rf"数据截止日[：:]?\s*({DATE_RE})", dedup)
        timeline = values.get("timeline", "")
        timeline_dates = re.findall(DATE_RE, timeline)
        if not reported_window or not r_coverage or not cutoff or len(timeline_dates) < 3:
            errors.append(f"选题 {number}：去重回执必须写明窗口、R数据覆盖起止与数据截止日。")
        else:
            target_day, window_start, window_end = map(date.fromisoformat, timeline_dates[:3])
            reported_start, reported_end = map(date.fromisoformat, reported_window.groups())
            coverage_start, coverage_end = map(date.fromisoformat, r_coverage.groups())
            cutoff_day = date.fromisoformat(cutoff.group(1))
            if (reported_start, reported_end) != (window_start, window_end):
                errors.append(f"选题 {number}：去重回执中的窗口必须与时间字段一致。")
            if coverage_start > window_start or coverage_end < cutoff_day:
                errors.append(f"选题 {number}：R数据未覆盖窗口起点或未达到数据截止日。")
            if window_end != target_day:
                errors.append(f"选题 {number}：去重窗口终点必须与目标上线日一致。")

    subtitle = values.get("subtitle")
    if subtitle is not None:
        if count_chars(subtitle) > 25:
            errors.append(f"选题 {number}：副标题超过 25 字（实际 {count_chars(subtitle)} 字）。")
        normalized_title = re.sub(r"[\s，。！？；：、,.!?;:\"'“”‘’]", "", title)
        normalized_subtitle = re.sub(r"[\s，。！？；：、,.!?;:\"'“”‘’]", "", subtitle)
        if normalized_title and normalized_title == normalized_subtitle:
            errors.append(f"选题 {number}：标题与副标题不得完全复述。")

    source = values.get("source")
    if source is not None and not valid_source(source):
        errors.append(
            f"选题 {number}：信息源必须是已核验、非占位的 "
            "[已验证] [来源名·文章标题](https://...)。"
        )

    p_score, month_score, quality_score = parse_scores(block)
    if p_score is None or month_score is None:
        errors.append(f"选题 {number}：缺少 P 潜力或月报潜力评分。")
    elif not 0 <= p_score <= 10 or not 0 <= month_score <= 10:
        errors.append(f"选题 {number}：两项业务评分必须在 0–10 之间。")

    if quality_score is None:
        errors.append(f"选题 {number}：缺少100分质量总分。")
    elif not 0 <= quality_score <= 100:
        errors.append(f"选题 {number}：质量总分必须在 0–100 之间。")

    if status == "主推" and not (
        p_score is not None
        and month_score is not None
        and quality_score is not None
        and p_score >= 7
        and month_score >= 8
        and quality_score >= 85
    ):
        errors.append(f"选题 {number}：主推必须同时满足质量总分≥85、P≥7、月报≥8。")
    if status == "可用" and (quality_score is None or quality_score < 75):
        errors.append(f"选题 {number}：可用候选的质量总分至少为75。")

    risk = values.get("risk")
    if risk is not None:
        if risk != "无" and "已处理" not in risk:
            errors.append(f"选题 {number}：正式候选的审核风险必须为“无”或明确写明“已处理”。")
        if any(token in risk for token in UNRESOLVED_RISK_TOKENS):
            errors.append(f"选题 {number}：仍有未处理风险，不得进入正式候选。")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python validate_candidate_output.py <candidate-output.md>")
        return 1
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    matches = list(CANDIDATE_RE.finditer(text))
    if not matches:
        print("ERROR: no candidate headings found. Expected: ### 选题 N：标题（X字）")
        return 1

    errors: list[str] = []
    numbers = [int(match.group(1)) for match in matches]
    expected = list(range(1, len(matches) + 1))
    if numbers != expected:
        errors.append(f"候选编号必须从 1 连续递增；当前为 {numbers}。")

    for index, match in enumerate(matches):
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        errors.extend(
            validate_block(
                int(match.group(1)), match.group(2), int(match.group(3)), text[match.end():block_end]
            )
        )

    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(
        f"PASSED: {len(matches)} candidate(s) satisfy mechanically checkable final-output rules. "
        "Source truth, copyright safety, and dedup completion still require substantive review."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
