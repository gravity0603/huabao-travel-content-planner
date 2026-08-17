#!/usr/bin/env python3
"""Validate hard output rules for huabao travel candidate Markdown."""

from __future__ import annotations

import re
import sys
from pathlib import Path

CANDIDATE_RE = re.compile(r"^###\s*选题\s*\d+\s*[：:]\s*(.+?)（(\d+)字）\s*$", re.MULTILINE)
SOURCE_RE = re.compile(r"^\[已验证\]\s+\[[^\]]+·[^\]]+\]\(https://[^)\s]+\)$")
SUBTITLE_PREFIX = "- 副标题："
SOURCE_PREFIX = "- 信息源："
P_PREFIX = "- P 潜力："
MONTH_PREFIX = "- 月报潜力："
STATUS_PREFIX = "- 状态："


def count_chars(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def score_from_line(line: str) -> int | None:
    match = re.search(r"(\d+)\s*/\s*10", line)
    return int(match.group(1)) if match else None


def validate_block(title: str, declared: int, block: str, index: int) -> list[str]:
    errors: list[str] = []
    actual = count_chars(title)
    if actual != declared:
        errors.append(f"选题 {index}：标题声明 {declared} 字，实际 {actual} 字。")
    if actual > 7:
        errors.append(f"选题 {index}：旅行标题超过 7 字（实际 {actual} 字）。")
    if any(token in title for token in ("吗", "么", "呢", "为何", "如何")) and not title.endswith("？"):
        errors.append(f"选题 {index}：疑问式标题缺少中文问号。")

    lines = [line.strip() for line in block.splitlines() if line.strip()]
    subtitle = next((line[len(SUBTITLE_PREFIX):] for line in lines if line.startswith(SUBTITLE_PREFIX)), None)
    if subtitle is None:
        errors.append(f"选题 {index}：缺少副标题。")
    elif count_chars(subtitle) > 25:
        errors.append(f"选题 {index}：副标题超过 25 字（实际 {count_chars(subtitle)} 字）。")

    source = next((line[len(SOURCE_PREFIX):] for line in lines if line.startswith(SOURCE_PREFIX)), None)
    if source is None:
        errors.append(f"选题 {index}：缺少信息源。")
    elif not SOURCE_RE.fullmatch(source):
        errors.append(f"选题 {index}：信息源必须是 [已验证] [来源名·文章标题](https://...)。")

    status = next((line[len(STATUS_PREFIX):] for line in lines if line.startswith(STATUS_PREFIX)), "")
    p_score = score_from_line(next((line for line in lines if line.startswith(P_PREFIX)), ""))
    month_score = score_from_line(next((line for line in lines if line.startswith(MONTH_PREFIX)), ""))
    if not status:
        errors.append(f"选题 {index}：缺少状态。")
    if p_score is None or month_score is None:
        errors.append(f"选题 {index}：缺少 P 潜力或月报潜力评分。")
    elif status == "主推" and not (p_score >= 7 and month_score >= 8):
        errors.append(f"选题 {index}：主推必须同时满足 P≥7、月报≥8。")
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
    for index, match in enumerate(matches, start=1):
        block_end = matches[index].start() if index < len(matches) else len(text)
        errors.extend(validate_block(match.group(1), int(match.group(2)), text[match.end():block_end], index))

    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASSED: {len(matches)} candidate(s) satisfy checked hard rules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
