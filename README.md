# 华为画报旅行风光专项 Skill

`huabao-travel-content-planner` 用于华为杂志锁屏旅行风光内容的策划、标题优化、候选审核和月报复盘。

## v0.6.0 核心能力

- 批量策划从原始素材库最近新增链接开始，并完成素材库、已做标题、近期已出选题三方概念去重。
- 按任务模式加载资料：标题优化不强制读取去重数据，月报复盘不强制读取素材库。
- 旅行标题 `≤7 字`、副标题 `≤25 字`；疑问句必须使用中文问号。
- 使用反常问句、画面翻译、规则/避坑、空间反差、故事钩子五类标题打法，但不照抄案例。
- 信息源使用 `[已验证] [来源名·文章标题](https://...)`；搜索线索只能标 `[待验证]`。
- P 潜力与月报潜力独立评分；仅 `P≥7` 且 `月报≥8` 标“主推”。
- 最终输出不单列“视觉类型”或“图片来源与版权状态”；两者仅用于内部筛选。
- 月报复盘默认只给分析结论，只有用户明确要求时才更新知识库。

## 目录

```text
.
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── .gitignore
├── agents/openai.yaml
├── references/
│   ├── data-contract.md
│   ├── evidence-index.md
│   ├── travel-strategy.md
│   └── title-playbook.md
├── evals/
│   ├── README.md
│   ├── evals.json
│   └── fixtures/
└── scripts/
    ├── validate_candidate_output.py
    └── test_validate_candidate_output.py
```

## 使用前准备

- 批量策划和上线候选审核：原始素材库、已做标题表、近期已出选题；周数据和月报用于评分。
- 标题表达优化：事实或画面题眼、原标题即可；缺三方数据时不会声明完成去重或标主推。
- 月报/周数据复盘：对应报告或数据即可。

## 校验

```powershell
python "$env:CODEX_HOME\skills\.system\skill-creator\scripts\quick_validate.py" <skill目录>
python scripts/test_validate_candidate_output.py
python scripts/validate_candidate_output.py <候选输出.md>
```

`validate_candidate_output.py` 只校验可机械检查的最终格式，不证明来源真实、版权安全或去重已经实质完成。行为评测说明见 [evals/README.md](evals/README.md)。
