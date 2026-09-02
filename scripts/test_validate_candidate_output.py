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
- 品类：旅行风光
- 素材范围 / 目标上线日 / 去重窗口：常青；2026-08-30；2026-07-31–2026-08-30
- 当前关联：常青素材；盐泉地貌解释
- 核心事实 / 确定性：盐泉因矿物与光线呈蓝色；已确认
- 首图证明 / 3种内页画面：蓝色盐泉俯拍；盐泉全景、矿物近景、地貌示意
- 主钩子 / 用户收益：视觉反常；地貌知识
- 风格对标：盐泉 | 画面翻译 | 拟物 | 成因兑现
- 副标题：荒漠盐泉呈现天然蓝洞
- 落地页：解释盐泉颜色与地貌形成机制
- 信息源：[已验证] [中国地质调查局·荒漠盐泉地貌说明](https://www.cgs.gov.cn/salt-spring)
- 来源等级 / 日期：专业机构；2026-08-20
- 去重回执：H 通过；R 通过；B 通过；窗口 2026-07-31–2026-08-30；R 数据覆盖 2026-07-01–2026-08-30；数据截止日 2026-08-30；H 最近数据 2026-08-30
- 质量总分：88/100；弱项：季节关联一般
- P 潜力：8/10；月报潜力：8/10
- 审核风险：无
"""

CASES = [
    ("valid", VALID, True),
    ("half-width-question", VALID.replace("戈壁藏蓝瞳", "海里有瀑布?").replace("（5字）", "（7字）"), False),
    ("missing-field", VALID.replace("- 落地页：解释盐泉颜色与地貌形成机制\n", ""), False),
    ("missing-timeline", VALID.replace("- 素材范围 / 目标上线日 / 去重窗口：常青；2026-08-30；2026-07-31–2026-08-30\n", ""), False),
    ("missing-certainty", VALID.replace("- 核心事实 / 确定性：盐泉因矿物与光线呈蓝色；已确认\n", ""), False),
    ("missing-visual-evidence", VALID.replace("- 首图证明 / 3种内页画面：蓝色盐泉俯拍；盐泉全景、矿物近景、地貌示意\n", ""), False),
    ("missing-hook-value", VALID.replace("- 主钩子 / 用户收益：视觉反常；地貌知识\n", ""), False),
    ("missing-source-meta", VALID.replace("- 来源等级 / 日期：专业机构；2026-08-20\n", ""), False),
    ("invalid-dedup-receipt", VALID.replace("H 通过；R 通过；B 通过", "H 通过；R 通过"), False),
    ("failed-dedup-status", VALID.replace("H 通过；R 通过；B 通过", "H 命中；R 覆盖不足；B 命中"), False),
    ("missing-dedup-window", VALID.replace("；窗口 2026-07-31–2026-08-30", ""), False),
    ("mismatched-dedup-window", VALID.replace("窗口 2026-07-31–2026-08-30", "窗口 2026-08-01–2026-08-30"), False),
    ("missing-r-coverage", VALID.replace("；R 数据覆盖 2026-07-01–2026-08-30；数据截止日 2026-08-30", ""), False),
    ("late-r-coverage", VALID.replace("R 数据覆盖 2026-07-01–2026-08-30", "R 数据覆盖 2026-08-01–2026-08-30"), False),
    ("empty-subtitle", VALID.replace("- 副标题：荒漠盐泉呈现天然蓝洞", "- 副标题："), False),
    ("bad-status", VALID.replace("- 状态：主推", "- 状态：已上线"), False),
    ("score-out-of-range", VALID.replace("P 潜力：8/10", "P 潜力：99/10"), False),
    ("placeholder-source", VALID.replace("https://www.cgs.gov.cn/salt-spring", "https://example.org/a"), False),
    ("placeholder-subdomain", VALID.replace("https://www.cgs.gov.cn/salt-spring", "https://fake.example.org/a"), False),
    ("placeholder-invalid-tld", VALID.replace("https://www.cgs.gov.cn/salt-spring", "https://source.invalid/a"), False),
    ("invalid-source-level", VALID.replace("来源等级 / 日期：专业机构", "来源等级 / 日期：自媒体"), False),
    ("missing-question-mark", VALID.replace("戈壁藏蓝瞳", "景区硬币去哪").replace("（5字）", "（6字）"), False),
    ("bad-main-threshold", VALID.replace("P 潜力：8/10", "P 潜力：6/10"), False),
    ("bad-main-quality-threshold", VALID.replace("质量总分：88/100", "质量总分：84/100"), False),
    ("usable-below-threshold", VALID.replace("- 状态：主推", "- 状态：可用").replace("质量总分：88/100", "质量总分：74/100"), False),
    ("quality-out-of-range", VALID.replace("质量总分：88/100", "质量总分：101/100"), False),
    ("unresolved-risk", VALID.replace("- 审核风险：无", "- 审核风险：版权未处理"), False),
    ("processed-risk", VALID.replace("- 审核风险：无", "- 审核风险：版权风险已处理"), True),
    ("duplicate-title-subtitle", VALID.replace("- 副标题：荒漠盐泉呈现天然蓝洞", "- 副标题：戈壁藏蓝瞳"), False),
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
