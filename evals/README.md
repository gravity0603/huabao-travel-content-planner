# 评测说明

`evals.json` 是行为回归定义，供支持 Skill eval 的外部评测流程或独立 Agent 审核使用；仓库不假设固定的评测框架。

确定性的终稿格式回归测试使用：

```powershell
python scripts/test_validate_candidate_output.py
```

行为评测重点检查素材库优先、三方概念去重、任务模式路由、来源状态、双目标评分、不得伪造已验证链接，以及月报复盘不自动修改知识库。
