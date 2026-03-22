# labs/ — 实验与原型

探索性实验、原型验证、概念验证。成熟后迁移到正式工序。

## 目录结构

```
labs/
├── prototypes/              # 语义排版原型实验
├── source-inference/        # 溯源推理研究
├── contradiction-analysis/  # 矛盾分析
├── planning/                # 规划文档
├── reports/                 # 研究报告
├── sima-qian-style/         # 司马迁文风研究
└── hybrid-semantic-analysis/ # 混合语义分析实验 (进行中)
```

## 各模块说明

### [prototypes/](prototypes/)
语义排版与可视化交互原型实验，包含两个实验及其数据：
- 实验一：右侧批注 + 语义排版（基于五帝本纪）
- 实验二：句间关系排版（基于楚世家片段）

### [source-inference/](source-inference/)
史料溯源推理研究，分析太史公如何获知历史事件。

### [contradiction-analysis/](contradiction-analysis/)
《史记》不同篇章间的矛盾发现与分析。

### [planning/](planning/)
表格结构化、多Agent协作等规划文档。

### [reports/](reports/)
各项研究的总结报告与可视化数据。

### [sima-qian-style/](sima-qian-style/)
司马迁文风研究（进行中）。

### [hybrid-semantic-analysis/](hybrid-semantic-analysis/)
混合语义分析成本优化实验 ✅ **阶段性完成**

**实验目标**: 对比本地模型、混合方案、纯LLM三种语义标注方案的成本和效果。

**已完成测试**:
- ✅ **方案A1 (LTP依存文法)**: 召回率83.3%,精确率100%,耗时1.5秒,$0
  - 优势: 零成本,速度快,人名/地名识别完美
  - 局限: 无法识别官职类实体

- ❌ **方案A2 (Qwen2.5-7B)**: 实测失败 - 显存不足
  - 优势: 支持消歧,可识别复杂实体(官职/事件等)
  - 局限: 需要14GB显存(FP16),8GB显存环境OOM
  - 状态: 已下载模型(15GB),实际测试失败2次
  - 替代: 可尝试Qwen2.5-3B (6GB显存)

**待测试**:
- ⏳ 方案B (混合): 本地模型预标注 + LLM精炼
- ⏳ 方案C (纯Claude): 直接标注 (对照组)

**当前结论**:
- LTP可用于大规模粗筛 (零成本,1.6小时/52万字)
- Qwen需要更多显存或使用小模型
- 混合方案和Claude方案待测试

**详细报告**: [`results/experiment_summary.md`](hybrid-semantic-analysis/results/experiment_summary.md)
