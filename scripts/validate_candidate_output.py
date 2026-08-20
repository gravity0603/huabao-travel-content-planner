#!/usr/bin/env python3
"""Validate mechanically checkable rules for final Huabao travel candidates."""

from __future__ import annotations

import re
import sys
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
    "context": "- 当前关联：",
    "subtitle": "- 副标题：",
    "landing": "- 落地页：",
    "source": "- 信息源：",
    "dedup": "- 概念指纹与去重结论：",
    "scores": "- P 潜力：",
    "risk": "- 审核风险：",
}
ALLOWED_STATUS = {"主推", "备选"}
QUESTION_TOKENS = (
    "吗", "么", "呢", "为何", "如何", "是否", "谁", "哪里", "哪儿", "去哪",
    "怎么", "怎样", "多少", "几座", "几个", "几处", "几种", "何时", "何地",
)
PLACEHOLDER_HOSTS = {"example.com", "www.example.com", "example.org", "www.example.org"}


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
    host = (parsed.hostname or "").lower()
    return bool(host and host not in PLACEHOLDER_HOSTS and "." in host)


def parse_scores(block: str) -> tuple[int | None, int | None]:
    p_match = re.search(r"P\s*潜力：\s*(\d+)\s*/\s*10", block)
    month_match = re.search(r"月报潜力：\s*(\d+)\s*/\s*10", block)
    return (
        int(p_match.group(1)) if p_match else None,
        int(month_match.group(1)) if month_match else None,
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
        errors.append(f"选题 {number}：状态只能是“主推”或“备选”。")

    subtitle = values.get("subtitle")
    if subtitle is not None and count_chars(subtitle) > 25:
        errors.append(f"选题 {number}：副标题超过 25 字（实际 {count_chars(subtitle)} 字）。")

    source = values.get("source")
    if source is not None and not valid_source(source):
        errors.append(
            f"选题 {number}：信息源必须是已核验、非占位的 "
            "[已验证] [来源名·文章标题](https://...)。"
        )

    p_score, month_score = parse_scores(block)
    if p_score is None or month_score is None:
        errors.append(f"选题 {number}：缺少 P 潜力或月报潜力评分。")
    else:
        if not 0 <= p_score <= 10 or not 0 <= month_score <= 10:
            errors.append(f"选题 {number}：两项评分必须在 0–10 之间。")
        if status == "主推" and not (p_score >= 7 and month_score >= 8):
            errors.append(f"选题 {number}：主推必须同时满足 P≥7、月报≥8。")

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
