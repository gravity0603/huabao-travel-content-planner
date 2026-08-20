# 华为画报旅行风光专项 Skill

`huabao-travel-content-planner` 用于华为杂志锁屏旅行风光内容的策划、审核和月报复盘。

## v0.5.0 核心能力

- 从**原始素材库最近新增链接**开始检索，不能跳过素材库。
- 强制比对素材库 CSV、已做标题表与近期已出选题；同一概念族不可第三次使用。
- 仅围绕自然异常、风光大片、有趣建筑组织旅行候选；历史冷知识仅作解释层。
- 先核验封面、图片来源、事实和版权，再写标题。
- 旅行标题 `≤7 字`、副标题 `≤25 字`；疑问句必须有中文问号。
- 基于 103 个旅行参考标题与 45 个旅行风光标题，沉淀“反常问句、画面翻译、规则/避坑、空间反差、故事钩子”五类标题打法；机制可借，历史标题不可照抄。
- 标题先通过对象锚点、画面证明、认知缺口、语言自然、事实兑现五项检查，再进入选题硬闸门。
- 每条信息源必须使用 `[来源名·文章标题](https://...)`；实际打开原文标 `[已验证]`，线索标 `[待验证]`。
- 使用 P 潜力和月报潜力两项独立评分；只有 `P≥7` 且 `月报≥8` 才标为“主推”。

## 目录

```text
.
├── SKILL.md                         # 触发条件、执行工作流与交付契约
├── agents/openai.yaml               # Codex UI 元数据
├── references/
│   ├── data-contract.md             # 输入顺序、去重与来源格式
│   ├── evidence-index.md            # 月报证据索引
│   ├── travel-strategy.md           # 旅行专项策略
│   └── title-playbook.md            # 标题样本分析与优化规范
├── evals/
│   ├── evals.json                   # 回归评测定义
│   └── fixtures/                    # 可移植、脱敏的评测素材
└── scripts/validate_candidate_output.py # 终稿格式硬校验
```

## 使用前准备

提供或确保可访问：

1. 原始素材库 CSV；
2. 已做标题表；
3. 近期已出选题；
4. 最新周数据与旅行月报；
5. 热点任务所需的新闻原文、图片来源或授权线索。

缺少前三项之一时，Skill 不得声称已完成概念级去重，也不得输出“主推”。

## 校验

```powershell
$env:PYTHONUTF8='1'
python C:\Users\zcy\.codex\skills\.system\skill-creator\scripts\quick_validate.py <skill目录>
python scripts/validate_candidate_output.py <候选输出.md>
```

详细工作流见 [SKILL.md](SKILL.md)，标题规范见 [references/title-playbook.md](references/title-playbook.md)，数据契约见 [references/data-contract.md](references/data-contract.md)，策略证据见 [references/evidence-index.md](references/evidence-index.md)。
