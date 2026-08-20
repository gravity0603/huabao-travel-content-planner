#!/usr/bin/env python3
"""Deterministic regression tests for validate_candidate_output.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_candidate_output.py")

VALID = """### 选题 1：戈壁藏蓝瞳（5字）
- 状态：主推
- 当前关联：常青素材；盐泉地貌解释
- 副标题：荒漠盐泉呈现天然蓝洞
- 落地页：解释盐泉颜色与地貌形成机制
- 信息源：[已验证] [国家地理机构·荒漠盐泉地貌说明](https://science.example.cn/salt-spring)
- 概念指纹与去重结论：荒漠盐泉 | 蓝色泉眼 | 盐泉成因 | 画面反差；三方未重复
- P 潜力：8/10；月报潜力：8/10
- 审核风险：无
"""

CASES = [
    ("valid", VALID, True),
    ("half-width-question", VALID.replace("戈壁藏蓝瞳", "海里有瀑布?").replace("（5字）", "（7字）"), False),
    ("missing-field", VALID.replace("- 落地页：解释盐泉颜色与地貌形成机制\n", ""), False),
    ("empty-subtitle", VALID.replace("- 副标题：荒漠盐泉呈现天然蓝洞", "- 副标题："), False),
    ("bad-status", VALID.replace("- 状态：主推", "- 状态：已上线"), False),
    ("score-out-of-range", VALID.replace("P 潜力：8/10", "P 潜力：99/10"), False),
    ("placeholder-source", VALID.replace("https://science.example.cn/salt-spring", "https://example.org/a"), False),
    ("missing-question-mark", VALID.replace("戈壁藏蓝瞳", "景区硬币去哪").replace("（5字）", "（6字）"), False),
    ("bad-main-threshold", VALID.replace("P 潜力：8/10", "P 潜力：6/10"), False),
]


def run_case(name: str, content: str, should_pass: bool) -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / f"{name}.md"
        path.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True
        )
        passed = result.returncode == 0
        if passed != should_pass:
            raise AssertionError(
                f"{name}: expected pass={should_pass}, got {passed}\n{result.stdout}{result.stderr}"
            )


def main() -> int:
    for name, content, should_pass in CASES:
        run_case(name, content, should_pass)
    print(f"PASSED: {len(CASES)} validator regression cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
