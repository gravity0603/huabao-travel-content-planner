# 华为画报旅行风光专项 Skill

`huabao-travel-content-planner` 用于华为杂志锁屏旅行风光内容的策划、标题优化、候选审核和月报复盘。

## v0.9.0 核心能力

- 批量策划从原始素材库最近新增链接开始，完成 H（全历史）、R（目标日前至少30天上传）、B（本批/本会话）跨会话概念去重；R 覆盖不足即降级。
- 按任务模式加载资料：标题优化不强制读取去重数据，月报复盘不强制读取素材库。
- 用户指定时间范围覆盖默认热点时效；目标上线日和去重窗口独立记录。
- 使用反常问句、画面翻译、规则/避坑、空间反差、故事钩子五类标题打法，但不照抄案例；先审自然语感再验标题 `≤7 字`、副标题 `≤25 字`，不硬压缩。
- 新增“标题事件测试”：纯画面描述不再视为合格标题；根据对象灵活选择突变、反常事件、状态悬念、季节限定、身份/关系错位或玩法/视角收益。
- 日本元素一票否决；地点、人物、文化、品牌、作品、配图和核心素材来源任一命中即淘汰，不通过改称或隐藏来源规避。
- 信息源使用 `[已验证] [来源名·文章标题](https://...)`；搜索线索只能标 `[待验证]`。
- 原子候选卡显式记录对象、核心事实、来源等级/日期、确定性、首图证明、3种内页、主钩子与用户收益。
- 同一事实先比较陈述型、疑问型、隐喻/画面翻译型三种结构；无题眼返回“应换题”。
- 先过12项硬门槛，再做100分质量评分和 P/月报业务评分；主推须总分≥85、P≥7、月报≥8且 H/R/B 全通过。
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

`validate_candidate_output.py` 校验标题/副标题、品类、确定性、首图/内页、钩子/收益、来源等级/日期、占位域名、H/R/B 全通过、R覆盖起止、未处理风险、质量总分及 P/月报门槛；它仍不证明来源真实、版权安全或去重已实质完成。行为评测说明见 [evals/README.md](evals/README.md)。
